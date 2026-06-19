#!/bin/bash
set -euo pipefail

# ── SCSI — Deploy completo (Docker Swarm, executado NA VPS) ──
# Uso:
#   ./scripts/deploy.sh                build + push + deploy (ciclo completo)
#   ./scripts/deploy.sh --skip-build   só redeploy do stack (sem build/push/pull)
#
# Pré-requisitos na VPS (nó manager do Swarm), no diretório do projeto:
#   - arquivo .env preenchido (DEBUG=False; ALLOWED_HOSTS com localhost p/ healthcheck)
#   - secret do Cloudflare:  printf '<TOKEN>' | docker secret create CLOUDFLARE_DNS_API_TOKEN -
#   - rede externa:          docker network create --driver overlay --attachable traefik_public
#   - login no GHCR (ou exporte GITHUB_TOKEN com scope write:packages para login automático)

REGISTRY="ghcr.io/pycodebr"
IMAGE="$REGISTRY/scsi"
STACK_NAME="scsi"
STACK_FILE="docker-stack.yml"
URL="https://scsi.digital"

# ── Cores ──
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!!]${NC} $1"; }
error() { echo -e "${RED}[ERRO]${NC} $1"; exit 1; }

SKIP_BUILD=0
[ "${1:-}" = "--skip-build" ] && SKIP_BUILD=1

echo "=== SCSI — Deploy ($STACK_NAME) ==="
echo ""

# ── 0. Pré-condições ──
command -v docker >/dev/null 2>&1 || error "Docker não encontrado."
docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null | grep -q active \
    || error "Este nó não está em Swarm ativo (rode: docker swarm init)."

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

# ── 1. Carrega .env (parser seguro: NÃO faz source — valores com & $ * espaços
#       quebrariam o shell — apenas exporta KEY=VALUE literalmente) ──
[ -f .env ] || error "Arquivo .env não encontrado em $REPO_DIR"
echo "--- Carregando .env ---"
while IFS= read -r line || [ -n "$line" ]; do
    line="${line%$'\r'}"
    case "$line" in ''|\#*) continue ;; esac
    [ "${line#*=}" = "$line" ] && continue
    key="${line%%=*}"; value="${line#*=}"
    key="${key#"${key%%[![:space:]]*}"}"; key="${key%"${key##*[![:space:]]}"}"
    case "$key" in ''|*[!A-Za-z0-9_]*) continue ;; esac
    case "$value" in
        \"*\") value="${value#\"}"; value="${value%\"}" ;;
        \'*\') value="${value#\'}"; value="${value%\'}" ;;
    esac
    export "$key=$value"
done < .env
info ".env carregado"

# ── 2. Validações que evitam deploy quebrado ──
echo ""
echo "--- Validações ---"
docker secret inspect CLOUDFLARE_DNS_API_TOKEN >/dev/null 2>&1 \
    || error "Secret 'CLOUDFLARE_DNS_API_TOKEN' ausente. Crie: printf '<TOKEN>' | docker secret create CLOUDFLARE_DNS_API_TOKEN -"
docker network ls --format '{{.Name}}' | grep -qx traefik_public \
    || error "Rede 'traefik_public' ausente. Crie: docker network create --driver overlay --attachable traefik_public"

[ "${DEBUG:-}" = "False" ] || warn "DEBUG não está 'False' (valor atual: '${DEBUG:-<vazio>}') — produção deve usar DEBUG=False."
case ",${ALLOWED_HOSTS:-}," in
    *,localhost,*) : ;;
    *) warn "ALLOWED_HOSTS não contém 'localhost' — o healthcheck do app vai falhar (DisallowedHost)." ;;
esac
info "Validações concluídas"

# ── 3. Build + Push ──
VERSION="$(git rev-parse --short HEAD 2>/dev/null || echo latest)"
if [ "$SKIP_BUILD" -eq 0 ]; then
    echo ""
    echo "--- Atualizando código (git pull) ---"
    BRANCH="$(git branch --show-current 2>/dev/null || echo '')"
    if [ -n "$BRANCH" ]; then
        git pull origin "$BRANCH" || warn "git pull falhou (seguindo com o código atual)."
        VERSION="$(git rev-parse --short HEAD)"
    else
        warn "Sem branch git detectada — pulando git pull."
    fi

    echo ""
    echo "--- Build da imagem ($IMAGE:$VERSION) ---"
    docker build -t "$IMAGE:$VERSION" -t "$IMAGE:latest" .
    info "Imagem construída"

    echo ""
    echo "--- Push para o GHCR ---"
    if ! docker push "$IMAGE:$VERSION"; then
        warn "Push falhou — tentando login no GHCR..."
        [ -n "${GITHUB_TOKEN:-}" ] || error "Defina GITHUB_TOKEN (scope write:packages) ou faça 'docker login ghcr.io'."
        echo "$GITHUB_TOKEN" | docker login ghcr.io -u pycodebr --password-stdin
        docker push "$IMAGE:$VERSION"
    fi
    docker push "$IMAGE:latest"
    info "Imagem enviada: $IMAGE:$VERSION"
else
    warn "--skip-build: pulando git pull, build e push."
fi

# ── 4. Deploy do stack ──
echo ""
echo "--- Deploy do stack ---"
docker stack deploy -c "$STACK_FILE" --with-registry-auth "$STACK_NAME"
info "Stack reconciliada"

# ── 5. Força rollout dos serviços da aplicação (garante a imagem nova) ──
echo ""
echo "--- Rollout dos serviços da aplicação ---"
for svc in app celery_worker celery_beat; do
    docker service update --force "${STACK_NAME}_${svc}" >/dev/null 2>&1 \
        && info "rollout: ${STACK_NAME}_${svc}" \
        || warn "rollout falhou (serviço ainda não existe?): ${STACK_NAME}_${svc}"
done

echo ""
echo "--- Aguardando estabilizar ---"
sleep 10

echo ""
echo "--- Status ---"
docker service ls --format "table {{.Name}}\t{{.Mode}}\t{{.Replicas}}\t{{.Image}}" | grep -E "^NAME|^${STACK_NAME}_" || true

# ── Resultado ──
echo ""
echo "=== Deploy concluído! ==="
echo "  Versão: $VERSION"
echo "  Imagem: $IMAGE:$VERSION"
echo "  URL:    $URL"
echo ""
echo "  Migrations/collectstatic rodam no entrypoint do 'app' (advisory lock)."
echo "  Superusuário (1x):  APP=\$(docker ps --filter name=${STACK_NAME}_app -q | head -1); docker exec -it \$APP python manage.py createsuperuser"
echo "  Logs:               docker service logs -f ${STACK_NAME}_app"
echo "  TLS/Traefik:        docker service logs -f ${STACK_NAME}_traefik"
