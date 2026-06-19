import logging
from typing import TypedDict, Optional

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from ai_agents.tools import build_tenant_tools

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = (
    'Você é o assistente da corretora "{trade_name}". Responda SEMPRE em português, '
    'em Markdown. Use as ferramentas disponíveis para consultar dados reais da '
    'corretora. NUNCA invente dados. Você só tem acesso aos dados desta corretora. '
    'Se a informação não existir, diga que não encontrou. '
    'Data de hoje: {today}. Papel do usuário: {role}.'
)

SUMMARY_PROMPT_TEMPLATE = (
    'Com base nos dados abaixo, gere um resumo executivo em Markdown para a entidade '
    'do tipo "{entity_type}" chamada "{entity_name}". '
    'Inclua: 1) Resumo principal 2) Pontos de atenção 3) Recomendações. '
    'Seja conciso e objetivo.\n\n'
    'Dados da entidade:\n{entity_data}\n\n'
    'Dados relacionados (cabos da corretora):\n{related_data}'
)


class SummaryState(TypedDict):
    entity_id: int
    entity_type: str
    entity_name: str
    entity_data: str
    related_data: str
    summary: str
    error: Optional[str]


def _load_entity(state: SummaryState, entity_type: str, entity_id: int, brokerage) -> dict:
    models_map = {
        'client': ('clients.models', 'Client'),
        'policy': ('insurance.models', 'Policy'),
        'proposal': ('insurance.models', 'Proposal'),
        'claim': ('claims.models', 'Claim'),
        'deal': ('crm.models', 'Deal'),
    }
    if entity_type not in models_map:
        return {'error': f'Tipo de entidade desconhecido: {entity_type}'}

    import importlib
    module_path, model_name = models_map[entity_type]
    module = importlib.import_module(module_path)
    Model = getattr(module, model_name)

    obj = Model.objects.filter(brokerage=brokerage, pk=entity_id).first()
    if not obj:
        return {'error': f'{entity_type} #{entity_id} não encontrado no tenant.'}

    import json
    fields = [f.name for f in obj._meta.get_fields() if f.name not in ('brokerage',)]
    data = {}
    for f in fields:
        try:
            val = getattr(obj, f)
            if callable(val):
                continue
            if hasattr(val, 'isoformat'):
                val = val.isoformat()
            elif isinstance(val, (int, float, bool, str)):
                pass
            else:
                val = str(val)
            data[f] = val
        except Exception:
            continue

    return {
        'entity_id': entity_id,
        'entity_type': entity_type,
        'entity_name': getattr(obj, 'name', getattr(obj, 'policy_number', getattr(obj, 'title', getattr(obj, 'claim_number', str(obj.pk))))),
        'entity_data': json.dumps(data, ensure_ascii=False, default=str),
    }


def _fetch_related(state: SummaryState, brokerage) -> str:
    tools = build_tenant_tools(brokerage)
    related_parts = []
    entity_type = state.get('entity_type', '')

    if entity_type == 'client':
        for t in tools:
            if t.name == 'list_clients':
                related_parts.append(t.invoke({'query': state.get('entity_name', '')}))
                break
    elif entity_type in ('policy', 'proposal', 'claim'):
        for t in tools:
            if t.name == 'list_policies':
                related_parts.append(t.invoke({}))
                break
        for t in tools:
            if t.name == 'list_claims':
                related_parts.append(t.invoke({}))
                break
    elif entity_type == 'deal':
        for t in tools:
            if t.name == 'list_clients':
                related_parts.append(t.invoke({}))
                break

    return '\n\n'.join(related_parts) if related_parts else 'Sem dados relacionados disponíveis.'


def create_summary_graph():
    llm = ChatOpenAI(
        model='gpt-4o-mini',
        temperature=0.3,
    )

    def load_node(state: SummaryState) -> dict:
        return state

    def fetch_node(state: SummaryState) -> dict:
        return state

    def prompt_node(state: SummaryState) -> dict:
        return state

    def generate_node(state: SummaryState) -> dict:
        prompt = SUMMARY_PROMPT_TEMPLATE.format(
            entity_type=state.get('entity_type', ''),
            entity_name=state.get('entity_name', ''),
            entity_data=state.get('entity_data', ''),
            related_data=state.get('related_data', ''),
        )
        try:
            response = llm.invoke(prompt)
            return {'summary': response.content}
        except Exception as e:
            logger.exception('Erro ao gerar resumo IA')
            return {'error': str(e)}

    graph = StateGraph(SummaryState)
    graph.add_node('load', load_node)
    graph.add_node('fetch', fetch_node)
    graph.add_node('prompt', prompt_node)
    graph.add_node('generate', generate_node)

    graph.set_entry_point('load')
    graph.add_edge('load', 'fetch')
    graph.add_edge('fetch', 'prompt')
    graph.add_edge('prompt', 'generate')
    graph.add_edge('generate', END)

    return graph.compile()


def run_summary_agent(entity_type: str, entity_id: int, brokerage) -> str:
    entity_data = _load_entity({}, entity_type, entity_id, brokerage)
    if entity_data.get('error'):
        raise ValueError(entity_data['error'])

    state = SummaryState(
        entity_id=entity_id,
        entity_type=entity_type,
        entity_name=entity_data.get('entity_name', ''),
        entity_data=entity_data.get('entity_data', ''),
        related_data='',
        summary='',
        error=None,
    )

    state['related_data'] = _fetch_related(state, brokerage)

    prompt = SUMMARY_PROMPT_TEMPLATE.format(
        entity_type=state['entity_type'],
        entity_name=state['entity_name'],
        entity_data=state['entity_data'],
        related_data=state['related_data'],
    )

    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.3)
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        logger.exception('Erro ao gerar resumo IA')
        raise


def run_chat_agent_stream(brokerage, user_role, messages, trade_name='Corretora'):
    from datetime import date

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        trade_name=trade_name,
        today=date.today().isoformat(),
        role=user_role,
    )

    tools = build_tenant_tools(brokerage)
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.3, streaming=True).bind_tools(tools)

    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    lc_messages = [SystemMessage(content=system_prompt)]
    for role, content in messages:
        if role == 'user':
            lc_messages.append(HumanMessage(content=content))
        elif role == 'assistant':
            lc_messages.append(AIMessage(content=content))

    tool_names = {t.name for t in tools}

    for chunk in llm.stream(lc_messages):
        if chunk.content:
            yield chunk.content
        if chunk.tool_calls:
            for tc in chunk.tool_calls:
                tool_name = tc.get('name', tc.get('function', {}).get('name', ''))
                if tool_name in tool_names:
                    for t in tools:
                        if t.name == tool_name:
                            args = tc.get('args', tc.get('function', {}).get('arguments', {}))
                            if isinstance(args, str):
                                import json
                                try:
                                    args = json.loads(args)
                                except (json.JSONDecodeError, TypeError):
                                    args = {}
                            result = t.invoke(args)
                            lc_messages.append(AIMessage(content='', tool_calls=[tc]))
                            from langchain_core.messages import ToolMessage
                            lc_messages.append(ToolMessage(content=str(result), tool_call_id=tc.get('id', '')))
                            for inner_chunk in llm.stream(lc_messages):
                                if inner_chunk.content:
                                    yield inner_chunk.content
                            break