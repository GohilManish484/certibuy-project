from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Create a test inspector user'

    def handle(self, *args, **options):
        if not User.objects.filter(username='inspector1').exists():
            inspector = User.objects.create_user(
                username='inspector1',
                email='inspector@certibuy.com',
                password='inspector123',
                first_name='John',
                last_name='Inspector',
                role='inspector'
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created inspector user: {inspector.username}'))
        else:
            self.stdout.write(self.style.WARNING('Inspector user already exists'))
