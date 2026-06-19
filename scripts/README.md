# Scripts de Setup — PycodeBR

Scripts que preparam **do zero** a máquina do aluno para desenvolver com o workflow de
IA Assistida (stack Python 3.13 + Django + Docker + CLIs de IA). São **genéricos**:
servem para o projeto SCSI e para qualquer outro projeto novo com a mesma stack.

Todos os scripts são **idempotentes** (pulam o que já está instalado), têm **logs visuais**
em cada etapa e **tratamento de erro** com motivo, linha e log completo.

| Objetivo                | Script             | Onde roda | Como rodar |
|-------------------------|--------------------|-----------|------------|
| **Máquina local** (Linux/macOS) | `setup_local.sh`  | Seu PC    | `curl -fsSL https://pycodebr.com.br/setup_local.sh -o setup_local.sh && bash setup_local.sh` |
| **Máquina local** (Windows)     | `setup_local.ps1` | Seu PC    | `irm https://pycodebr.com.br/setup_local.ps1 \| iex` (PowerShell **Admin**) |
| **VPS + Deploy completo**       | `setup_deploy.sh` | Servidor  | `curl -fsSL https://pycodebr.com.br/setup_deploy.sh -o setup_deploy.sh && sudo bash setup_deploy.sh` (como **root**) |

O que cada script instala (se faltar): Python 3.13 + venv, Node.js + npm/npx,
Docker + Compose, **Claude Code**, **OpenCode** e **Codex CLI**, git/curl e o
**GitHub CLI (`gh`)** — e já **autentica você no GitHub**. Ele tenta primeiro o fluxo
padrão do `gh` (login pelo navegador); **se isso falhar**, cai num **fallback guiado por
token**: o script te leva passo a passo até `github.com/settings/tokens/new` (com os escopos
`repo` e `workflow` já marcados), você cola o código `ghp_...` e ele autentica — o token é
lido sem aparecer na tela. Assim funciona até em máquinas sem navegador. Depois ele
**pergunta onde** criar o projeto e **qual o nome**, cria a pasta, monta a `.venv`,
instala o Django, roda `django-admin startproject core .`, gera o `requirements.txt`,
cria o `.gitignore` (mesmo padrão do projeto SCSI) e um `.env` modelo com as variáveis
mais usadas (em branco). Por fim, **pergunta se você quer enviar o projeto para o
GitHub**: se sim, pergunta o **nome do repositório** (sugere o nome da pasta) e se ele
deve ser **público ou privado**, cria o repositório com o `gh` e faz o **`first commit`**.

---

## Linux / macOS

**Comando único** (recomendado — baixa e executa):

```bash
curl -fsSL https://pycodebr.com.br/setup_local.sh -o setup_local.sh && bash setup_local.sh
```

> O script é **interativo** (pergunta a pasta e o nome do projeto). Ele redireciona
> a entrada do teclado a partir do `/dev/tty`, então até o formato
> `curl -fsSL https://pycodebr.com.br/setup_local.sh | bash` funciona — mas o
> comando recomendado acima (baixar e rodar) é o mais previsível.

- **macOS**: instala o Homebrew se necessário e o Docker Desktop (abra o app uma vez no fim).
- **Linux**: usa o gerenciador nativo (apt/dnf/pacman/zypper) e o instalador oficial da Docker.
  Você é adicionado ao grupo `docker` — faça **logout/login** uma vez para usar sem `sudo`.

Log da execução: `./setup_local.log`.

---

## Windows — e a questão do Docker/WSL

**Sim, o Docker no Windows precisa do WSL2.** O Docker Desktop é a forma oficial e mais
simples de ter Docker no Windows, e ele roda o motor (engine) dentro do **WSL2**
(Windows Subsystem for Linux). Não há Docker nativo "puro" no Windows para containers Linux —
sempre há uma camada Linux por baixo (WSL2 é a recomendada; Hyper-V é o caminho antigo).

Por isso o `setup_local.ps1` **habilita o WSL2 automaticamente** antes de instalar o Docker.

### Opção A (recomendada) — Setup nativo no Windows + Docker Desktop

Tudo roda no Windows; o Docker usa o WSL2 só por baixo dos panos. É o caminho mais simples
para a maioria dos alunos.

1. Menu Iniciar → digite **PowerShell** → botão direito → **Executar como administrador**.
2. **Comando único** (recomendado — baixa e executa em memória):
   ```powershell
   irm https://pycodebr.com.br/setup_local.ps1 | iex
   ```
   O `irm` (Invoke-RestMethod) baixa o script e o `iex` (Invoke-Expression) o executa.
   Como roda em memória, **não precisa** mexer no `Set-ExecutionPolicy`, e as
   perguntas funcionam normalmente.

   Se preferir baixar o arquivo antes:
   ```powershell
   irm https://pycodebr.com.br/setup_local.ps1 -OutFile setup_local.ps1
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
   .\setup_local.ps1
   ```
4. Se ele habilitar o WSL2, **reinicie o Windows** e rode o script de novo
   (ele é idempotente e continua de onde parou).
5. No fim, abra o **Docker Desktop** uma vez para concluir a configuração.

Log da execução: `.\setup_local.log`.

### Opção B (alternativa "tudo Linux") — Desenvolver dentro do WSL2/Ubuntu

Para quem prefere um ambiente Linux limpo (mesmos comandos do Linux/macOS):

1. No PowerShell **como Administrador**:
   ```powershell
   wsl --install -d Ubuntu
   ```
   Reinicie o Windows e crie usuário/senha do Ubuntu quando pedir.
2. Instale o **Docker Desktop** (ele se integra ao WSL2 — em *Settings → Resources → WSL
   Integration*, ative o Ubuntu). Alternativamente, instale o Docker Engine direto dentro do Ubuntu.
3. Abra o **Ubuntu** (menu Iniciar) e rode o script de Linux normalmente:
   ```bash
   curl -fsSL https://pycodebr.com.br/setup_local.sh -o setup_local.sh && bash setup_local.sh
   ```

> Dica: trabalhe com os arquivos **dentro** do filesystem do WSL (ex.: `~/projects`),
> não em `/mnt/c/...`, para ter performance bem melhor.

### Qual escolher?

- **Iniciante / só quer que funcione** → **Opção A**.
- **Quer ambiente Linux idêntico ao de produção / já curte terminal** → **Opção B**.

Ambas terminam com Python, Node, Docker e os CLIs de IA prontos.

---

## VPS — deploy completo do zero (`setup_deploy.sh`)

Faz **todo** o deploy de produção (Docker Swarm + Traefik + GHCR), genérico para
qualquer projeto com a stack/estrutura do SCSI. Pensado para rodar **uma vez** e
levar o sistema do zero até o ar.

### Como rodar

1. Acesse a VPS **como root** (ex.: `ssh root@SEU_IP`).
2. Rode o **comando único** (recomendado — baixa e executa):
   ```bash
   curl -fsSL https://pycodebr.com.br/setup_deploy.sh -o setup_deploy.sh && sudo bash setup_deploy.sh
   ```
   Alternativa em uma linha só, sem salvar arquivo:
   ```bash
   sudo bash -c "$(curl -fsSL https://pycodebr.com.br/setup_deploy.sh)"
   ```

> **Sobre `curl ... | bash`:** este script é **interativo** e troca de usuário no
> meio (root → `deploy`). Para isso funcionar mesmo via pipe, ele (a) redireciona o
> teclado a partir do `/dev/tty` e (b) quando roda sem arquivo em disco, se
> **rebaixa** sozinho de `SETUP_DEPLOY_URL` (variável que aponta para a URL pública
> do script) para continuar como `deploy`. Ainda assim, o comando recomendado
> (baixar e rodar) é o mais previsível e o que deixa o log/arquivo na máquina.

### Como funciona (arquitetura em 2 fases)

O script é **uma execução só**, iniciada como root, dividida em duas fases:

- **FASE 1 — Sistema (root):** `apt update/upgrade`, utilitários, timezone,
  fail2ban, swap, firewall (UFW: 22/80/443), tuning de produção (sysctl/limits),
  Docker + `daemon.json`, Swarm + labels de nó, e **cria o usuário `deploy`**
  (sudo + grupo docker, com as chaves SSH copiadas do root).
- **FASE 2 — Deploy (usuário `deploy`):** o script **se re-executa sozinho como
  `deploy`** e conduz: chave SSH do GitHub (mostra a chave e **pausa** para você
  colar no GitHub), `~/.ssh/config`, clone do repositório (SSH e, se falhar,
  HTTPS), login no **GHCR** (token classic), **`.env`** (abre um editor para você
  **colar o `.env` do projeto** — com fallback de "colar e finalizar"), criação
  **manual** das redes (`traefik_public`, `<stack>_internal` isolada, `<stack>_egress`),
  **build/push/pull**, **Basic Auth do Traefik** (htpasswd, com `$` escapado para
  o Swarm), **secret da Cloudflare**, `docker stack deploy`, verificação e **`seed_demo --force`**.

> **Regra de ouro:** o deploy roda **sempre** sob o usuário `deploy` — mesmo você
> iniciando como root. Isso é garantido pelo handoff automático entre as fases.
> Se preferir o fluxo manual (criar o `deploy` à mão e rodar a fase de deploy),
> basta rodar o mesmo script já logado como `deploy` — ele pula a FASE 1.

### O que o script vai te pedir (tenha em mãos)

- Nome do projeto (igual ao repositório no GitHub), timezone, tamanho do swap.
- **Chave SSH** gerada na hora → você cola no GitHub e dá ENTER.
- URL do repositório (SSH; cai para HTTPS se falhar).
- **Token classic do GitHub** (escopos `read:packages`, `write:packages`, `delete:packages`).
- O **conteúdo do `.env`** do projeto (você cola num editor que ele abre).
- **Token da Cloudflare** (template *Edit zone DNS*).
- Senha do dashboard do Traefik (ou deixa ele gerar).

### Depois do deploy

O próprio script imprime os comandos no final. Para novos deploys após alterar o
código, dentro da pasta do projeto na VPS:
```bash
git pull && ./scripts/deploy.sh          # build + push + deploy
./scripts/deploy.sh --skip-build         # só redeploy da stack
```

---

## Resolução de problemas

- **Erro no meio da execução**: leia o "Motivo" na caixa vermelha e o log
  (`setup_local.log`). Rode o script de novo — ele retoma do ponto seguro.
- **`docker` pede sudo no Linux**: faça logout/login (ou rode `newgrp docker`).
- **Comando `claude`/`opencode`/`codex` não encontrado após instalar**: feche e reabra o
  terminal (PATH do npm global) e tente de novo.
- **Windows: `winget` não encontrado**: instale o *App Installer* pela Microsoft Store.
- **Windows: script não executa**: rode o `Set-ExecutionPolicy ... Bypass` da Opção A.
