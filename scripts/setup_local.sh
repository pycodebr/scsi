#!/usr/bin/env bash
# =============================================================================
#  setup_local.sh  —  Setup de ambiente de desenvolvimento (Linux e macOS)
# =============================================================================
#  PycodeBR — workflow de IA Assistida (SCSI e qualquer outro projeto)
#
#  O QUE ESTE SCRIPT FAZ (de forma idempotente — pula o que já está instalado):
#    1. Detecta seu sistema operacional e gerenciador de pacotes
#    2. Instala Python 3.13 + venv               (se faltar)
#    3. Instala Node.js + npm/npx                 (se faltar)
#    4. Instala Docker + Docker Compose           (se faltar)
#    5. Instala os CLIs de IA:
#         - Claude Code  (@anthropic-ai/claude-code)
#         - OpenCode     (opencode-ai)
#         - Codex CLI    (@openai/codex)
#    6. Instala ferramentas de apoio (git, curl, etc.)
#    7. Instala o GitHub CLI (gh) e autentica você no GitHub
#       (fluxo padrão; se falhar, fallback guiado por token)
#    8. Cria a pasta do SEU projeto (pergunta onde e qual nome)
#    9. Cria a .venv, instala Django, roda `django-admin startproject core .`,
#       gera o requirements.txt e o .gitignore
#   10. Cria um arquivo .env com as variáveis mais usadas (em branco)
#   11. (Opcional) Cria o repositório no GitHub e faz o "first commit" (gh)
#
#  USO:
#    bash scripts/setup_local.sh
#    # ou torne executável:  chmod +x scripts/setup_local.sh && ./scripts/setup_local.sh
#
#  Em caso de erro, o script mostra o motivo, a linha e o comando que falhou,
#  e grava um log completo em:  ./setup_local.log
# =============================================================================

set -Eeuo pipefail

# Se a entrada padrão NÃO for um terminal (ex.: rodando via 'curl ... | bash'),
# redireciona a entrada para o terminal real — assim as perguntas funcionam
# mesmo quando o script chega pelo "cano" do curl.
if [[ ! -t 0 && -e /dev/tty ]]; then exec </dev/tty; fi

# ─────────────────────────────────────────────────────────────────────────────
#  Constantes / Configuração
# ─────────────────────────────────────────────────────────────────────────────
readonly PYTHON_TARGET="3.13"            # versão alvo do Python
readonly SCRIPT_NAME="$(basename "$0")"
readonly LOG_FILE="$(pwd)/setup_local.log"
TOTAL_STEPS=11
CURRENT_STEP=0

# ─────────────────────────────────────────────────────────────────────────────
#  Cores e símbolos (com fallback se o terminal não suportar)
# ─────────────────────────────────────────────────────────────────────────────
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1 && [[ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]]; then
  BOLD="$(tput bold)";   RESET="$(tput sgr0)"
  RED="$(tput setaf 1)"; GREEN="$(tput setaf 2)"; YELLOW="$(tput setaf 3)"
  BLUE="$(tput setaf 4)"; CYAN="$(tput setaf 6)"; GREY="$(tput setaf 8)"
else
  BOLD=""; RESET=""; RED=""; GREEN=""; YELLOW=""; BLUE=""; CYAN=""; GREY=""
fi

# ─────────────────────────────────────────────────────────────────────────────
#  Logging visual e didático
# ─────────────────────────────────────────────────────────────────────────────
# Tudo também é gravado (sem cores) no LOG_FILE para diagnóstico.
_logfile() { printf '%s %s\n' "[$(date '+%H:%M:%S')]" "$1" >>"$LOG_FILE"; }

banner() {
  echo ""
  echo "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${RESET}"
  printf "${BOLD}${CYAN}║${RESET} %-60s ${BOLD}${CYAN}║${RESET}\n" "$1"
  echo "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${RESET}"
}

step() {
  CURRENT_STEP=$((CURRENT_STEP + 1))
  echo ""
  echo "${BOLD}${BLUE}▶ ETAPA ${CURRENT_STEP}/${TOTAL_STEPS}:${RESET} ${BOLD}$1${RESET}"
  echo "${GREY}──────────────────────────────────────────────────────────────${RESET}"
  _logfile "ETAPA ${CURRENT_STEP}/${TOTAL_STEPS}: $1"
}

info()    { echo "  ${BLUE}ℹ${RESET}  $1";        _logfile "INFO  $1"; }
ok()      { echo "  ${GREEN}✔${RESET}  $1";        _logfile "OK    $1"; }
warn()    { echo "  ${YELLOW}⚠${RESET}  $1";        _logfile "WARN  $1"; }
skip()    { echo "  ${GREEN}✓${RESET}  ${GREY}$1 (já instalado — pulando)${RESET}"; _logfile "SKIP  $1"; }
working() { echo "  ${CYAN}⏳${RESET} $1...";       _logfile "WORK  $1"; }

# ─────────────────────────────────────────────────────────────────────────────
#  Tratamento de erros — mostra motivo, linha, comando e onde parou
# ─────────────────────────────────────────────────────────────────────────────
on_error() {
  local exit_code=$1 line=$2 cmd=$3
  echo ""
  echo "${BOLD}${RED}╔══════════════════════════════════════════════════════════════╗${RESET}"
  echo "${BOLD}${RED}║  ❌ ERRO — o script parou                                     ║${RESET}"
  echo "${BOLD}${RED}╚══════════════════════════════════════════════════════════════╝${RESET}"
  echo "  ${RED}Etapa........:${RESET} ${CURRENT_STEP}/${TOTAL_STEPS}"
  echo "  ${RED}Linha........:${RESET} ${line}"
  echo "  ${RED}Comando......:${RESET} ${cmd}"
  echo "  ${RED}Código saída.:${RESET} ${exit_code}"
  echo ""
  echo "  ${YELLOW}O que fazer:${RESET}"
  echo "    1. Leia a mensagem de erro logo acima desta caixa."
  echo "    2. O log completo está em: ${BOLD}${LOG_FILE}${RESET}"
  echo "    3. Rode o script de novo — ele é idempotente e retoma de onde dá."
  echo "    4. Se persistir, copie o log e peça ajuda ao seu CLI de IA."
  echo ""
  _logfile "ERRO exit=$exit_code line=$line cmd=<$cmd> step=$CURRENT_STEP/$TOTAL_STEPS"
  # Pausa para o usuário ler o erro (não trava se não houver terminal).
  if [[ -e /dev/tty ]]; then
    read -r -p "  Pressione ENTER para fechar..." _ </dev/tty 2>/dev/null || true
  fi
  exit "$exit_code"
}
trap 'on_error $? ${LINENO} "$BASH_COMMAND"' ERR

# ─────────────────────────────────────────────────────────────────────────────
#  Utilitários
# ─────────────────────────────────────────────────────────────────────────────
have() { command -v "$1" >/dev/null 2>&1; }

# Retenta um comando até 3x com backoff (útil para downloads/instalações de rede)
retry() {
  local max=3 attempt=1 delay=3
  until "$@"; do
    if (( attempt >= max )); then
      warn "Falhou após ${max} tentativas: $*"
      return 1
    fi
    warn "Tentativa ${attempt}/${max} falhou. Nova tentativa em ${delay}s..."
    sleep "$delay"
    attempt=$((attempt + 1)); delay=$((delay * 2))
  done
}

# Pergunta sim/não exigindo S ou N explícito
confirm_SN() {
  local prompt="$1" answer
  while true; do
    read -r -p "  ${YELLOW}❓ ${prompt} [S/N]:${RESET} " answer || true
    case "$answer" in
      [Ss]|[Ss][Ii][Mm]) return 0 ;;
      [Nn]|[Nn][Aa][Oo]) return 1 ;;
      *) warn "Responda com S (sim) ou N (não)." ;;
    esac
  done
}

# ─────────────────────────────────────────────────────────────────────────────
#  Detecção de SO e gerenciador de pacotes
# ─────────────────────────────────────────────────────────────────────────────
OS=""           # macos | linux
DISTRO=""       # debian | fedora | arch | ...
PKG=""          # brew | apt | dnf | pacman | zypper
SUDO=""         # "" ou "sudo"

detect_os() {
  case "$(uname -s)" in
    Darwin) OS="macos" ;;
    Linux)  OS="linux" ;;
    *) echo "SO não suportado: $(uname -s). Use Linux ou macOS (no Windows use setup_local.ps1)."; exit 1 ;;
  esac

  if [[ "$OS" == "macos" ]]; then
    PKG="brew"
  else
    if [[ -r /etc/os-release ]]; then
      # shellcheck disable=SC1091
      . /etc/os-release
      DISTRO="${ID:-}${ID_LIKE:+ $ID_LIKE}"
    fi
    if   have apt-get; then PKG="apt"
    elif have dnf;     then PKG="dnf"
    elif have pacman;  then PKG="pacman"
    elif have zypper;  then PKG="zypper"
    else
      echo "Não encontrei um gerenciador de pacotes suportado (apt/dnf/pacman/zypper)."
      exit 1
    fi
    # Define SUDO se não formos root
    if [[ "$(id -u)" -ne 0 ]]; then
      have sudo || { echo "Preciso de 'sudo' para instalar pacotes no Linux."; exit 1; }
      SUDO="sudo"
    fi
  fi

  info "Sistema......: ${BOLD}${OS}${RESET}${DISTRO:+ (${DISTRO})}"
  info "Gerenciador..: ${BOLD}${PKG}${RESET}"
}

# Atualiza índice de pacotes (apenas 1x por execução, quando aplicável)
PKG_UPDATED=0
pkg_update_once() {
  [[ "$PKG_UPDATED" -eq 1 ]] && return 0
  case "$PKG" in
    apt)    working "Atualizando índice de pacotes (apt update)"; retry $SUDO apt-get update -y >>"$LOG_FILE" 2>&1 ;;
    dnf)    : ;;  # dnf resolve metadados automaticamente
    pacman) working "Sincronizando pacotes (pacman -Sy)"; retry $SUDO pacman -Sy --noconfirm >>"$LOG_FILE" 2>&1 ;;
    zypper) working "Atualizando repositórios (zypper refresh)"; retry $SUDO zypper --non-interactive refresh >>"$LOG_FILE" 2>&1 ;;
  esac
  PKG_UPDATED=1
}

# Instala um pacote pelo gerenciador nativo
pkg_install() {
  local pkg="$1"
  pkg_update_once
  case "$PKG" in
    brew)   retry brew install "$pkg" >>"$LOG_FILE" 2>&1 ;;
    apt)    retry $SUDO apt-get install -y "$pkg" >>"$LOG_FILE" 2>&1 ;;
    dnf)    retry $SUDO dnf install -y "$pkg" >>"$LOG_FILE" 2>&1 ;;
    pacman) retry $SUDO pacman -S --noconfirm "$pkg" >>"$LOG_FILE" 2>&1 ;;
    zypper) retry $SUDO zypper --non-interactive install -y "$pkg" >>"$LOG_FILE" 2>&1 ;;
  esac
}

# =============================================================================
#  ETAPA 0 — Boas-vindas + pré-requisitos
# =============================================================================
: >"$LOG_FILE"   # zera o log desta execução
banner "🚀  SETUP DE AMBIENTE — PycodeBR"
echo "  Este script prepara tudo que você precisa para desenvolver."
echo "  Ele é ${BOLD}seguro${RESET} e ${BOLD}idempotente${RESET}: pode rodar quantas vezes quiser."
echo "  Log completo desta execução: ${GREY}${LOG_FILE}${RESET}"

step "Detectando seu sistema e ferramentas base"
detect_os

# Homebrew é pré-requisito no macOS
if [[ "$OS" == "macos" ]] && ! have brew; then
  working "Instalando Homebrew (gerenciador de pacotes do macOS)"
  retry /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Carrega o brew no PATH desta sessão (Apple Silicon e Intel)
  if [[ -x /opt/homebrew/bin/brew ]]; then eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -x /usr/local/bin/brew ]]; then eval "$(/usr/local/bin/brew shellenv)"; fi
  ok "Homebrew instalado"
elif [[ "$OS" == "macos" ]]; then
  skip "Homebrew"
fi

# Ferramentas base mínimas
for tool in git curl; do
  if have "$tool"; then skip "$tool"; else working "Instalando $tool"; pkg_install "$tool"; ok "$tool instalado"; fi
done
# Em Debian/Ubuntu, garante suporte a repositórios https e build de pacotes Python
if [[ "$PKG" == "apt" ]]; then
  pkg_install ca-certificates || true
  pkg_install software-properties-common || true
fi

# =============================================================================
#  ETAPA 1 — Python 3.13 + venv
# =============================================================================
step "Python ${PYTHON_TARGET} + venv"

python_ok() {
  # Verdadeiro se existe um python com a versão alvo e o módulo venv funciona
  local bin
  for bin in "python${PYTHON_TARGET}" python3 python; do
    if have "$bin" && "$bin" -c "import sys; exit(0 if sys.version_info[:2]==(${PYTHON_TARGET/./, }) else 1)" 2>/dev/null; then
      if "$bin" -c "import venv" 2>/dev/null; then PYTHON_BIN="$bin"; return 0; fi
    fi
  done
  return 1
}

PYTHON_BIN=""
if python_ok; then
  skip "Python ${PYTHON_TARGET} ($("$PYTHON_BIN" --version 2>&1))"
else
  working "Instalando Python ${PYTHON_TARGET}"
  case "$PKG" in
    brew)
      pkg_install "python@${PYTHON_TARGET}"
      ;;
    apt)
      # deadsnakes oferece versões recentes de Python no Ubuntu/Debian
      if ! apt-cache show "python${PYTHON_TARGET}" >/dev/null 2>&1; then
        info "Adicionando o PPA deadsnakes (Python recente)"
        pkg_install software-properties-common
        retry $SUDO add-apt-repository -y ppa:deadsnakes/ppa >>"$LOG_FILE" 2>&1 || \
          warn "Não consegui adicionar o deadsnakes; tentando pacote nativo da distro."
        PKG_UPDATED=0; pkg_update_once
      fi
      pkg_install "python${PYTHON_TARGET}" || pkg_install python3
      pkg_install "python${PYTHON_TARGET}-venv" || pkg_install python3-venv || true
      pkg_install "python${PYTHON_TARGET}-dev"  || true
      ;;
    dnf)
      pkg_install "python${PYTHON_TARGET/./}" || pkg_install "python${PYTHON_TARGET}" || pkg_install python3
      ;;
    pacman)
      pkg_install python
      ;;
    zypper)
      pkg_install "python${PYTHON_TARGET/./}" || pkg_install python3
      ;;
  esac
  if python_ok; then
    ok "Python instalado: $("$PYTHON_BIN" --version 2>&1)"
  else
    # fallback: qualquer python3 com venv serve para continuar
    if have python3 && python3 -c "import venv" 2>/dev/null; then
      PYTHON_BIN="python3"
      warn "Python ${PYTHON_TARGET} exato não disponível; usando $(python3 --version 2>&1)."
    else
      echo "Não consegui deixar um Python utilizável com venv. Veja $LOG_FILE."; exit 1
    fi
  fi
fi

# =============================================================================
#  ETAPA 2 — Node.js + npm/npx
# =============================================================================
step "Node.js + npm/npx"

if have node && have npm && have npx; then
  skip "Node.js ($(node --version)) / npm ($(npm --version))"
else
  working "Instalando Node.js LTS"
  case "$PKG" in
    brew)
      pkg_install node
      ;;
    apt)
      # NodeSource fornece o Node LTS mais atual para Debian/Ubuntu
      retry bash -c "curl -fsSL https://deb.nodesource.com/setup_lts.x | $SUDO -E bash -" >>"$LOG_FILE" 2>&1 \
        || warn "NodeSource falhou; tentando pacote da distro."
      pkg_install nodejs || true
      have npm || pkg_install npm || true
      ;;
    dnf)
      retry bash -c "curl -fsSL https://rpm.nodesource.com/setup_lts.x | $SUDO bash -" >>"$LOG_FILE" 2>&1 || true
      pkg_install nodejs || true
      ;;
    pacman)
      pkg_install nodejs; pkg_install npm
      ;;
    zypper)
      pkg_install nodejs; pkg_install npm || true
      ;;
  esac
  if have node && have npm; then
    ok "Node.js instalado: $(node --version) (npm $(npm --version))"
  else
    echo "Não consegui instalar o Node.js. Veja $LOG_FILE."; exit 1
  fi
fi

# =============================================================================
#  ETAPA 3 — Docker + Docker Compose
# =============================================================================
step "Docker + Docker Compose"

if have docker && docker compose version >/dev/null 2>&1; then
  skip "Docker ($(docker --version | awk '{print $3}' | tr -d ,))"
elif have docker; then
  skip "Docker (instalado)"
  warn "Plugin 'docker compose' não detectado — verifique sua instalação do Docker."
else
  working "Instalando Docker"
  case "$OS" in
    macos)
      # No macOS o Docker roda via Docker Desktop (aplicativo)
      retry brew install --cask docker >>"$LOG_FILE" 2>&1
      ok "Docker Desktop instalado"
      warn "Abra o aplicativo ${BOLD}Docker${RESET} uma vez para finalizar a configuração."
      warn "Depois confirme com: ${BOLD}docker run hello-world${RESET}"
      ;;
    linux)
      # Script oficial de conveniência da Docker (cobre as principais distros)
      working "Baixando e executando o instalador oficial da Docker"
      retry bash -c "curl -fsSL https://get.docker.com | $SUDO sh" >>"$LOG_FILE" 2>&1
      # Habilita e inicia o serviço, se houver systemd
      if have systemctl; then
        $SUDO systemctl enable --now docker >>"$LOG_FILE" 2>&1 || true
      fi
      # Adiciona o usuário ao grupo docker (evita precisar de sudo)
      if [[ -n "$SUDO" ]]; then
        $SUDO groupadd -f docker >>"$LOG_FILE" 2>&1 || true
        $SUDO usermod -aG docker "$USER" >>"$LOG_FILE" 2>&1 || true
        warn "Você foi adicionado ao grupo 'docker'. ${BOLD}Faça logout/login${RESET} (ou rode 'newgrp docker') para usar o Docker sem sudo."
      fi
      ok "Docker instalado"
      ;;
  esac
fi

# =============================================================================
#  ETAPA 4 — CLIs de IA (Claude Code, OpenCode, Codex)
# =============================================================================
step "CLIs de IA (Claude Code · OpenCode · Codex)"

# Instala um pacote npm global de forma idempotente (verifica o binário)
npm_global_cli() {
  local bin="$1" pkg="$2" label="$3"
  if have "$bin"; then
    skip "$label"
  else
    working "Instalando $label  ($pkg)"
    if retry npm install -g "$pkg" >>"$LOG_FILE" 2>&1; then
      ok "$label instalado"
    else
      warn "Não consegui instalar $label via npm. Você pode instalar depois com: npm i -g $pkg"
    fi
  fi
}

if have npm; then
  npm_global_cli claude   "@anthropic-ai/claude-code" "Claude Code CLI"
  npm_global_cli opencode "opencode-ai"               "OpenCode CLI"
  npm_global_cli codex    "@openai/codex"             "Codex CLI"
else
  warn "npm indisponível — pulei a instalação dos CLIs de IA."
fi

# =============================================================================
#  ETAPA 5 — GitHub CLI (gh) + autenticação no GitHub
# =============================================================================
step "GitHub CLI (gh) + autenticação no GitHub"

# Instala o gh — a CLI oficial do GitHub (para criar/enviar repositórios)
install_gh() {
  if have gh; then skip "GitHub CLI (gh)"; return 0; fi
  working "Instalando GitHub CLI (gh)"
  case "$PKG" in
    brew)
      pkg_install gh
      ;;
    apt)
      if apt-cache show gh >/dev/null 2>&1; then
        pkg_install gh
      else
        # Repositório oficial do GitHub CLI (https://cli.github.com)
        retry bash -c "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | $SUDO dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg" >>"$LOG_FILE" 2>&1
        $SUDO chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg >>"$LOG_FILE" 2>&1 || true
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
          | $SUDO tee /etc/apt/sources.list.d/github-cli.list >/dev/null
        PKG_UPDATED=0; pkg_update_once
        pkg_install gh
      fi
      ;;
    dnf)
      pkg_install gh || {
        retry $SUDO dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo >>"$LOG_FILE" 2>&1 || true
        pkg_install gh
      }
      ;;
    pacman)
      pkg_install github-cli
      ;;
    zypper)
      pkg_install gh || true
      ;;
  esac
  if have gh; then
    ok "GitHub CLI instalado ($(gh --version | head -1))"
  else
    warn "Não consegui instalar o gh automaticamente. Instale depois: https://cli.github.com"
  fi
}
install_gh

# Fallback de autenticação: guia o usuário a gerar e COLAR um token de acesso.
# Usado quando o 'gh auth login' padrão (navegador/dispositivo) não dá certo —
# útil em máquinas sem navegador (servidores/WSL) ou quando o fluxo web falha.
gh_token_login() {
  echo
  info "Vamos autenticar pelo método do ${BOLD}token de acesso${RESET}."
  info "É como uma senha temporária que autoriza este computador a enviar seu projeto."
  echo
  info "${BOLD}Passo a passo (faça no seu navegador, pode ser no celular):${RESET}"
  info "  ${CYAN}1.${RESET} Faça login na sua conta em ${BOLD}https://github.com${RESET}"
  info "  ${CYAN}2.${RESET} Abra este link, que já vem com tudo pré-preenchido:"
  info "       ${BOLD}https://github.com/settings/tokens/new?scopes=repo,workflow&description=Setup%20PycodeBR${RESET}"
  info "  ${CYAN}3.${RESET} Em ${BOLD}Expiration${RESET} escolha um prazo (ex.: 30 days)."
  info "  ${CYAN}4.${RESET} Os escopos ${BOLD}repo${RESET} e ${BOLD}workflow${RESET} já vêm marcados — deixe assim."
  info "  ${CYAN}5.${RESET} Desça e clique no botão verde ${BOLD}Generate token${RESET}."
  info "  ${CYAN}6.${RESET} Copie o código gerado (começa com ${BOLD}ghp_...${RESET})."
  info "     ${GREY}Atenção: o GitHub só mostra esse código UMA vez.${RESET}"
  echo
  info "Cole o token abaixo e tecle ENTER. ${GREY}(por segurança ele não aparece na tela)${RESET}"
  # Lê o token sem exibir na tela; -s some com o eco, então imprimimos a quebra de linha.
  local GH_PAT=""
  read -r -s -p "  ${CYAN}🔑 Cole seu token do GitHub: ${RESET}" GH_PAT </dev/tty || true
  echo
  if [[ -z "$GH_PAT" ]]; then
    warn "Nenhum token informado. Pulando a autenticação por enquanto."
    warn "Quando tiver o token, rode dentro da pasta: ${BOLD}gh auth login --with-token${RESET}"
    return 1
  fi
  working "Autenticando no GitHub com o token"
  if printf '%s' "$GH_PAT" | gh auth login --with-token >>"$LOG_FILE" 2>&1; then
    local gh_user; gh_user="$(gh api user --jq .login 2>/dev/null || true)"
    ok "Autenticado no GitHub${gh_user:+ como ${BOLD}@${gh_user}${RESET}}"
    unset GH_PAT
    return 0
  fi
  warn "O token não foi aceito (pode estar incompleto, expirado ou sem o escopo 'repo')."
  warn "Gere um novo no link acima e rode: ${BOLD}gh auth login --with-token${RESET}"
  unset GH_PAT
  return 1
}

# Autentica você no GitHub — pula se já estiver autenticado.
# 1) tenta o fluxo padrão do gh (navegador/dispositivo);
# 2) se falhar, cai no fallback guiado por token (gh_token_login).
if have gh; then
  if gh auth status >/dev/null 2>&1; then
    skip "Autenticação no GitHub (gh já autenticado)"
  elif [[ -n "${GH_TOKEN:-}${GITHUB_TOKEN:-}" ]]; then
    # Já existe um token no ambiente — o gh usa ele sozinho, nada a fazer.
    skip "Autenticação no GitHub (usando token da variável de ambiente)"
  else
    info "Vamos conectar você ao GitHub (necessário para enviar o projeto)."
    info "A seguir o GitHub CLI faz algumas perguntas ${BOLD}em inglês${RESET}. Responda assim:"
    info "  ${CYAN}•${RESET} ${BOLD}What account do you want to log into?${RESET} → escolha ${BOLD}GitHub.com${RESET}"
    info "  ${CYAN}•${RESET} ${BOLD}What is your preferred protocol...?${RESET} → escolha ${BOLD}HTTPS${RESET}"
    info "  ${CYAN}•${RESET} ${BOLD}Authenticate Git with your GitHub credentials?${RESET} → ${BOLD}Yes${RESET} (Sim)"
    info "  ${CYAN}•${RESET} ${BOLD}How would you like to authenticate...?${RESET} → ${BOLD}Login with a web browser${RESET} (pelo navegador)"
    info "  ${CYAN}•${RESET} Ele mostra um código (ex.: ${BOLD}ABCD-1234${RESET}); copie, tecle ENTER, cole no navegador e autorize."
    info "${GREY}(Use ↑ ↓ para navegar e ENTER para escolher. Se não conseguir, seguimos pelo token.)${RESET}"
    gh auth login </dev/tty || true
    # Confirma se deu certo; se não, oferece o fallback guiado por token.
    if gh auth status >/dev/null 2>&1; then
      gh_user="$(gh api user --jq .login 2>/dev/null || true)"
      ok "Autenticado no GitHub${gh_user:+ como ${BOLD}@${gh_user}${RESET}}"
    else
      warn "A autenticação padrão não foi concluída. Vamos tentar pelo token."
      gh_token_login || true
    fi
  fi
else
  warn "gh indisponível — a autenticação no GitHub será pulada."
fi

# =============================================================================
#  ETAPA 6 — Coleta dos dados do projeto (onde e qual nome)
# =============================================================================
step "Dados do seu projeto"

echo "  Agora vamos criar a pasta do seu projeto."
echo ""

# Onde criar
DEFAULT_DIR="$HOME/projects"
while true; do
  read -r -p "  ${CYAN}📁 Onde deseja criar a pasta do seu projeto?${RESET} [${DEFAULT_DIR}]: " BASE_DIR || true
  BASE_DIR="${BASE_DIR:-$DEFAULT_DIR}"
  BASE_DIR="${BASE_DIR/#\~/$HOME}"     # expande ~
  [[ -n "$BASE_DIR" ]] && break
  warn "Informe um diretório válido."
done

# Nome do projeto (sem espaços)
while true; do
  read -r -p "  ${CYAN}🏷  Qual o nome do projeto? (não use espaços)${RESET}: " PROJECT_NAME || true
  if [[ -z "$PROJECT_NAME" ]]; then
    warn "O nome não pode ser vazio."
  elif [[ "$PROJECT_NAME" =~ [[:space:]] ]]; then
    warn "O nome não pode ter espaços. Use _ ou - (ex: scsi_v1)."
  elif [[ ! "$PROJECT_NAME" =~ ^[A-Za-z0-9._-]+$ ]]; then
    warn "Use apenas letras, números, ponto, hífen ou underline."
  else
    break
  fi
done

PROJECT_DIR="${BASE_DIR%/}/${PROJECT_NAME}"
info "Caminho do projeto: ${BOLD}${PROJECT_DIR}${RESET}"

# =============================================================================
#  ETAPA 7 — Criação da pasta (com checagem de pasta existente)
# =============================================================================
step "Criando a pasta do projeto"

if [[ -d "$PROJECT_DIR" ]]; then
  warn "A pasta ${BOLD}${PROJECT_DIR}${RESET} JÁ EXISTE."
  if [[ -n "$(ls -A "$PROJECT_DIR" 2>/dev/null)" ]]; then
    warn "E ela NÃO está vazia. Criar o projeto aqui pode sobrescrever arquivos."
  fi
  if confirm_SN "Deseja MESMO continuar usando esta pasta existente?"; then
    ok "Ok, continuando na pasta existente."
  else
    info "Operação cancelada pelo usuário. Rode o script de novo com outro caminho/nome."
    exit 0
  fi
else
  working "Criando ${PROJECT_DIR}"
  mkdir -p "$PROJECT_DIR"
  ok "Pasta criada"
fi
cd "$PROJECT_DIR"

# =============================================================================
#  ETAPA 8 — .venv + Django + startproject core . + requirements.txt + .gitignore
# =============================================================================
step "Ambiente Python do projeto (.venv + Django)"

if [[ -d ".venv" ]]; then
  skip ".venv já existe"
else
  working "Criando ambiente virtual (.venv) com ${PYTHON_BIN}"
  "$PYTHON_BIN" -m venv .venv
  ok ".venv criada"
fi

# Ativa a venv NESTA sessão do script
# shellcheck disable=SC1091
source .venv/bin/activate
ok "Ambiente virtual ativado ($(python --version 2>&1))"

working "Atualizando pip"
retry python -m pip install --upgrade pip >>"$LOG_FILE" 2>&1
ok "pip atualizado ($(pip --version | awk '{print $2}'))"

# Instala Django (se ainda não estiver na venv)
if python -c "import django" 2>/dev/null; then
  skip "Django ($(python -c 'import django; print(django.get_version())'))"
else
  working "Instalando Django"
  retry pip install "Django" >>"$LOG_FILE" 2>&1
  ok "Django instalado ($(python -c 'import django; print(django.get_version())'))"
fi

# Cria o projeto Django 'core' no diretório atual (se ainda não existir)
if [[ -f "manage.py" ]]; then
  skip "Projeto Django já existe (manage.py encontrado)"
else
  working "Criando projeto Django: django-admin startproject core ."
  django-admin startproject core .
  ok "Projeto 'core' criado"
fi

# Gera/atualiza requirements.txt
working "Gerando requirements.txt (pip freeze)"
pip freeze >requirements.txt
ok "requirements.txt gerado ($(wc -l <requirements.txt | tr -d ' ') pacotes)"

# Cria o .gitignore do projeto (mesmo conteúdo do projeto SCSI v1)
if [[ -f ".gitignore" ]]; then
  skip ".gitignore já existe (não foi sobrescrito)"
else
  working "Criando .gitignore"
  cat >.gitignore <<'GITEOF'
# Created by https://www.toptal.com/developers/gitignore/api/django
# Edit at https://www.toptal.com/developers/gitignore?templates=django

### Django ###
*.log
*.pot
*.pyc
__pycache__/
local_settings.py
db.sqlite3
db.sqlite3-journal
media

# If your build process includes running collectstatic, then you probably don't need or want to include staticfiles/
# in your Git repository. Update and uncomment the following line accordingly.
# <django-project-name>/staticfiles/

### Django.Python Stack ###
# Byte-compiled / optimized / DLL files
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo

# Django stuff:

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm.fming.dev/#use-with-ide
.pdm.toml

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a more nuclear
#  option (not recommended) you can uncomment the following to ignore the entire idea folder.
#.idea/

# End of https://www.toptal.com/developers/gitignore/api/django
.claude
.DS_Store
site/
staticfiles/
GITEOF
  ok ".gitignore criado (mesmo padrão do projeto SCSI v1)"
fi

# =============================================================================
#  ETAPA 9 — Arquivo .env com as variáveis mais usadas (em branco)
# =============================================================================
step "Arquivo .env (variáveis de ambiente)"

if [[ -f ".env" ]]; then
  skip ".env já existe (não foi sobrescrito)"
else
  working "Criando .env modelo"
  cat >.env <<'ENVEOF'
# =============================================================================
#  .env — variáveis de ambiente do projeto (PREENCHA antes de rodar)
#  Nunca versione este arquivo com segredos reais (mantenha no .gitignore).
# =============================================================================

# --- Django ---
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# --- Localização ---
TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br

# --- Banco de dados (PostgreSQL) ---
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
DATABASE_URL=

# --- RabbitMQ ---
RABBITMQ_DEFAULT_USER=
RABBITMQ_DEFAULT_PASS=

# --- Celery / Redis ---
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=
REDIS_URL=

# --- IA / LLM ---
OPENAI_API_KEY=
OPENAI_MODEL=
ANTHROPIC_API_KEY=
LANGSMITH_API_KEY=

# --- E-mail (SMTP) ---
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
ENVEOF
  ok ".env criado (variáveis em branco, prontas para preencher)"
fi

# =============================================================================
#  ETAPA 11 — Enviar o projeto para o GitHub (opcional)
# =============================================================================
step "Enviar o projeto para o GitHub (opcional)"

if ! have gh; then
  warn "gh não está disponível — pulando o envio ao GitHub."
  warn "Instale em https://cli.github.com e depois rode 'gh repo create' na pasta."
elif ! gh auth status >/dev/null 2>&1; then
  warn "Você não está autenticado no GitHub. Pulando o envio."
  warn "Rode 'gh auth login' e depois 'gh repo create' dentro da pasta do projeto."
elif confirm_SN "Deseja enviar este projeto para o GitHub agora?"; then
  # Nome do repositório — sugere o nome da pasta do projeto como padrão
  read -r -p "  ${CYAN}🏷  Nome do repositório no GitHub${RESET} [${PROJECT_NAME}]: " REPO_NAME || true
  REPO_NAME="${REPO_NAME:-$PROJECT_NAME}"

  # Visibilidade: público ou privado
  if confirm_SN "O repositório deve ser PÚBLICO? (responda N para PRIVADO)"; then
    VISIBILITY="--public"
  else
    VISIBILITY="--private"
  fi

  have git || pkg_install git

  # Inicializa o repositório git (se ainda não houver)
  if [[ ! -d .git ]]; then
    working "Inicializando repositório git"
    git init -b main >>"$LOG_FILE" 2>&1 || git init >>"$LOG_FILE" 2>&1
  fi

  # Garante uma identidade git (usa os dados da sua conta do GitHub se faltar)
  if [[ -z "$(git config user.email 2>/dev/null)" && -z "$(git config --global user.email 2>/dev/null)" ]]; then
    gh_login="$(gh api user --jq .login 2>/dev/null || true)"
    gh_name="$(gh api user --jq '.name // .login' 2>/dev/null || true)"
    if [[ -n "$gh_login" ]]; then
      git config user.name  "${gh_name:-$gh_login}"
      git config user.email "${gh_login}@users.noreply.github.com"
    fi
  fi

  working "Criando o primeiro commit (\"first commit\")"
  git add -A
  git commit -m "first commit" >>"$LOG_FILE" 2>&1 || warn "Nada novo para commitar."

  working "Criando o repositório no GitHub e enviando (gh repo create)"
  if gh repo create "$REPO_NAME" $VISIBILITY --source=. --remote=origin --push >>"$LOG_FILE" 2>&1; then
    REPO_URL="$(gh repo view "$REPO_NAME" --json url --jq .url 2>/dev/null || true)"
    ok "Projeto enviado ao GitHub${REPO_URL:+: $REPO_URL}"
  else
    warn "Não consegui criar/enviar o repositório. Veja o ${LOG_FILE}."
    warn "Talvez o nome '$REPO_NAME' já exista na sua conta — tente outro com 'gh repo create'."
  fi
else
  info "Ok! O projeto não foi enviado ao GitHub."
  info "Quando quiser, dentro da pasta rode: ${CYAN}gh repo create${RESET}."
fi

# =============================================================================
#  FIM — Resumo + próximos passos
# =============================================================================
banner "✅  TUDO PRONTO!"
echo "  Seu ambiente e seu projeto estão configurados."
echo ""
echo "  ${BOLD}Resumo:${RESET}"
echo "    • Projeto.....: ${BOLD}${PROJECT_DIR}${RESET}"
echo "    • Python......: $(python --version 2>&1)"
have node   && echo "    • Node........: $(node --version)"
have docker && echo "    • Docker......: $(docker --version 2>/dev/null | awk '{print $3}' | tr -d , || echo 'instalado')"
have claude   && echo "    • Claude Code.: ok"
have opencode && echo "    • OpenCode....: ok"
have codex    && echo "    • Codex.......: ok"
echo ""
echo "  ${BOLD}Próximos passos:${RESET}"
echo "    1. ${CYAN}cd ${PROJECT_DIR}${RESET}"
echo "    2. ${CYAN}source .venv/bin/activate${RESET}     ${GREY}# ativar o ambiente${RESET}"
echo "    3. ${CYAN}python manage.py runserver${RESET}    ${GREY}# testar o Django${RESET}"
echo "    4. Preencha o arquivo ${BOLD}.env${RESET} com seus valores"
echo "    5. Abra seu CLI de IA na pasta: ${CYAN}claude${RESET} (ou ${CYAN}opencode${RESET} / ${CYAN}codex${RESET})"
echo ""
if [[ "$OS" == "linux" ]] && have docker; then
  echo "  ${YELLOW}Lembrete Docker:${RESET} se 'docker ps' pedir sudo, faça logout/login uma vez."
  echo ""
fi
_logfile "CONCLUÍDO com sucesso — projeto em $PROJECT_DIR"
