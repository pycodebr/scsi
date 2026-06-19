<#
=============================================================================
 setup_local.ps1  —  Setup de ambiente de desenvolvimento (Windows 10/11)
=============================================================================
 PycodeBR — workflow de IA Assistida (SCSI e qualquer outro projeto)

 O QUE ESTE SCRIPT FAZ (idempotente — pula o que já está instalado):
   1. Verifica/instala o gerenciador de pacotes do Windows (winget)
   2. Habilita o WSL2 (necessário para o Docker Desktop)
   3. Instala Python 3.13                      (se faltar)
   4. Instala Node.js LTS + npm/npx            (se faltar)
   5. Instala Docker Desktop                   (se faltar)
   6. Instala os CLIs de IA:
        - Claude Code  (@anthropic-ai/claude-code)
        - OpenCode     (opencode-ai)
        - Codex CLI    (@openai/codex)
   7. Instala git e ferramentas de apoio
   8. Instala o GitHub CLI (gh) e autentica voce no GitHub
      (fluxo padrao; se falhar, fallback guiado por token)
   9. Cria a pasta do SEU projeto (pergunta onde e qual nome)
  10. Cria a .venv, instala Django, roda 'django-admin startproject core .',
      gera o requirements.txt e o .gitignore
  11. Cria um arquivo .env com as variáveis mais usadas (em branco)
  12. (Opcional) Cria o repositorio no GitHub e faz o "first commit" (gh)

 COMO RODAR (PowerShell COMO ADMINISTRADOR):
   1. Abra o menu Iniciar, digite "PowerShell"
   2. Clique com o botão direito > "Executar como administrador"
   3. Libere a execução do script nesta janela:
        Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
   4. Rode:
        .\scripts\setup_local.ps1

 Em caso de erro, o motivo aparece na tela e um log completo fica em:
   .\setup_local.log
=============================================================================
#>

#Requires -Version 5.1
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

# Libera a execução de scripts .ps1 APENAS nesta sessão (escopo Process: não pede
# admin e não altera nada permanente no sistema). É necessário porque o 'npm' no
# Windows é um 'npm.ps1' e, com a ExecutionPolicy padrão (Restricted), comandos
# como 'npm --version' / 'npm install -g' (e os shims claude/opencode/codex) seriam
# bloqueados com "a execução de scripts foi desabilitada neste sistema".
try { Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force } catch {}

# Evita que o pip escreva o aviso "A new release of pip..." no stderr — que, com
# ErrorActionPreference='Stop', seria interpretado como erro fatal pelo PowerShell.
$env:PIP_DISABLE_PIP_VERSION_CHECK = '1'

$script:LogFile   = Join-Path (Get-Location) 'setup_local.log'
$script:Step      = 0
$script:TotalStep = 13
Set-Content -Path $script:LogFile -Value "[$(Get-Date -Format HH:mm:ss)] Início do setup" -Encoding utf8

# ─────────────────────────────────────────────────────────────────────────────
#  Logging visual e didático
# ─────────────────────────────────────────────────────────────────────────────
function Write-Log { param([string]$Msg) Add-Content -Path $script:LogFile -Value "[$(Get-Date -Format HH:mm:ss)] $Msg" }

function Show-Banner { param([string]$Text)
  Write-Host ""
  Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
  Write-Host ("║ {0,-60} ║" -f $Text) -ForegroundColor Cyan
  Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
}
function Show-Step { param([string]$Text)
  $script:Step++
  Write-Host ""
  Write-Host "▶ ETAPA $($script:Step)/$($script:TotalStep): $Text" -ForegroundColor Blue
  Write-Host "──────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
  Write-Log "ETAPA $($script:Step)/$($script:TotalStep): $Text"
}
function Info    { param([string]$m) Write-Host "  i  $m" -ForegroundColor Blue;   Write-Log "INFO  $m" }
function Ok      { param([string]$m) Write-Host "  OK $m" -ForegroundColor Green;  Write-Log "OK    $m" }
function Warn    { param([string]$m) Write-Host "  !  $m" -ForegroundColor Yellow; Write-Log "WARN  $m" }
function Skip    { param([string]$m) Write-Host "  -  $m (ja instalado - pulando)" -ForegroundColor DarkGray; Write-Log "SKIP  $m" }
function Working { param([string]$m) Write-Host "  .. $m..." -ForegroundColor Cyan; Write-Log "WORK  $m" }

# ─────────────────────────────────────────────────────────────────────────────
#  Saída segura — PAUSA antes de sair para a janela NÃO fechar e sumir o erro
# ─────────────────────────────────────────────────────────────────────────────
function Wait-Key {
  # Só pausa se houver interface interativa (não trava em automação/CI).
  if ([Environment]::UserInteractive) {
    try { Read-Host "`n  >> Pressione ENTER para fechar esta janela" | Out-Null } catch {}
  }
}
function Exit-Script { param([int]$Code = 0) Wait-Key; exit $Code }

# ─────────────────────────────────────────────────────────────────────────────
#  Tratamento de erros
# ─────────────────────────────────────────────────────────────────────────────
function Stop-OnError { param([System.Management.Automation.ErrorRecord]$Err)
  Write-Host ""
  Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Red
  Write-Host "║  ERRO — o script parou                                        ║" -ForegroundColor Red
  Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Red
  Write-Host "  Etapa....: $($script:Step)/$($script:TotalStep)" -ForegroundColor Red
  Write-Host "  Motivo...: $($Err.Exception.Message)" -ForegroundColor Red
  Write-Host "  Linha....: $($Err.InvocationInfo.ScriptLineNumber)" -ForegroundColor Red
  Write-Host "  Comando..: $($Err.InvocationInfo.Line.Trim())" -ForegroundColor Red
  Write-Host ""
  Write-Host "  O que fazer:" -ForegroundColor Yellow
  Write-Host "    1. Leia o 'Motivo' acima."
  Write-Host "    2. Log completo em: $($script:LogFile)"
  Write-Host "    3. Rode o script de novo — ele e idempotente e retoma de onde da."
  Write-Host ""
  Write-Log  "ERRO: $($Err.Exception.Message) | linha $($Err.InvocationInfo.ScriptLineNumber)"
  Write-Log  ($Err | Out-String)
  Wait-Key            # pausa para o usuario LER o erro antes da janela fechar
  exit 1
}

# ─────────────────────────────────────────────────────────────────────────────
#  Utilitários
# ─────────────────────────────────────────────────────────────────────────────
function Test-Cmd { param([string]$Name) [bool](Get-Command $Name -ErrorAction SilentlyContinue) }

# Testa se um módulo Python está instalado SEM disparar erro fatal. Quando o módulo
# NÃO existe, o "import" joga um traceback no stderr; com ErrorActionPreference='Stop'
# isso viraria erro fatal (e o '2>$null' não suprime no PowerShell 5.1). Por isso
# baixamos o ErrorActionPreference só aqui e checamos o código de saída.
function Test-PyModule {
  param([string]$Module)
  $prev = $ErrorActionPreference
  $ErrorActionPreference = 'SilentlyContinue'
  try {
    & python -c "import $Module" 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
  } finally { $ErrorActionPreference = $prev }
}

function Update-Path {
  # Recarrega o PATH (Máquina + Usuário) para enxergar o que acabou de ser instalado
  $env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' +
              [System.Environment]::GetEnvironmentVariable('Path','User')
}

function Invoke-Retry { param([scriptblock]$Action, [int]$Max = 3, [int]$Delay = 3)
  for ($i = 1; $i -le $Max; $i++) {
    try { & $Action; return $true }
    catch {
      if ($i -ge $Max) { throw }
      Warn "Tentativa $i/$Max falhou. Nova tentativa em ${Delay}s..."
      Start-Sleep -Seconds $Delay; $Delay *= 2
    }
  }
}

function Confirm-SN { param([string]$Prompt)
  while ($true) {
    $a = Read-Host "  ? $Prompt [S/N]"
    switch -Regex ($a.ToUpper()) {
      '^(S|SIM)$'     { return $true }
      '^(N|NAO|NÃO)$' { return $false }
      default         { Warn "Responda com S (sim) ou N (nao)." }
    }
  }
}

# Instala um pacote via winget de forma idempotente, verificando o comando alvo
function Install-Winget { param([string]$Id, [string]$CheckCmd, [string]$Label)
  if ($CheckCmd -and (Test-Cmd $CheckCmd)) { Skip $Label; return }
  Working "Instalando $Label ($Id)"
  Invoke-Retry { winget install --id $Id -e --silent --accept-package-agreements --accept-source-agreements 2>&1 | Add-Content $script:LogFile } | Out-Null
  Update-Path
  Ok "$Label instalado"
}

# Roda um comando nativo (git, gh, ...) gravando TODA a saída (incluindo stderr) no
# log, SEM deixar que avisos no stderr virem erro fatal. Isso é necessário porque o
# 'git' emite avisos no stderr (ex.: "LF will be replaced by CRLF...") e, com
# ErrorActionPreference='Stop' + '2>&1', o PowerShell trataria isso como erro
# terminante (NativeCommandError) e o trap pararia o script. Mesmo padrão já usado
# em Test-PyModule. O código de saída real fica em $LASTEXITCODE para checagem.
function Invoke-Logged {
  param([Parameter(Mandatory)][scriptblock]$Action)
  $prev = $ErrorActionPreference
  $ErrorActionPreference = 'SilentlyContinue'
  try { & $Action 2>&1 | Add-Content $script:LogFile } finally { $ErrorActionPreference = $prev }
}

trap { Stop-OnError $_ }

# =============================================================================
#  ETAPA 0 — Boas-vindas + checagens
# =============================================================================
Show-Banner "SETUP DE AMBIENTE — PycodeBR (Windows)"
Write-Host "  Este script prepara tudo que voce precisa para desenvolver."
Write-Host "  Ele e seguro e idempotente: pode rodar quantas vezes quiser."
Write-Host "  Log completo desta execucao: $($script:LogFile)" -ForegroundColor DarkGray

Show-Step "Verificando pre-requisitos (Administrador + winget)"

# Precisa ser Administrador (WSL e Docker exigem)
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
           ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
  Warn "Este script PRECISA ser executado como Administrador."
  Write-Host "  Feche esta janela, abra o PowerShell com 'Executar como administrador' e rode de novo."
  Exit-Script 1
}
Ok "Rodando como Administrador"

# winget vem com o 'App Installer' da Microsoft Store no Windows 10/11
if (Test-Cmd winget) {
  Ok "winget disponivel ($(winget --version 2>$null))"
} else {
  Warn "winget nao encontrado. Instale o 'App Installer' pela Microsoft Store e rode de novo:"
  Write-Host "    https://apps.microsoft.com/detail/9NBLGGH4NNS1"
  Exit-Script 1
}

# =============================================================================
#  ETAPA 1 — Git + ferramentas de apoio
# =============================================================================
Show-Step "Git e ferramentas de apoio"
Install-Winget -Id 'Git.Git' -CheckCmd 'git' -Label 'Git'

# =============================================================================
#  ETAPA 2 — WSL2 (necessário para o Docker Desktop)
# =============================================================================
Show-Step "WSL2 (necessario para o Docker no Windows)"

$wslOk = $false
try { wsl --status *> $null; if ($LASTEXITCODE -eq 0) { $wslOk = $true } } catch { $wslOk = $false }

if ($wslOk) {
  Skip "WSL2"
} else {
  Working "Habilitando o WSL2 e instalando o Ubuntu (pode pedir REINICIAR)"
  try {
    wsl --install -d Ubuntu 2>&1 | Add-Content $script:LogFile
    Ok "WSL2 habilitado"
    Warn "IMPORTANTE: pode ser necessario REINICIAR o Windows agora."
    Warn "Apos reiniciar, rode este script de novo — ele continua de onde parou."
  } catch {
    Warn "Nao consegui habilitar o WSL automaticamente."
    Warn "Habilite manualmente (Admin): wsl --install   e reinicie o PC."
  }
}

# =============================================================================
#  ETAPA 3 — Python 3.13
# =============================================================================
Show-Step "Python 3.13"
# 'py -3.13' é a forma confiável de detectar uma versão específica no Windows
$pyHas313 = $false
try { & py -3.13 --version *> $null; if ($LASTEXITCODE -eq 0) { $pyHas313 = $true } } catch {}
if ($pyHas313) {
  Skip "Python 3.13 ($(py -3.13 --version 2>&1))"
} else {
  Install-Winget -Id 'Python.Python.3.13' -CheckCmd '' -Label 'Python 3.13'
}
Update-Path

# Resolve um executável de Python utilizável
$PythonExe = $null
foreach ($cand in @('py -3.13','python','python3')) {
  $parts = $cand.Split(' ')
  if (Test-Cmd $parts[0]) { $PythonExe = $cand; break }
}
if (-not $PythonExe) { throw "Python nao ficou disponivel no PATH. Feche e reabra o PowerShell e rode de novo." }
Info "Usando Python: $PythonExe"

# =============================================================================
#  ETAPA 4 — Node.js LTS + npm/npx
# =============================================================================
Show-Step "Node.js LTS + npm/npx"
if ((Test-Cmd node) -and (Test-Cmd npm)) {
  Skip "Node.js ($(node --version)) / npm ($(npm --version))"
} else {
  Install-Winget -Id 'OpenJS.NodeJS.LTS' -CheckCmd '' -Label 'Node.js LTS'
}
Update-Path

# =============================================================================
#  ETAPA 5 — Docker Desktop
# =============================================================================
Show-Step "Docker Desktop"
if (Test-Cmd docker) {
  Skip "Docker ($(docker --version 2>$null))"
} else {
  Install-Winget -Id 'Docker.DockerDesktop' -CheckCmd '' -Label 'Docker Desktop'
  Warn "Abra o 'Docker Desktop' uma vez para concluir a configuracao."
  Warn "Ele usara o WSL2 como backend. Confirme depois com: docker run hello-world"
}

# =============================================================================
#  ETAPA 6 — CLIs de IA (Claude Code, OpenCode, Codex)
# =============================================================================
Show-Step "CLIs de IA (Claude Code · OpenCode · Codex)"
function Install-NpmCli { param([string]$Bin,[string]$Pkg,[string]$Label)
  if (Test-Cmd $Bin) { Skip $Label; return }
  Working "Instalando $Label ($Pkg)"
  try {
    Invoke-Retry { npm install -g $Pkg 2>&1 | Add-Content $script:LogFile } | Out-Null
    Update-Path
    Ok "$Label instalado"
  } catch {
    Warn "Nao consegui instalar $Label. Instale depois com: npm i -g $Pkg"
  }
}
if (Test-Cmd npm) {
  Install-NpmCli -Bin 'claude'   -Pkg '@anthropic-ai/claude-code' -Label 'Claude Code CLI'
  Install-NpmCli -Bin 'opencode' -Pkg 'opencode-ai'               -Label 'OpenCode CLI'
  Install-NpmCli -Bin 'codex'    -Pkg '@openai/codex'             -Label 'Codex CLI'
} else {
  Warn "npm indisponivel (talvez precise reabrir o PowerShell). Pulei os CLIs de IA."
}

# =============================================================================
#  ETAPA 7 — GitHub CLI (gh) + autenticacao no GitHub
# =============================================================================
Show-Step "GitHub CLI (gh) + autenticacao no GitHub"

# Instala o gh (CLI oficial do GitHub) via winget, de forma idempotente
Install-Winget -Id 'GitHub.cli' -CheckCmd 'gh' -Label 'GitHub CLI (gh)'

# Fallback de autenticacao: guia o usuario a gerar e COLAR um token de acesso.
# Usado quando o 'gh auth login' padrao nao da certo. Retorna $true se autenticou.
function Invoke-GhTokenLogin {
  Write-Host ""
  Info "Vamos autenticar pelo metodo do token de acesso."
  Info "E como uma senha temporaria que autoriza este computador a enviar seu projeto."
  Write-Host ""
  Info "Passo a passo (faca no seu navegador, pode ser no celular):"
  Info "  1. Faca login na sua conta em https://github.com"
  Info "  2. Abra este link, que ja vem com tudo pre-preenchido:"
  Info "       https://github.com/settings/tokens/new?scopes=repo,workflow&description=Setup%20PycodeBR"
  Info "  3. Em Expiration escolha um prazo (ex.: 30 days)."
  Info "  4. Os escopos 'repo' e 'workflow' ja vem marcados — deixe assim."
  Info "  5. Desca e clique no botao verde 'Generate token'."
  Info "  6. Copie o codigo gerado (comeca com ghp_...)."
  Info "     Atencao: o GitHub so mostra esse codigo UMA vez."
  Write-Host ""
  Info "Cole o token abaixo e tecle ENTER (por seguranca ele nao aparece na tela)."
  $sec = Read-Host "  Cole seu token do GitHub" -AsSecureString
  $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
  $ghPat = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
  [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
  if ([string]::IsNullOrWhiteSpace($ghPat)) {
    Warn "Nenhum token informado. Pulando a autenticacao por enquanto."
    Warn "Quando tiver o token, rode na pasta: gh auth login --with-token"
    return $false
  }
  Working "Autenticando no GitHub com o token"
  $ghToken = $ghPat.Trim()
  Invoke-Logged { $ghToken | gh auth login --with-token }
  $ghPat = $null; $ghToken = $null
  $ghOk = $false
  try { gh auth status *> $null; if ($LASTEXITCODE -eq 0) { $ghOk = $true } } catch {}
  if ($ghOk) {
    $ghUser = (gh api user --jq .login 2>$null)
    if ($ghUser) { Ok "Autenticado no GitHub como @$ghUser" } else { Ok "Autenticado no GitHub" }
    return $true
  }
  Warn "O token nao foi aceito (pode estar incompleto, expirado ou sem o escopo 'repo')."
  Warn "Gere um novo no link acima e rode: gh auth login --with-token"
  return $false
}

# Autentica voce no GitHub — pula se ja estiver autenticado.
# 1) tenta o fluxo padrao do gh (navegador/dispositivo);
# 2) se falhar, cai no fallback guiado por token (Invoke-GhTokenLogin).
if (Test-Cmd gh) {
  $ghAuthed = $false
  try { gh auth status *> $null; if ($LASTEXITCODE -eq 0) { $ghAuthed = $true } } catch {}
  if ($ghAuthed) {
    Skip "Autenticacao no GitHub (gh ja autenticado)"
  } elseif ($env:GH_TOKEN -or $env:GITHUB_TOKEN) {
    Skip "Autenticacao no GitHub (usando token da variavel de ambiente)"
  } else {
    Info "Vamos conectar voce ao GitHub (necessario para enviar o projeto)."
    Info "A seguir o GitHub CLI faz algumas perguntas em ingles. Responda assim:"
    Info "  - What account do you want to log into?           -> escolha GitHub.com"
    Info "  - What is your preferred protocol...?             -> escolha HTTPS"
    Info "  - Authenticate Git with your GitHub credentials?  -> Yes (Sim)"
    Info "  - How would you like to authenticate...?          -> Login with a web browser (pelo navegador)"
    Info "  - Ele mostra um codigo (ex.: ABCD-1234); copie, tecle ENTER, cole no navegador e autorize."
    Info "  (Use as setas para navegar e ENTER para escolher. Se nao conseguir, seguimos pelo token.)"
    try { gh auth login } catch {}
    $ghOk = $false
    try { gh auth status *> $null; if ($LASTEXITCODE -eq 0) { $ghOk = $true } } catch {}
    if ($ghOk) {
      $ghUser = (gh api user --jq .login 2>$null)
      if ($ghUser) { Ok "Autenticado no GitHub como @$ghUser" } else { Ok "Autenticado no GitHub" }
    } else {
      Warn "A autenticacao padrao nao foi concluida. Vamos tentar pelo token."
      [void](Invoke-GhTokenLogin)
    }
  }
} else {
  Warn "gh indisponivel — a autenticacao no GitHub sera pulada."
}

# =============================================================================
#  ETAPA 8 — Dados do projeto (onde e qual nome)
# =============================================================================
Show-Step "Dados do seu projeto"
Write-Host "  Agora vamos criar a pasta do seu projeto."
Write-Host ""

$DefaultDir = Join-Path $env:USERPROFILE 'projects'
$BaseDir = Read-Host "  Onde deseja criar a pasta do seu projeto? [$DefaultDir]"
if ([string]::IsNullOrWhiteSpace($BaseDir)) { $BaseDir = $DefaultDir }

while ($true) {
  $ProjectName = Read-Host "  Qual o nome do projeto? (nao use espacos)"
  if ([string]::IsNullOrWhiteSpace($ProjectName)) { Warn "O nome nao pode ser vazio." }
  elseif ($ProjectName -match '\s') { Warn "O nome nao pode ter espacos. Use _ ou - (ex: scsi_v1)." }
  elseif ($ProjectName -notmatch '^[A-Za-z0-9._-]+$') { Warn "Use apenas letras, numeros, ponto, hifen ou underline." }
  else { break }
}
$ProjectDir = Join-Path $BaseDir $ProjectName
Info "Caminho do projeto: $ProjectDir"

# =============================================================================
#  ETAPA 9 — Criação da pasta (com checagem de pasta existente)
# =============================================================================
Show-Step "Criando a pasta do projeto"
if (Test-Path $ProjectDir) {
  Warn "A pasta '$ProjectDir' JA EXISTE."
  if ((Get-ChildItem -Force $ProjectDir | Measure-Object).Count -gt 0) {
    Warn "E ela NAO esta vazia. Criar o projeto aqui pode sobrescrever arquivos."
  }
  if (Confirm-SN "Deseja MESMO continuar usando esta pasta existente?") {
    Ok "Ok, continuando na pasta existente."
  } else {
    Info "Operacao cancelada. Rode o script de novo com outro caminho/nome."
    Exit-Script 0
  }
} else {
  Working "Criando $ProjectDir"
  New-Item -ItemType Directory -Path $ProjectDir -Force | Out-Null
  Ok "Pasta criada"
}
Set-Location $ProjectDir

# =============================================================================
#  ETAPA 10 — .venv + Django + startproject + requirements.txt + .gitignore
# =============================================================================
Show-Step "Ambiente Python do projeto (.venv + Django)"

if (Test-Path ".venv") {
  Skip ".venv ja existe"
} else {
  Working "Criando ambiente virtual (.venv)"
  $pyParts = $PythonExe.Split(' ')
  if ($pyParts.Length -gt 1) {
    & $pyParts[0] $pyParts[1..($pyParts.Length-1)] -m venv .venv
  } else {
    & $pyParts[0] -m venv .venv
  }
  Ok ".venv criada"
}

# Ativa a venv nesta sessão
$Activate = Join-Path $ProjectDir ".venv\Scripts\Activate.ps1"
. $Activate
Ok "Ambiente virtual ativado ($(python --version 2>&1))"

Working "Atualizando pip"
Invoke-Retry { python -m pip install --upgrade pip 2>&1 | Add-Content $script:LogFile } | Out-Null
Ok "pip atualizado"

if (Test-PyModule 'django') {
  Skip "Django ($(python -c 'import django; print(django.get_version())'))"
} else {
  Working "Instalando Django"
  Invoke-Retry { pip install Django 2>&1 | Add-Content $script:LogFile } | Out-Null
  Ok "Django instalado ($(python -c 'import django; print(django.get_version())'))"
}

if (Test-Path "manage.py") {
  Skip "Projeto Django ja existe (manage.py encontrado)"
} else {
  Working "Criando projeto Django: django-admin startproject core ."
  django-admin startproject core .
  Ok "Projeto 'core' criado"
}

Working "Gerando requirements.txt (pip freeze)"
$prevEAP = $ErrorActionPreference; $ErrorActionPreference = 'SilentlyContinue'
pip freeze 2>$null | Out-File -Encoding utf8 requirements.txt
$ErrorActionPreference = $prevEAP
Ok "requirements.txt gerado"

# Cria o .gitignore do projeto (mesmo conteudo do projeto SCSI v1)
if (Test-Path ".gitignore") {
  Skip ".gitignore ja existe (nao foi sobrescrito)"
} else {
  Working "Criando .gitignore"
  $gitignoreContent = @'
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
'@
  Set-Content -Path ".gitignore" -Value $gitignoreContent -Encoding utf8
  Ok ".gitignore criado (mesmo padrao do projeto SCSI v1)"
}

# =============================================================================
#  ETAPA 11 — .env com as variáveis mais usadas (em branco)
# =============================================================================
Show-Step "Arquivo .env (variaveis de ambiente)"
if (Test-Path ".env") {
  Skip ".env ja existe (nao foi sobrescrito)"
} else {
  Working "Criando .env modelo"
  $envContent = @'
# =============================================================================
#  .env — variaveis de ambiente do projeto (PREENCHA antes de rodar)
#  Nunca versione este arquivo com segredos reais (mantenha no .gitignore).
# =============================================================================

# --- Django ---
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# --- Localizacao ---
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
'@
  Set-Content -Path ".env" -Value $envContent -Encoding utf8
  Ok ".env criado (variaveis em branco, prontas para preencher)"
}

# =============================================================================
#  ETAPA 12 — Enviar o projeto para o GitHub (opcional)
# =============================================================================
Show-Step "Enviar o projeto para o GitHub (opcional)"

$ghReady = $false
if (Test-Cmd gh) { try { gh auth status *> $null; if ($LASTEXITCODE -eq 0) { $ghReady = $true } } catch {} }

if (-not (Test-Cmd gh)) {
  Warn "gh nao esta disponivel — pulando o envio ao GitHub."
  Warn "Instale em https://cli.github.com e depois rode 'gh repo create' na pasta."
} elseif (-not $ghReady) {
  Warn "Voce nao esta autenticado no GitHub. Pulando o envio."
  Warn "Rode 'gh auth login' e depois 'gh repo create' dentro da pasta do projeto."
} elseif (Confirm-SN "Deseja enviar este projeto para o GitHub agora?") {
  # Nome do repositorio — sugere o nome da pasta do projeto como padrao
  $RepoName = Read-Host "  ? Nome do repositorio no GitHub [$ProjectName]"
  if ([string]::IsNullOrWhiteSpace($RepoName)) { $RepoName = $ProjectName }

  # Visibilidade: publico ou privado
  if (Confirm-SN "O repositorio deve ser PUBLICO? (responda N para PRIVADO)") {
    $Visibility = '--public'
  } else {
    $Visibility = '--private'
  }

  # Inicializa o repositorio git (se ainda nao houver)
  if (-not (Test-Path ".git")) {
    Working "Inicializando repositorio git"
    Invoke-Logged { git init -b main }
  }

  # Garante uma identidade git (usa os dados da sua conta do GitHub se faltar)
  $hasEmail = $false
  try { if (git config user.email)          { $hasEmail = $true } } catch {}
  if (-not $hasEmail) { try { if (git config --global user.email) { $hasEmail = $true } } catch {} }
  if (-not $hasEmail) {
    $ghLogin = (gh api user --jq .login 2>$null)
    $ghName  = (gh api user --jq '.name // .login' 2>$null)
    if ($ghLogin) {
      git config user.name  "$ghName"
      git config user.email "$ghLogin@users.noreply.github.com"
    }
  }

  Working "Criando o primeiro commit ('first commit')"
  Invoke-Logged { git add -A }
  Invoke-Logged { git commit -m "first commit" }

  Working "Criando o repositorio no GitHub e enviando (gh repo create)"
  Invoke-Logged { gh repo create $RepoName $Visibility --source=. --remote=origin --push }
  if ($LASTEXITCODE -eq 0) {
    Ok "Projeto enviado ao GitHub"
  } else {
    Warn "Nao consegui criar/enviar o repositorio. Veja o log: $($script:LogFile)"
    Warn "Talvez o nome '$RepoName' ja exista na sua conta — tente outro com 'gh repo create'."
  }
} else {
  Info "Ok! O projeto nao foi enviado ao GitHub."
  Info "Quando quiser, dentro da pasta rode: gh repo create"
}

# =============================================================================
#  FIM — Resumo + próximos passos
# =============================================================================
Show-Banner "TUDO PRONTO!"
Write-Host "  Seu ambiente e seu projeto estao configurados."
Write-Host ""
Write-Host "  Resumo:"
Write-Host "    * Projeto.: $ProjectDir"
Write-Host "    * Python..: $(python --version 2>&1)"
if (Test-Cmd node)   { Write-Host "    * Node....: $(node --version)" }
if (Test-Cmd docker) { Write-Host "    * Docker..: $(docker --version 2>$null)" }
Write-Host ""
Write-Host "  Proximos passos:"
Write-Host "    1. cd $ProjectDir"
Write-Host "    2. .\.venv\Scripts\Activate.ps1     # ativar o ambiente"
Write-Host "    3. python manage.py runserver       # testar o Django"
Write-Host "    4. Preencha o arquivo .env com seus valores"
Write-Host "    5. Abra seu CLI de IA na pasta: claude (ou opencode / codex)"
Write-Host ""
Warn "Se voce acabou de habilitar o WSL2/Docker, talvez precise REINICIAR o Windows."
Write-Log "CONCLUIDO com sucesso — projeto em $ProjectDir"
Wait-Key   # mantem a janela aberta para o usuario ler o resumo
