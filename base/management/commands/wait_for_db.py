"""Management command que aguarda o banco de dados ficar disponível.

Usado no entrypoint dos containers (app, celery) antes de rodar migrations ou
iniciar workers. O Docker Swarm ignora ``depends_on`` em runtime, então este
comando garante que o serviço só prossiga quando o Postgres estiver aceitando
conexões — evitando os erros de "failed to resolve host 'db'" / connection
refused durante a subida do stack.
"""
import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Aguarda o banco de dados padrão aceitar conexões.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Tempo máximo de espera em segundos (default: 60).',
        )
        parser.add_argument(
            '--interval',
            type=float,
            default=2.0,
            help='Intervalo entre tentativas em segundos (default: 2).',
        )

    def handle(self, *args, **options):
        timeout = options['timeout']
        interval = options['interval']
        deadline = time.monotonic() + timeout

        self.stdout.write('Aguardando o banco de dados...')
        while True:
            try:
                connections['default'].cursor()
            except OperationalError as exc:
                if time.monotonic() >= deadline:
                    self.stderr.write(
                        self.style.ERROR(
                            f'Banco indisponível após {timeout}s: {exc}'
                        )
                    )
                    raise SystemExit(1)
                self.stdout.write('  banco indisponível, tentando novamente...')
                time.sleep(interval)
            else:
                self.stdout.write(self.style.SUCCESS('Banco disponível!'))
                return
