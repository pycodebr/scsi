#!/usr/bin/env bash
# =============================================================================
#  setup_deploy.sh — Setup COMPLETO de VPS + Deploy (Docker Swarm + Traefik + GHCR)
# =============================================================================
#  PycodeBR — deploy do zero, "como mágica", para qualquer sistema
#  com a mesma stack/estrutura do SCSI (Django + Celery + Postgres + Redis +
#  RabbitMQ, publicado via Traefik no Docker Swarm, imagens no GHCR).
#
#  Este script replica, passo a passo, o tutorial do Encontro Elite #03
#  (Deploy, monitoria e observabilidade de sistemas com IA — parte 1).
#
#  COMO FUNCIONA (leia com calma):
#    Você acessa a VPS UMA vez como root e roda este script. Ele então:
#      FASE 1 (root): prepara o servidor (update, utilitários, timezone,
#        fail2ban, swap, firewall, tuning de produção, Docker, Swarm, labels) e
#        cria o usuário 'deploy'. Você NÃO precisa criar nada à mão.
#      FASE 2 (deploy): o script re-executa a si mesmo JÁ como o usuário 'deploy'
#        (regra de ouro: o deploy é sempre feito pelo usuário deploy) e conduz:
#        chave SSH do GitHub, clone, login no GHCR, .env, redes, build/push/pull,
#        basic auth do Traefik, secret da Cloudflare, deploy da stack e seed.
#
#  COMO RODAR (na VPS, logado como root):
#      bash setup_deploy.sh
#
#  É IDEMPOTENTE: pode rodar de novo quantas vezes quiser — pula o que já existe.
#  Em caso de erro, mostra o motivo/linha/comando e grava log em ~/setup_deploy.log
#  Requisitos: VPS Ubuntu LTS (24.04 recomendado), acesso root, domínio no Cloudflare.
# =============================================================================

set -Eeuo pipefail

# Se a entrada padrão NÃO for um terminal (ex.: rodando via 'curl ... | bash'),
# redireciona a entrada para o terminal real — assim as perguntas funcionam
# mesmo quando o script chega pelo "cano" do curl.
if [[ ! -t 0 && -e /dev/tty ]]; then exec </dev/tty; fi

# ─────────────────────────────────────────────────────────────────────────────
#  Cores / logging visual
# ─────────────────────────────────────────────────────────────────────────────
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1 && [[ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]]; then
  BOLD="$(tput bold)";   RESET="$(tput sgr0)"
  RED="$(tput setaf 1)"; GREEN="$(tput setaf 2)"; YELLOW="$(tput setaf 3)"
  BLUE="$(tput setaf 4)"; CYAN="$(tput setaf 6)"; GREY="$(tput setaf 8)"
else
  BOLD=""; RESET=""; RED=""; GREEN=""; YELLOW=""; BLUE=""; CYAN=""; GREY=""
fi

LOG_FILE="${HOME:-/root}/setup_deploy.log"
STEP=0
PHASE_LABEL=""

_logfile() { printf '%s %s\n' "[$(date '+%F %H:%M:%S')]" "$1" >>"$LOG_FILE" 2>/dev/null || true; }

banner() {
  echo ""
  echo "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${RESET}"
  printf "${BOLD}${CYAN}║${RESET} %-60s ${BOLD}${CYAN}║${RESET}\n" "$1"
  echo "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${RESET}"
}
step() {
  STEP=$((STEP + 1))
  echo ""
  echo "${BOLD}${BLUE}▶ ${PHASE_LABEL} — PASSO ${STEP}:${RESET} ${BOLD}$1${RESET}"
  echo "${GREY}──────────────────────────────────────────────────────────────${RESET}"
  _logfile "PASSO ${STEP} (${PHASE_LABEL}): $1"
}
info()    { echo "  ${BLUE}ℹ${RESET}  $1";  _logfile "INFO  $1"; }
ok()      { echo "  ${GREEN}✔${RESET}  $1";  _logfile "OK    $1"; }
warn()    { echo "  ${YELLOW}⚠${RESET}  $1"; _logfile "WARN  $1"; }
skip()    { echo "  ${GREEN}✓${RESET}  ${GREY}$1 (já existe — pulando)${RESET}"; _logfile "SKIP  $1"; }
working() { echo "  ${CYAN}⏳${RESET} $1..."; _logfile "WORK  $1"; }

# Caixa de DESTAQUE para coisas que o usuário PRECISA fazer (copiar/colar/abrir)
action_box() {
  echo ""
  echo "${BOLD}${YELLOW}  ┌──────────────────────── AÇÃO NECESSÁRIA ───────────────────────┐${RESET}"
  while [[ $# -gt 0 ]]; do echo "${BOLD}${YELLOW}  │${RESET} $1"; shift; done
  echo "${BOLD}${YELLOW}  └────────────────────────────────────────────────────────────────┘${RESET}"
  echo ""
}

pause_enter() {
  echo ""
  read -r -p "  ${BOLD}${GREEN}➜ Quando terminar, pressione ENTER para continuar...${RESET} " _ || true
}

# ─────────────────────────────────────────────────────────────────────────────
#  Tratamento de erros
# ─────────────────────────────────────────────────────────────────────────────
on_error() {
  local exit_code=$1 line=$2 cmd=$3
  echo ""
  echo "${BOLD}${RED}╔══════════════════════════════════════════════════════════════╗${RESET}"
  echo "${BOLD}${RED}║  ❌ ERRO — o script parou                                     ║${RESET}"
  echo "${BOLD}${RED}╚══════════════════════════════════════════════════════════════╝${RESET}"
  echo "  ${RED}Fase.........:${RESET} ${PHASE_LABEL}"
  echo "  ${RED}Passo........:${RESET} ${STEP}"
  echo "  ${RED}Linha........:${RESET} ${line}"
  echo "  ${RED}Comando......:${RESET} ${cmd}"
  echo "  ${RED}Código saída.:${RESET} ${exit_code}"
  echo ""
  echo "  ${YELLOW}O que fazer:${RESET}"
  echo "    1. Leia a mensagem de erro logo acima desta caixa."
  echo "    2. Log completo: ${BOLD}${LOG_FILE}${RESET}"
  echo "    3. Rode o script de novo — ele é idempotente e retoma de onde dá."
  echo ""
  _logfile "ERRO exit=$exit_code line=$line cmd=<$cmd> fase=$PHASE_LABEL passo=$STEP"
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

retry() {
  local max=3 attempt=1 delay=4
  until "$@"; do
    if (( attempt >= max )); then warn "Falhou após ${max} tentativas: $*"; return 1; fi
    warn "Tentativa ${attempt}/${max} falhou. Nova tentativa em ${delay}s..."
    sleep "$delay"; attempt=$((attempt + 1)); delay=$((delay * 2))
  done
}

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

ask() {  # ask "Pergunta" "default" -> ecoa a resposta (prompt vai p/ stderr)
  local prompt="$1" default="${2:-}" answer
  if [[ -n "$default" ]]; then
    read -r -p "  ${CYAN}❯ ${prompt}${RESET} [${default}]: " answer || true
    echo "${answer:-$default}"
  else
    read -r -p "  ${CYAN}❯ ${prompt}${RESET}: " answer || true
    echo "$answer"
  fi
}

ask_secret() {  # lê valor sem ecoar na tela
  local prompt="$1" answer
  read -r -s -p "  ${CYAN}❯ ${prompt}${RESET}: " answer || true
  echo "" >&2
  echo "$answer"
}

gen_secret() { openssl rand -base64 24 2>/dev/null | tr -dc 'A-Za-z0-9' | head -c "${1:-20}" || true; }

# Arquivo de estado para passar dados da fase root -> fase deploy
STATE_FILE_NAME=".setup_deploy.state"

# URL pública do próprio script. Usada como FALLBACK no handoff root->deploy
# quando o script roda via 'bash -c "$(curl ...)"' (sem arquivo em disco).
# Troque pela SUA URL, ou exporte SETUP_DEPLOY_URL=... antes de rodar.
SCRIPT_URL="${SETUP_DEPLOY_URL:-https://pycodebr.com.br/setup_deploy.sh}"

# Detecta o IP PÚBLICO da VPS (para advertise-addr do Swarm e para o DNS).
detect_public_ip() {
  # Força IPv4 (-4): usamos registro A na Cloudflare. IPv6 seria registro AAAA.
  local ip=""
  ip="$(curl -4 -fsS --max-time 5 https://api.ipify.org 2>/dev/null || true)"
  [[ -n "$ip" ]] || ip="$(curl -4 -fsS --max-time 5 https://ifconfig.me 2>/dev/null || true)"
  [[ -n "$ip" ]] || ip="$(curl -4 -fsS --max-time 5 https://icanhazip.com 2>/dev/null || true)"
  ip="$(printf '%s' "$ip" | tr -d '[:space:]')"
  # Fallback local: primeiro endereço IPv4 das interfaces (ignora IPv6).
  [[ -n "$ip" ]] || ip="$(hostname -I 2>/dev/null | tr ' ' '\n' | grep -E '^[0-9]+(\.[0-9]+){3}$' | head -n1)" || true
  printf '%s' "$ip"
}

# Estado do Swarm neste nó e se ele é MANAGER (necessário p/ overlay/stack/secret).
swarm_state() { docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null || echo unknown; }
is_manager()  { [[ "$(docker info --format '{{.Swarm.ControlAvailable}}' 2>/dev/null)" == "true" ]]; }

# Garante que este nó seja um MANAGER do Swarm. Conserta estados inconsistentes
# (ex.: nó "active" mas não-manager, resquício de tentativas anteriores).
ensure_swarm_manager() {
  is_manager && return 0
  local ip
  ip="$(detect_public_ip)"
  ip="$(ask "IP público para anunciar no Swarm (advertise-addr)" "${ip:-127.0.0.1}")"
  if [[ "$(swarm_state)" == "active" ]]; then
    warn "O Swarm está ativo, mas este nó NÃO é manager (estado inconsistente)."
    warn "Como ainda não há nada implantado, o seguro é resetar e reinicializar."
    confirm_SN "Posso resetar o Swarm deste nó (docker swarm leave --force) e reinicializar?" \
      || { echo "Sem um nó manager não dá para seguir. Ajuste o Swarm e rode de novo."; exit 1; }
    docker swarm leave --force >>"$LOG_FILE" 2>&1 || true
  fi
  working "docker swarm init --advertise-addr ${ip}"
  docker swarm init --advertise-addr "$ip" >>"$LOG_FILE" 2>&1
  ok "Swarm inicializado (este nó é o manager)"
}

# Define/atualiza uma variável no .env (substitui a linha se existir, senão adiciona).
# Aceita valores com caracteres especiais ($ / . :) sem expandir nada.
set_env_var() {
  local k="$1" v="$2" tmp
  tmp="$(mktemp)"
  [[ -f .env ]] && { grep -v "^${k}=" .env >"$tmp" 2>/dev/null || true; }
  printf '%s=%s\n' "$k" "$v" >>"$tmp"
  mv "$tmp" .env
  chmod 600 .env
}

# =============================================================================
# =============================================================================
#  FASE 1 — SISTEMA (executada como ROOT)
#  Replica a seção "Configurações iniciais da VPS" do Encontro Elite #03.
# =============================================================================
# =============================================================================
phase_system() {
  PHASE_LABEL="FASE 1: SISTEMA (root)"; STEP=0

  # ── Pré-checagens ──
  step "Verificando o sistema"
  if [[ ! -r /etc/os-release ]]; then echo "Sistema sem /etc/os-release — use Ubuntu/Debian."; exit 1; fi
  # shellcheck disable=SC1091
  . /etc/os-release
  if ! have apt-get; then
    echo "Este script suporta Ubuntu/Debian (apt). Detectado: ${PRETTY_NAME:-?}"; exit 1
  fi
  info "Servidor: ${BOLD}${PRETTY_NAME:-Linux}${RESET}"
  export DEBIAN_FRONTEND=noninteractive

  # ── Coleta de dados da FASE 1 ──
  step "Informações básicas do servidor"
  echo "  Vamos coletar poucas informações para preparar o servidor."
  DEPLOY_USER="$(ask "Nome do usuário de deploy a criar" "deploy")"
  TIMEZONE="$(ask "Fuso horário (timezone)" "America/Sao_Paulo")"
  SWAP_GB="$(ask "Tamanho do swap em GB (0 = não criar)" "4")"
  echo ""
  echo "  ${BOLD}Nome do projeto${RESET} — use EXATAMENTE o nome do repositório no GitHub."
  echo "  ${GREY}(ele vira a pasta principal e prefixo de variáveis, redes e stack)${RESET}"
  PROJECT_NAME="$(ask "Nome do projeto (igual ao repositório)" "")"
  while [[ -z "$PROJECT_NAME" || "$PROJECT_NAME" =~ [[:space:]] ]]; do
    warn "Informe um nome sem espaços (ex: scsi_v1)."
    PROJECT_NAME="$(ask "Nome do projeto (igual ao repositório)" "")"
  done

  # ── update & upgrade ──
  step "Atualizando o servidor (apt update && upgrade)"
  working "apt update"
  retry apt-get update -y >>"$LOG_FILE" 2>&1
  working "apt upgrade (pode demorar alguns minutos)"
  retry apt-get upgrade -y >>"$LOG_FILE" 2>&1
  ok "Servidor atualizado"

  # ── utilitários (mesma lista do Notion) ──
  step "Instalando utilitários (curl, git, htop, iotop, net-tools, unzip)"
  working "apt install utilitários"
  retry apt-get install -y curl git htop iotop net-tools unzip >>"$LOG_FILE" 2>&1
  ok "Utilitários instalados"

  # ── timezone ──
  step "Configurando timezone (${TIMEZONE})"
  if timedatectl show -p Timezone --value 2>/dev/null | grep -qx "$TIMEZONE"; then
    skip "Timezone já é ${TIMEZONE}"
  else
    timedatectl set-timezone "$TIMEZONE" >>"$LOG_FILE" 2>&1 || warn "Não consegui ajustar o timezone."
    ok "Timezone ajustado para ${TIMEZONE}"
  fi

  # ── fail2ban (config idêntica ao Notion) ──
  step "Instalando e configurando o fail2ban (anti força-bruta no SSH)"
  retry apt-get install -y fail2ban >>"$LOG_FILE" 2>&1
  if [[ -f /etc/fail2ban/jail.local ]]; then
    skip "jail.local já existe"
  else
    working "Criando /etc/fail2ban/jail.local"
    tee /etc/fail2ban/jail.local >/dev/null <<'EOF'
[ssh]
enabled = true
port = 22
filter = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
EOF
    ok "jail.local criado (ban 1h após 3 tentativas)"
  fi
  systemctl enable fail2ban >>"$LOG_FILE" 2>&1 || true
  systemctl restart fail2ban >>"$LOG_FILE" 2>&1 || warn "Não consegui (re)iniciar o fail2ban."
  ok "fail2ban ativo"

  # ── swap (4G por padrão, como no Notion) ──
  step "Configurando swap de memória (${SWAP_GB}G)"
  if [[ "$SWAP_GB" == "0" ]]; then
    info "Swap pulado a pedido (0 GB)."
  elif swapon --show 2>/dev/null | grep -q '/swapfile'; then
    skip "Swapfile já ativo"
  else
    working "Criando swapfile de ${SWAP_GB}G"
    if ! fallocate -l "${SWAP_GB}G" /swapfile >>"$LOG_FILE" 2>&1; then
      dd if=/dev/zero of=/swapfile bs=1M count=$((SWAP_GB * 1024)) >>"$LOG_FILE" 2>&1
    fi
    chmod 600 /swapfile
    mkswap /swapfile >>"$LOG_FILE" 2>&1
    swapon /swapfile >>"$LOG_FILE" 2>&1
    grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >>/etc/fstab
    ok "Swap de ${SWAP_GB}G ativo (persistente no /etc/fstab)"
    free -h | sed 's/^/    /' || true
  fi

  # ── firewall (UFW) — libera SSH ANTES de ativar (não derruba a conexão) ──
  step "Configurando firewall (UFW: SSH, HTTP, HTTPS)"
  ufw default deny incoming  >>"$LOG_FILE" 2>&1 || true
  ufw default allow outgoing >>"$LOG_FILE" 2>&1 || true
  ufw allow 22/tcp  comment 'SSH'   >>"$LOG_FILE" 2>&1 || true
  ufw allow 80/tcp  comment 'HTTP'  >>"$LOG_FILE" 2>&1 || true
  ufw allow 443/tcp comment 'HTTPS' >>"$LOG_FILE" 2>&1 || true
  if ufw status 2>/dev/null | grep -q 'Status: active'; then
    skip "UFW já estava ativo (regras garantidas)"
  else
    working "Ativando o UFW"
    ufw --force enable >>"$LOG_FILE" 2>&1
    ok "Firewall ativo (22, 80, 443 liberados)"
  fi

  # ── tuning de produção (sysctl) — bloco idêntico ao Notion ──
  step "Tuning de produção (sysctl)"
  if grep -q 'Production Tuning' /etc/sysctl.conf 2>/dev/null; then
    skip "sysctl de produção já aplicado"
  else
    working "Anexando parâmetros em /etc/sysctl.conf"
    tee -a /etc/sysctl.conf >/dev/null <<'EOF'

# === Production Tuning ===
# Network performance
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_tw_reuse = 1

# File descriptors
fs.file-max = 2097152
fs.inotify.max_user_watches = 524288

# Virtual memory
vm.swappiness = 10
vm.overcommit_memory = 1
EOF
    sysctl -p >>"$LOG_FILE" 2>&1 || warn "sysctl -p retornou aviso (veja o log)."
    ok "Parâmetros de produção aplicados"
  fi

  # ── Docker Engine (instalador oficial, como no Notion) ──
  step "Instalando o Docker Engine"
  if have docker; then
    skip "Docker ($(docker --version | awk '{print $3}' | tr -d ,))"
  else
    working "Removendo versões antigas do Docker (se houver)"
    apt-get remove -y docker docker-engine docker.io containerd runc >>"$LOG_FILE" 2>&1 || true
    working "Instalando via script oficial (get.docker.com)"
    retry bash -c "curl -fsSL https://get.docker.com | sh" >>"$LOG_FILE" 2>&1
    systemctl enable docker >>"$LOG_FILE" 2>&1 || true
    systemctl start docker  >>"$LOG_FILE" 2>&1 || true
    ok "Docker instalado ($(docker --version | awk '{print $3}' | tr -d ,))"
  fi

  # ── Docker para produção (daemon.json idêntico ao Notion) ──
  step "Configurando o Docker para produção (daemon.json)"
  if [[ -f /etc/docker/daemon.json ]] && grep -q '9323' /etc/docker/daemon.json 2>/dev/null; then
    skip "daemon.json já configurado"
  else
    mkdir -p /etc/docker
    working "Escrevendo /etc/docker/daemon.json"
    tee /etc/docker/daemon.json >/dev/null <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "20m",
    "max-file": "5"
  },
  "storage-driver": "overlay2",
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 65536
    }
  },
  "metrics-addr": "127.0.0.1:9323",
  "ipv6": false
}
EOF
    systemctl restart docker >>"$LOG_FILE" 2>&1
    ok "Docker reconfigurado para produção"
  fi

  # ── Swarm + labels do node (igual ao Notion: infra=true, app=true) ──
  step "Inicializando o Docker Swarm"
  if is_manager; then
    skip "Swarm ativo e este nó é manager"
  else
    ensure_swarm_manager
  fi
  local nodehost
  nodehost="$(docker node ls --format '{{.Hostname}}' 2>/dev/null | head -n1)" || true
  if [[ -n "$nodehost" ]]; then
    docker node update --label-add infra=true "$nodehost" >>"$LOG_FILE" 2>&1 || true
    docker node update --label-add app=true   "$nodehost" >>"$LOG_FILE" 2>&1 || true
    ok "Labels do nó aplicadas (infra=true, app=true)"
  fi

  # ── usuário deploy (adduser + sudo + chaves SSH do root, como no Notion) ──
  step "Criando o usuário '${DEPLOY_USER}' (dono do deploy)"
  if id "$DEPLOY_USER" >/dev/null 2>&1; then
    skip "Usuário ${DEPLOY_USER} já existe"
  else
    working "Criando usuário ${DEPLOY_USER}"
    adduser --disabled-password --gecos "" "$DEPLOY_USER" >>"$LOG_FILE" 2>&1
    ok "Usuário ${DEPLOY_USER} criado"
  fi
  usermod -aG sudo,docker "$DEPLOY_USER"
  ok "${DEPLOY_USER} adicionado aos grupos sudo e docker"
  # sudo sem senha (facilita o aluno; pode endurecer depois)
  echo "${DEPLOY_USER} ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers.d/90-${DEPLOY_USER}
  chmod 440 /etc/sudoers.d/90-${DEPLOY_USER}
  # Copia as chaves SSH autorizadas do root para o deploy
  if [[ -f /root/.ssh/authorized_keys ]]; then
    mkdir -p "/home/${DEPLOY_USER}/.ssh"
    cp /root/.ssh/authorized_keys "/home/${DEPLOY_USER}/.ssh/"
    chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "/home/${DEPLOY_USER}/.ssh"
    chmod 700 "/home/${DEPLOY_USER}/.ssh"
    chmod 600 "/home/${DEPLOY_USER}/.ssh/authorized_keys"
    ok "Chaves SSH copiadas — você poderá acessar como ${DEPLOY_USER} com a mesma chave"
  else
    warn "root não tem authorized_keys. Garanta acesso SSH ao usuário ${DEPLOY_USER} depois."
  fi

  # ── Handoff para a FASE 2 (como usuário deploy) ──
  step "Passando o bastão para o usuário '${DEPLOY_USER}'"
  local self dest state
  self="$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || echo "")"
  dest="/home/${DEPLOY_USER}/setup_deploy.sh"
  if [[ -n "$self" && -f "$self" ]]; then
    cp "$self" "$dest"                       # rodando a partir de um arquivo em disco
  else
    # Rodando via 'bash -c "$(curl ...)"' — sem arquivo: baixamos da URL pública.
    working "Obtendo o script de ${SCRIPT_URL} para continuar como ${DEPLOY_USER}"
    if ! curl -fsSL "$SCRIPT_URL" -o "$dest" 2>>"$LOG_FILE"; then
      warn "Não consegui obter o arquivo do script para continuar automaticamente."
      action_box \
        "A FASE 1 (servidor) terminou com sucesso. Para a FASE 2 (deploy):" \
        "  su - ${DEPLOY_USER}" \
        "  bash setup_deploy.sh   (ou rode o one-liner de novo como ${DEPLOY_USER})"
      exit 0
    fi
  fi
  chown "${DEPLOY_USER}:${DEPLOY_USER}" "$dest"
  chmod 750 "$dest"
  state="/home/${DEPLOY_USER}/${STATE_FILE_NAME}"
  cat >"$state" <<EOF
PROJECT_NAME=${PROJECT_NAME}
EOF
  chown "${DEPLOY_USER}:${DEPLOY_USER}" "$state"
  ok "Script copiado para ${dest}"
  info "Continuando AUTOMATICAMENTE como '${DEPLOY_USER}'..."
  echo ""
  # exec: substitui o processo atual — daqui pra frente rodamos como deploy
  exec sudo -iu "$DEPLOY_USER" bash "$dest" --as-deploy
}

# =============================================================================
# =============================================================================
#  FASE 2 — DEPLOY (executada como usuário 'deploy')
#  Replica a seção "Configurando e rodando a stack na VPS" do Encontro Elite #03.
# =============================================================================
# =============================================================================
phase_deploy() {
  PHASE_LABEL="FASE 2: DEPLOY (${USER:-$(whoami)})"; STEP=0

  banner "🚢  FASE 2 — DEPLOY (usuário: ${USER:-$(whoami)})"

  # Carrega estado vindo da FASE 1, se existir
  PROJECT_NAME="${PROJECT_NAME:-}"
  if [[ -f "${HOME}/${STATE_FILE_NAME}" ]]; then
    # shellcheck disable=SC1090
    . "${HOME}/${STATE_FILE_NAME}"
  fi

  # ── Pré-checagens ──
  step "Verificando Docker e Swarm"
  if ! have docker; then
    echo "Docker não encontrado. Rode a FASE 1 como root primeiro (bash setup_deploy.sh)."; exit 1
  fi
  if ! docker info >/dev/null 2>&1; then
    echo "Sem permissão no Docker. Saia e entre de novo (newgrp docker) ou rode a FASE 1 como root."; exit 1
  fi
  # Exige nó MANAGER (criar rede overlay / stack / secret precisa disso).
  # Se o Swarm estiver ausente ou inconsistente, conserta automaticamente.
  ensure_swarm_manager
  ok "Docker e Swarm OK (nó manager)"

  # ── Dados do projeto/GitHub ──
  step "Dados do projeto e do GitHub"
  [[ -n "$PROJECT_NAME" ]] || PROJECT_NAME="$(ask "Nome do projeto (igual ao repositório)" "")"
  while [[ -z "$PROJECT_NAME" || "$PROJECT_NAME" =~ [[:space:]] ]]; do
    warn "Informe um nome sem espaços."; PROJECT_NAME="$(ask "Nome do projeto (igual ao repositório)" "")"
  done
  PROJECT_DIR="${HOME}/${PROJECT_NAME}"
  info "Pasta do projeto: ${BOLD}${PROJECT_DIR}${RESET}"

  # ── Chave SSH para o GitHub (id_ed25519_github, como no Notion) ──
  step "Gerando chave SSH para o GitHub"
  SSH_KEY="${HOME}/.ssh/id_ed25519_github"
  mkdir -p "${HOME}/.ssh"; chmod 700 "${HOME}/.ssh"
  if [[ -f "$SSH_KEY" ]]; then
    skip "Chave SSH já existe (${SSH_KEY})"
  else
    working "Gerando chave ed25519 (comment: vps-${PROJECT_NAME})"
    ssh-keygen -t ed25519 -C "vps-${PROJECT_NAME}" -f "$SSH_KEY" -N "" >>"$LOG_FILE" 2>&1
    ok "Chave SSH gerada"
  fi
  echo ""
  echo "  ${BOLD}Esta é a sua CHAVE PÚBLICA (copie TODA a linha abaixo):${RESET}"
  echo "${GREY}──────────────────────────────────────────────────────────────${RESET}"
  echo "${BOLD}${GREEN}$(cat "${SSH_KEY}.pub")${RESET}"
  echo "${GREY}──────────────────────────────────────────────────────────────${RESET}"
  action_box \
    "1. Abra no navegador:  https://github.com/settings/ssh/new" \
    "   (GitHub ▸ Settings ▸ SSH and GPG keys ▸ New SSH key)" \
    "2. Cole a chave pública acima e salve." \
    "3. Volte aqui e pressione ENTER."
  pause_enter

  # ── ~/.ssh/config ──
  step "Configurando ~/.ssh/config"
  if grep -q "Host github.com" "${HOME}/.ssh/config" 2>/dev/null; then
    skip "~/.ssh/config já tem github.com"
  else
    cat >>"${HOME}/.ssh/config" <<SSHCFG
Host github.com
  HostName github.com
  User git
  IdentityFile ${SSH_KEY}
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
SSHCFG
    chmod 600 "${HOME}/.ssh/config"
    ok "~/.ssh/config criado"
  fi
  ssh-keyscan github.com >>"${HOME}/.ssh/known_hosts" 2>/dev/null || true
  if ssh -o BatchMode=yes -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    ok "Autenticação no GitHub via SSH confirmada"
  else
    warn "Não confirmei a autenticação SSH (pode ser normal). Seguimos para o clone."
  fi

  # ── Clone do projeto (SSH e, se falhar, HTTPS) ──
  step "Clonando o projeto"
  if [[ -d "${PROJECT_DIR}/.git" ]]; then
    skip "Projeto já clonado em ${PROJECT_DIR}"
  else
    REPO_SSH="$(ask "URL do repositório em SSH (ex: git@github.com:user/${PROJECT_NAME}.git)" "")"
    if ! retry git clone "$REPO_SSH" "$PROJECT_DIR" >>"$LOG_FILE" 2>&1; then
      warn "Clone via SSH falhou. Vamos tentar via HTTPS."
      REPO_HTTPS="$(ask "URL do repositório em HTTPS (ex: https://github.com/user/${PROJECT_NAME}.git)" "")"
      retry git clone "$REPO_HTTPS" "$PROJECT_DIR" >>"$LOG_FILE" 2>&1
    fi
    ok "Repositório clonado em ${PROJECT_DIR}"
  fi
  cd "$PROJECT_DIR"

  # Descobre convenções do projeto a partir dos arquivos clonados
  STACK_FILE="docker-stack.yml"
  [[ -f "$STACK_FILE" ]] || { echo "docker-stack.yml não encontrado no repositório."; exit 1; }
  IMAGE="$(grep -oE 'ghcr\.io/[^:[:space:]"]+' "$STACK_FILE" 2>/dev/null | head -n1)" || true
  [[ -n "$IMAGE" ]] || IMAGE="ghcr.io/usuario/${PROJECT_NAME}"
  GHCR_OWNER="$(echo "$IMAGE" | cut -d/ -f2)"
  if [[ -f scripts/deploy.sh ]]; then
    STACK_NAME="$(grep -E '^STACK_NAME=' scripts/deploy.sh 2>/dev/null | head -n1 | cut -d'"' -f2)" || true
  fi
  STACK_NAME="${STACK_NAME:-$PROJECT_NAME}"
  info "Imagem...: ${BOLD}${IMAGE}${RESET}"
  info "Stack....: ${BOLD}${STACK_NAME}${RESET}"

  # ── Login no GHCR ──
  step "Autenticando no GitHub Container Registry (GHCR)"
  if [[ -f "${HOME}/.docker/config.json" ]] && grep -q 'ghcr.io' "${HOME}/.docker/config.json" 2>/dev/null; then
    skip "Já autenticado no ghcr.io"
  else
    GHCR_OWNER="$(ask "Seu usuário/organização do GitHub (dono das imagens)" "$GHCR_OWNER")"
    action_box \
      "Crie um TOKEN CLASSIC do GitHub (Personal access token classic):" \
      "  GitHub ▸ Settings ▸ Developer settings ▸ Tokens (classic)" \
      "  https://github.com/settings/tokens/new" \
      "  Escopos: read:packages, write:packages, delete:packages" \
      "  Gere e copie o token (vai colar a seguir, sem aparecer na tela)."
    GHCR_TOKEN="$(ask_secret "Cole o token classic do GitHub")"
    working "docker login ghcr.io"
    echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_OWNER" --password-stdin >>"$LOG_FILE" 2>&1
    ok "Autenticado no GHCR como ${GHCR_OWNER}"
  fi

  # ── .env: o usuário COLA o conteúdo do projeto ──
  step "Criando o arquivo .env (cole o conteúdo do seu projeto)"
  if [[ -s .env ]] && ! confirm_SN ".env já existe e tem conteúdo. Quer substituir?"; then
    skip ".env mantido"
  else
    action_box \
      "Vou abrir um EDITOR para você COLAR o conteúdo do .env do seu projeto." \
      "(é o mesmo .env que você usa, com DEBUG=False e os valores de produção)" \
      "" \
      "No editor nano:" \
      "  • Cole o conteúdo (Ctrl+Shift+V, ou clique com o botão direito)" \
      "  • Salvar: Ctrl+O e depois ENTER" \
      "  • Sair:   Ctrl+X"
    pause_enter
    : >.env
    "${EDITOR:-nano}" .env || true
    if [[ ! -s .env ]]; then
      warn "O .env ficou vazio pelo editor. Vamos pelo modo 'colar e finalizar'."
      echo "  ${BOLD}Cole o conteúdo do .env agora. Para FINALIZAR, digite numa linha: ${GREEN}__FIM__${RESET}"
      : >.env
      while IFS= read -r line; do
        [[ "$line" == "__FIM__" ]] && break
        printf '%s\n' "$line" >>.env
      done
    fi
    [[ -s .env ]] || { echo ".env continua vazio — não dá para seguir."; exit 1; }
    chmod 600 .env
    ok ".env salvo ($(wc -l <.env | tr -d ' ') linhas)"
  fi

  # ── Rede traefik_public (criada PRIMEIRO, antes do build) ──
  step "Criando a rede traefik_public"
  if docker network ls --format '{{.Name}}' | grep -qx 'traefik_public'; then
    skip "Rede traefik_public"
  else
    working "docker network create --driver overlay --attachable traefik_public"
    docker network create --driver overlay --attachable traefik_public >>"$LOG_FILE" 2>&1
    ok "Rede traefik_public criada"
  fi

  # ── Build + Push + Pull (igual ao Notion) ──
  step "Build, Push e Pull da imagem"
  local version
  version="$(git rev-parse --short HEAD 2>/dev/null || echo latest)"
  working "docker build -> ${IMAGE}:${version} e :latest"
  retry docker build -t "${IMAGE}:${version}" -t "${IMAGE}:latest" . >>"$LOG_FILE" 2>&1
  ok "Build concluído"
  working "docker push (enviando ao GHCR)"
  retry docker push "${IMAGE}:${version}" >>"$LOG_FILE" 2>&1
  retry docker push "${IMAGE}:latest" >>"$LOG_FILE" 2>&1
  ok "Push concluído"
  working "docker pull (testando o registry)"
  retry docker pull "${IMAGE}:latest" >>"$LOG_FILE" 2>&1
  ok "Pull concluído — registry funcionando"

  # ── Redes overlay internas (internal isolada + egress) ──
  step "Criando as redes overlay do projeto"
  if docker network ls --format '{{.Name}}' | grep -qx "${STACK_NAME}_internal"; then
    skip "Rede ${STACK_NAME}_internal"
  else
    working "Criando ${STACK_NAME}_internal (isolada da internet)"
    docker network create --driver overlay --attachable --internal "${STACK_NAME}_internal" >>"$LOG_FILE" 2>&1
    ok "Rede ${STACK_NAME}_internal criada"
  fi
  if docker network ls --format '{{.Name}}' | grep -qx "${STACK_NAME}_egress"; then
    skip "Rede ${STACK_NAME}_egress"
  else
    working "Criando ${STACK_NAME}_egress (com saída para a internet)"
    docker network create --driver overlay --attachable "${STACK_NAME}_egress" >>"$LOG_FILE" 2>&1
    ok "Rede ${STACK_NAME}_egress criada"
  fi
  docker network ls --filter driver=overlay --format 'table {{.Name}}\t{{.Driver}}\t{{.Scope}}' | sed 's/^/    /' || true

  # ── Basic Auth do dashboard do Traefik (htpasswd -nbB) — salvo no .env ──
  step "Gerando Basic Auth do dashboard do Traefik"
  retry apt-get -y install apache2-utils >>"$LOG_FILE" 2>&1 || sudo apt-get -y install apache2-utils >>"$LOG_FILE" 2>&1 || true
  local dash_user dash_pass htpasswd_raw
  dash_user="$(ask "Usuário do dashboard do Traefik" "admin")"
  dash_pass="$(ask_secret "Senha do dashboard (ENTER para gerar uma)")"
  [[ -n "$dash_pass" ]] || { dash_pass="$(gen_secret 20)"; info "Senha gerada: ${BOLD}${dash_pass}${RESET}"; }
  htpasswd_raw="$(htpasswd -nbB "$dash_user" "$dash_pass")"
  # Salva o hash CRU (um '$') no .env. O docker-stack.yml lê via
  # ${TRAEFIK_DASHBOARD_AUTH} — sem precisar duplicar '$' nem editar o YAML.
  set_env_var "TRAEFIK_DASHBOARD_AUTH" "$htpasswd_raw"
  if grep -q 'TRAEFIK_DASHBOARD_AUTH' "$STACK_FILE" 2>/dev/null; then
    ok "Hash salvo no .env (TRAEFIK_DASHBOARD_AUTH) — o docker-stack.yml já lê de lá"
  else
    warn "Hash salvo no .env, MAS o docker-stack.yml não usa \${TRAEFIK_DASHBOARD_AUTH}."
    warn "No label basicauth.users, troque o hash fixo por:  \${TRAEFIK_DASHBOARD_AUTH}"
  fi
  action_box \
    "Dashboard do Traefik:" \
    "  Usuário: ${dash_user}" \
    "  Senha..: ${dash_pass}   (ANOTE — não será mostrada de novo)"

  # ── Secret da Cloudflare (TLS via DNS-01) ──
  step "Criando o secret da Cloudflare (TLS wildcard via DNS-01)"
  if docker secret inspect CLOUDFLARE_DNS_API_TOKEN >/dev/null 2>&1; then
    skip "Secret CLOUDFLARE_DNS_API_TOKEN já existe"
    if confirm_SN "Quer recriar o secret da Cloudflare?"; then
      docker secret rm CLOUDFLARE_DNS_API_TOKEN >>"$LOG_FILE" 2>&1 || true
    fi
  fi
  if ! docker secret inspect CLOUDFLARE_DNS_API_TOKEN >/dev/null 2>&1; then
    action_box \
      "Crie um API Token na Cloudflare:" \
      "  https://dash.cloudflare.com/profile/api-tokens ▸ Create Token" \
      "  Template 'Edit zone DNS'. Permissions: Zone > DNS > Edit e" \
      "  Zone > Zone > Read. Zone Resources: a SUA zona (domínio)." \
      "  Copie o token (vai colar a seguir, sem aparecer na tela)."
    local cf_token
    cf_token="$(ask_secret "Cole o API Token da Cloudflare")"
    while [[ -z "$cf_token" ]]; do warn "Token vazio."; cf_token="$(ask_secret "Cole o API Token da Cloudflare")"; done
    printf '%s' "$cf_token" | docker secret create CLOUDFLARE_DNS_API_TOKEN - >>"$LOG_FILE" 2>&1
    ok "Secret CLOUDFLARE_DNS_API_TOKEN criado"
  fi

  # ── DNS do domínio (pré-requisito para o TLS funcionar) ──
  step "Conferindo o DNS do domínio"
  local DOMAIN VPS_IP resolved
  DOMAIN="$(grep -E '^DOMAIN=' .env 2>/dev/null | cut -d= -f2- | tr -d '[:space:]')" || true
  VPS_IP="$(detect_public_ip)"
  if [[ -z "$DOMAIN" ]]; then
    warn "Não encontrei DOMAIN no .env — pulando a verificação de DNS."
  else
    # Aviso se o docker-stack.yml tiver domínio fixo diferente do .env
    if grep -qE 'Host\(`' "$STACK_FILE" 2>/dev/null \
       && ! grep -q "$DOMAIN" "$STACK_FILE" 2>/dev/null \
       && ! grep -q '${DOMAIN' "$STACK_FILE" 2>/dev/null; then
      warn "ATENÇÃO: o docker-stack.yml parece ter um domínio FIXO diferente de '${DOMAIN}'."
      warn "Confira os labels do Traefik (Host(...), tls.domains[0].main/sans) e ajuste o domínio."
    fi
    action_box \
      "No Cloudflare, aponte estes registros DNS para o IP da VPS (${VPS_IP:-?}):" \
      "  A   ${DOMAIN}                 ->  ${VPS_IP:-IP_DA_VPS}" \
      "  A   *.${DOMAIN}  (wildcard)   ->  ${VPS_IP:-IP_DA_VPS}" \
      "  (o proxy laranja da Cloudflare pode ficar ATIVO — o TLS é via DNS-01)"
    resolved="$(getent hosts "$DOMAIN" 2>/dev/null | awk '{print $1}' | head -n1)" || true
    if [[ -n "$resolved" ]]; then
      info "Agora ${DOMAIN} resolve para: ${resolved} (com proxy Cloudflare, será um IP da Cloudflare)"
    else
      warn "Ainda não consegui resolver ${DOMAIN} (DNS pode levar minutos para propagar)."
    fi
    confirm_SN "O DNS já está apontando para a VPS e posso seguir com o deploy?" \
      || { warn "Tudo bem — ajuste o DNS e rode o script de novo (ele retoma daqui)."; exit 0; }
  fi

  # ── Deploy da stack (igual ao Notion) ──
  step "Fazendo o deploy da stack"
  # Carrega o .env no AMBIENTE para a interpolação de ${DOMAIN} etc. no stack file.
  # Parser seguro KEY=VALUE (NÃO usa 'source': valores com & $ * @ quebrariam o shell).
  local line key value
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    case "$line" in ''|\#*) continue ;; esac
    [[ "${line#*=}" == "$line" ]] && continue
    key="${line%%=*}"; value="${line#*=}"
    key="${key#"${key%%[![:space:]]*}"}"; key="${key%"${key##*[![:space:]]}"}"
    case "$key" in ''|*[!A-Za-z0-9_]*) continue ;; esac
    case "$value" in
      \"*\") value="${value#\"}"; value="${value%\"}" ;;
      \'*\') value="${value#\'}"; value="${value%\'}" ;;
    esac
    export "$key=$value"
  done < .env
  working "docker stack deploy -c ${STACK_FILE} ${STACK_NAME}"
  docker stack deploy -c "$STACK_FILE" --with-registry-auth "$STACK_NAME" >>"$LOG_FILE" 2>&1
  ok "Stack enviada ao Swarm"

  # ── Verificação ──
  step "Verificando se os serviços subiram"
  working "Aguardando os serviços estabilizarem (até ~3 min)"
  local tries=0 max_tries=36 all_up=0
  while (( tries < max_tries )); do
    if docker stack services "$STACK_NAME" >/dev/null 2>&1 \
       && ! docker stack services "$STACK_NAME" --format '{{.Replicas}}' | grep -qE '^0/'; then
      all_up=1; break
    fi
    sleep 5; tries=$((tries+1))
  done
  echo ""
  docker stack services "$STACK_NAME" 2>/dev/null | sed 's/^/    /' || true
  echo ""
  if (( all_up == 1 )); then
    ok "Todos os serviços estão com réplicas ativas 🎉"
  else
    warn "Alguns serviços ainda não subiram (TLS/migrations podem levar minutos)."
    warn "Acompanhe: docker service logs -f ${STACK_NAME}_traefik   e   ${STACK_NAME}_app"
  fi

  # ── Seed de dados (seed_demo --force, igual ao Notion) ──
  step "Populando dados de demonstração (seed_demo --force)"
  local app_cid=""
  for _ in 1 2 3 4 5 6; do
    app_cid="$(docker ps --filter "name=${STACK_NAME}_app" -q | head -n1)" || true
    [[ -n "$app_cid" ]] && break
    sleep 5
  done
  if [[ -n "$app_cid" ]]; then
    if docker exec "$app_cid" python manage.py seed_demo --force >>"$LOG_FILE" 2>&1; then
      ok "seed_demo executado com sucesso"
    else
      warn "seed_demo falhou (veja o log). Você pode rodar depois manualmente."
    fi
  else
    warn "Container do app ainda não está pronto — rode o seed depois (instruções abaixo)."
  fi

  # ── Final ──
  print_final_instructions
}

print_final_instructions() {
  local domain
  domain="$(grep -E '^DOMAIN=' .env 2>/dev/null | cut -d= -f2-)" || true
  banner "✅  DEPLOY CONCLUÍDO!"
  echo "  Seu sistema está no ar (pode levar alguns minutos para o TLS validar)."
  echo ""
  echo "  ${BOLD}Acessos:${RESET}"
  echo "    • Aplicação....: ${CYAN}https://${domain:-seu-dominio}${RESET}"
  echo "    • Dashboard TLS: ${CYAN}https://traefik.${domain:-seu-dominio}${RESET} (Basic Auth)"
  echo ""
  echo "  ${BOLD}Comandos úteis (dentro de ${PROJECT_DIR}):${RESET}"
  echo "    • Logs do app......: ${CYAN}docker service logs -f ${STACK_NAME}_app${RESET}"
  echo "    • Logs do Traefik..: ${CYAN}docker service logs -f ${STACK_NAME}_traefik${RESET}  ${GREY}(emissão do SSL)${RESET}"
  echo "    • Status...........: ${CYAN}docker stack services ${STACK_NAME}${RESET}"
  echo "    • Volumes..........: ${CYAN}docker volume ls | grep ${STACK_NAME}${RESET}"
  echo "    • Superusuário.....: ${CYAN}APP=\$(docker ps --filter name=${STACK_NAME}_app -q | head -1); docker exec -it \$APP python manage.py createsuperuser${RESET}"
  echo "    • Rodar seed.......: ${CYAN}APP=\$(docker ps --filter name=${STACK_NAME}_app -q | head -1); docker exec -it \$APP python manage.py seed_demo --force${RESET}"
  echo ""
  echo "  ${BOLD}Para fazer deploy após alterações no código:${RESET}"
  echo "    ${CYAN}cd ${PROJECT_DIR}${RESET}"
  echo "    ${CYAN}./scripts/deploy.sh${RESET}            ${GREY}# build + push + deploy completo${RESET}"
  echo "    ${GREY}(use ./scripts/deploy.sh --skip-build para só redeployar a stack)${RESET}"
  echo ""
  echo "  ${GREY}Log completo desta execução: ${LOG_FILE}${RESET}"
  _logfile "CONCLUÍDO — projeto em ${PROJECT_DIR}"
}

# =============================================================================
#  Roteamento: root -> FASE 1 (depois handoff); não-root -> FASE 2
# =============================================================================
: >"$LOG_FILE" 2>/dev/null || true

if [[ "${1:-}" != "--as-deploy" ]]; then
  banner "🚀  SETUP DE VPS + DEPLOY — PycodeBR"
  echo "  Este script faz o deploy COMPLETO do seu sistema, do zero."
  echo "  É seguro e idempotente: pode rodar quantas vezes quiser."
  echo "  Log desta execução: ${GREY}${LOG_FILE}${RESET}"
  echo ""
  echo "  ${BOLD}📋 ANTES DE COMEÇAR, tenha em mãos:${RESET}"
  echo "    • O conteúdo do ${BOLD}.env de produção${RESET} do seu projeto (você vai COLAR ele)"
  echo "    • O ${BOLD}domínio${RESET} já criado e gerenciado na ${BOLD}Cloudflare${RESET}"
  echo "    • A ${BOLD}URL do repositório${RESET} no GitHub (SSH ou HTTPS)"
  echo "    • Um ${BOLD}token classic do GitHub${RESET} (escopos read/write/delete:packages)"
  echo "    • Um ${BOLD}API Token da Cloudflare${RESET} (template 'Edit zone DNS')"
  echo ""
  echo "  ${GREY}Dica: deixe DOMAIN preenchido no seu .env — ele controla o domínio do${RESET}"
  echo "  ${GREY}app E do Traefik (certificado TLS wildcard + host do dashboard).${RESET}"
  if [[ "$(id -u)" -eq 0 ]]; then
    echo ""
    confirm_SN "Tudo em mãos? Posso começar a preparar o servidor?" \
      || { echo "  Sem problemas — rode de novo quando estiver pronto."; exit 0; }
  fi
fi

if [[ "$(id -u)" -eq 0 ]]; then
  phase_system    # termina com 'exec' para a FASE 2 como usuário deploy
else
  phase_deploy
fi
