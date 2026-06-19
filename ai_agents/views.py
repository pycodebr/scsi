import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from base.mixins import RoleRequiredMixin, TenantQuerysetMixin
from .models import ChatSession, ChatMessage
from .agents import run_chat_agent_stream

logger = logging.getLogger(__name__)

ENTITY_MODEL_MAP = {
    'client': ('clients.models', 'Client'),
    'policy': ('insurance.models', 'Policy'),
    'proposal': ('insurance.models', 'Proposal'),
    'claim': ('claims.models', 'Claim'),
    'deal': ('crm.models', 'Deal'),
}


def _get_model(entity_type):
    import importlib
    module_path, model_name = ENTITY_MODEL_MAP[entity_type]
    module = importlib.import_module(module_path)
    return getattr(module, model_name)


# ── Summary Views ──────────────────────────────────────────────────────────

@method_decorator(csrf_exempt, name='dispatch')
class GenerateSummaryView(RoleRequiredMixin, View):
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer')

    def post(self, request, entity_type, pk):
        if entity_type not in ENTITY_MODEL_MAP:
            return JsonResponse({'error': 'Tipo de entidade inválido.'}, status=400)

        Model = _get_model(entity_type)
        obj = Model.objects.filter(brokerage=request.tenant, pk=pk).first()
        if not obj:
            return JsonResponse({'error': 'Entidade não encontrada.'}, status=404)

        if obj.ai_summary_status == 'processing':
            return JsonResponse({'status': 'processing', 'message': 'Resumo já está sendo gerado.'}, status=202)

        Model.objects.filter(pk=pk, brokerage=request.tenant).update(ai_summary_status='processing')

        task_map = {
            'client': 'ai_agents.tasks.generate_client_summary',
            'policy': 'ai_agents.tasks.generate_policy_summary',
            'proposal': 'ai_agents.tasks.generate_proposal_summary',
            'claim': 'ai_agents.tasks.generate_claim_summary',
            'deal': 'ai_agents.tasks.generate_deal_summary',
        }

        import importlib
        module_path, func_name = task_map[entity_type].rsplit('.', 1)
        module = importlib.import_module(module_path)
        task_func = getattr(module, func_name)
        task_func.delay(pk)

        return JsonResponse({'status': 'processing', 'message': 'Gerando resumo. Você será notificado ao concluir.'}, status=202)


class SummaryStatusView(LoginRequiredMixin, View):
    def get(self, request, entity_type, pk):
        if entity_type not in ENTITY_MODEL_MAP:
            return JsonResponse({'error': 'Tipo de entidade inválido.'}, status=400)

        Model = _get_model(entity_type)
        obj = Model.objects.filter(brokerage=request.tenant, pk=pk).values('ai_summary_status', 'ai_summary', 'ai_summary_updated_at').first()
        if not obj:
            return JsonResponse({'error': 'Entidade não encontrada.'}, status=404)

        return JsonResponse({
            'status': obj['ai_summary_status'],
            'summary': obj['ai_summary'],
            'updated_at': obj['ai_summary_updated_at'].isoformat() if obj['ai_summary_updated_at'] else None,
        })


# ── Chat Views ─────────────────────────────────────────────────────────────

class ChatSessionListView(RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')
    model = ChatSession
    template_name = 'ai_agents/chat.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        return ChatSession.objects.filter(
            brokerage=self.request.tenant,
            user=self.request.user,
        ).order_by('-updated_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        active_session = None
        pk = self.kwargs.get('pk')
        if pk:
            active_session = get_object_or_404(
                ChatSession, pk=pk, brokerage=self.request.tenant, user=self.request.user
            )
        elif ctx['sessions'].exists():
            active_session = ctx['sessions'].first()
        ctx['active_session'] = active_session
        if active_session:
            ctx['chat_messages'] = ChatMessage.objects.filter(session=active_session).order_by('created_at')
        else:
            ctx['chat_messages'] = ChatMessage.objects.none()
        return ctx


class ChatSessionCreateView(RoleRequiredMixin, View):
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')

    def post(self, request):
        session = ChatSession.objects.create(
            brokerage=request.tenant,
            user=request.user,
            title=request.POST.get('title', 'Nova conversa'),
        )
        return JsonResponse({
            'id': session.pk,
            'title': session.title,
            'url': session.get_absolute_url(),
        })


class ChatSessionRenameView(RoleRequiredMixin, View):
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')

    def post(self, request, pk):
        session = get_object_or_404(
            ChatSession, pk=pk, brokerage=request.tenant, user=request.user
        )
        title = request.POST.get('title', '').strip()
        if title:
            session.title = title
            session.save(update_fields=['title', 'updated_at'])
        return JsonResponse({'ok': True, 'title': session.title})


class ChatSessionDeleteView(RoleRequiredMixin, View):
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')

    def post(self, request, pk):
        session = get_object_or_404(
            ChatSession, pk=pk, brokerage=request.tenant, user=request.user
        )
        session.delete()
        return JsonResponse({'ok': True})


class ChatSessionExportView(RoleRequiredMixin, View):
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')

    def get(self, request, pk):
        session = get_object_or_404(
            ChatSession, pk=pk, brokerage=request.tenant, user=request.user
        )
        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        lines = [
            f'# {session.title}',
            f'',
            f'> Exportado em {timezone.now().strftime("%d/%m/%Y %H:%M")}',
            f'',
            f'---',
            f'',
        ]
        role_label = {'user': '**Você**', 'assistant': '**Assistente**', 'system': '**Sistema**'}
        for msg in messages:
            label = role_label.get(msg.role, msg.role)
            lines.append(f'{label}:')
            lines.append(f'')
            lines.append(msg.content)
            lines.append(f'')
            lines.append(f'---')
            lines.append(f'')
        filename = f'chat-{session.pk}-{session.title[:30].replace(" ", "-")}.md'
        response = HttpResponse('\n'.join(lines), content_type='text/markdown; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class ChatMessageSendView(RoleRequiredMixin, View):
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')

    def post(self, request, pk):
        session = get_object_or_404(
            ChatSession, pk=pk, brokerage=request.tenant, user=request.user
        )
        body = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        user_message = body.get('message', '').strip()
        if not user_message:
            return JsonResponse({'error': 'Mensagem vazia.'}, status=400)

        ChatMessage.objects.create(session=session, role=ChatMessage.Role.USER, content=user_message)

        history = ChatMessage.objects.filter(session=session).order_by('created_at')
        history_data = [(m.role, m.content) for m in history]

        def event_stream():
            full_response = ''
            try:
                for chunk in run_chat_agent_stream(
                    brokerage=request.tenant,
                    user_role=request.user.role,
                    messages=history_data,
                    trade_name=request.tenant.trade_name,
                ):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
                ChatMessage.objects.create(
                    session=session,
                    role=ChatMessage.Role.ASSISTANT,
                    content=full_response,
                )
                yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
            except Exception as e:
                logger.exception('Erro no streaming do chat')
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response