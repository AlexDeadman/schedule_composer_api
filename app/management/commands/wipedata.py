from django.core.management import BaseCommand

from app.models import Direction, Classroom, Lecturer


class Command(BaseCommand):
    help = 'Wipe data'

    def handle(self, *args, **options):
        for model in [Direction, Classroom, Lecturer]:
            model.objects.all().delete()
