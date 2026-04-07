from django.core.management.base import BaseCommand

from core.services import RoleService


class Command(BaseCommand):
    help = 'Crea o actualiza semillas de roles del sistema ERP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--extended',
            action='store_true',
            help='Incluye roles extendidos por dominio ademas de los estandar',
        )

    def handle(self, *args, **options):
        include_extended = options.get('extended', False)
        if include_extended:
            result = RoleService.create_default_roles(include_extended=True)
            self.stdout.write(self.style.SUCCESS('Roles estandar + extendidos inicializados correctamente'))
        else:
            result = RoleService.create_standard_roles()
            self.stdout.write(self.style.SUCCESS('Roles estandar inicializados correctamente'))

        self.stdout.write('- Roles estandar: Administrador, Operador, Auditor, Supervisor')
        self.stdout.write(f"- Roles esperados: {result['total_roles']}")
        self.stdout.write(f"- Roles creados: {result['created']}")
        self.stdout.write(f"- Roles actualizados: {result['updated']}")
