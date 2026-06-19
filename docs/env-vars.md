# Variáveis de Ambiente

Todas as credenciais ficam no **`.env`** na raiz do projeto, carregadas pelo `django-environ`. Um **`.env.example`** versionado documenta as chaves (sem valores reais).

## Referência completa

| Variável | Exemplo | Descrição |
|---|---|---|
| `DEBUG` | `False` | Modo debug (False em produção) |
| `SECRET_KEY` | `***` | Chave secreta Django |
| `ALLOWED_HOSTS` | `scsi.digital,www.scsi.digital` | Hosts permitidos (comma-separated) |
| `CSRF_TRUSTED_ORIGINS` | `https://scsi.digital` | Origens confiáveis para CSRF |
| `DATABASE_URL` | `postgres://scsi:senha@db:5432/scsi` | Conexão PostgreSQL |
| `POSTGRES_DB` | `scsi` | Nome do banco PostgreSQL |
| `POSTGRES_USER` | `scsi` | Usuário do banco |
| `POSTGRES_PASSWORD` | `***` | Senha do banco |
| `CELERY_BROKER_URL` | `amqp://scsi:senha@rabbitmq:5672//` | Broker RabbitMQ |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/0` | Result backend Redis |
| `RABBITMQ_DEFAULT_USER` | `scsi` | Usuário RabbitMQ |
| `RABBITMQ_DEFAULT_PASS` | `***` | Senha RabbitMQ |
| `REDIS_URL` | `redis://redis:6379/1` | Cache/locks Redis |
| `OPENAI_API_KEY` | `sk-***` | Chave da API OpenAI |
| `OPENAI_MODEL` | `gpt-4o-mini` | Modelo padrão de IA |
| `EMAIL_HOST` | `smtp.provider.com` | Host SMTP |
| `EMAIL_PORT` | `587` | Porta SMTP |
| `EMAIL_HOST_USER` | `no-reply@scsi.digital` | Usuário SMTP |
| `EMAIL_HOST_PASSWORD` | `***` | Senha SMTP |
| `EMAIL_USE_TLS` | `True` | TLS no e-mail |
| `DEFAULT_FROM_EMAIL` | `SCSI <no-reply@scsi.digital>` | Remetente padrão |
| `TIME_ZONE` | `America/Sao_Paulo` | Fuso horário |
| `LANGUAGE_CODE` | `pt-br` | Idioma padrão |
| `MEDIA_ROOT` | `/app/media` | Raiz da mídia protegida |
| `STATIC_ROOT` | `/app/staticfiles` | Raiz dos estáticos coletados |
| `SECURE_SSL_REDIRECT` | `True` | Força HTTPS em produção |
| `ACME_EMAIL` | `admin@scsi.digital` | E-mail Let's Encrypt (Traefik) |

## Segredos em produção

Em produção (Docker Swarm), os segredos sensíveis podem ser geridos por **Docker secrets** em vez de `.env` em texto plano:

```bash
printf 'minha-secret-key' | docker secret create scsi_secret_key -
printf 'sk-...'          | docker secret create scsi_openai_key  -
```

O `.env` continua existindo para variáveis não sensíveis (DEBUG, TIME_ZONE, etc.).

## Desenvolvimento local

Para rodar localmente sem Docker, basta omitir `DATABASE_URL` para cair no SQLite padrão, ou apontar para um PostgreSQL local.