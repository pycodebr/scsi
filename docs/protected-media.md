# Arquivos Protegidos

## Visão geral

O SCSI **nunca serve arquivos publicamente**. Todos os uploads são armazenados em `/app/media/` e servidos via view autenticada sob o prefixo `/protected-media/`.

## Configuração

```python
# settings.py
MEDIA_URL = '/protected-media/'
MEDIA_ROOT = Path('/app/media')
```

O WhiteNoise serve estáticos, mas **não** mídia. Os arquivos de mídia são servidos por uma view Django que verifica autenticação e permissão por tenant.

## Padrão de path dos uploads

O `Document` usa `FileField` com `upload_to` dinâmico que gera paths no formato:

```
brokerage_<id>/<app>/<uuid>_<filename>
```

Exemplo:
```
/media/brokerage_1/clients/a1b2c3-foto_perfil.jpg
/media/brokerage_5/claims/d4e5f6-boletim_ocorrencia.pdf
```

## GenericForeignKey

O model `Document` usa `GenericForeignKey` (`content_type` + `object_id`) para que qualquer entidade possa ter anexos sem FK explícita:

```python
class Document(TenantAwareModel):
    file = models.FileField(upload_to=tenant_upload_path)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
```

Isso permite anexar documentos a `Client`, `Policy`, `Claim`, etc. sem criar campos de FK em cada model.

## Produção

Em produção (Docker Swarm + Traefik), os arquivos são:

1. Armazenados no volume Docker `media_data` (persistente)
2. Servidos pela view autenticada do Django (não pelo nginx/Traefik diretamente)
3. O Traefik não expõe `/media/` — apenas o app Django serve `/protected-media/`

Isto garante que **somente usuários autenticados e do mesmo tenant** podem acessar arquivos.