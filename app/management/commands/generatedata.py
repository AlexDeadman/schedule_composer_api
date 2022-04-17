import random

import faker.providers
from django.core.management import call_command
from django.core.management.base import BaseCommand
from faker import Faker
from ..lists import DISCIPLINES, CLASSROOM_TYPES
from ...models import *


class Provider(faker.providers.BaseProvider):
    def discipline(self):
        return self.random_element(DISCIPLINES)

    def audience_type(self):
        return self.random_element(CLASSROOM_TYPES)


def hours(part_max_hours):
    return random.randint(1, part_max_hours) if random.getrandbits(1) else None


def generate_disciplines(fake):
    for _ in range(len(DISCIPLINES)):
        rand_discipline = fake.unique.discipline()

        hours_total = random.randint(30, 150)
        part_max_hours = int(hours_total / 5)

        Discipline.objects.create(
            name=rand_discipline[0],
            code=rand_discipline[1],
            cycle=rand_discipline[2],
            syllabus_id=Syllabus.objects.first().pk,
            hours_total=hours_total,
            hours_lec=hours(part_max_hours),
            hours_pr=hours(part_max_hours),
            hours_la=hours(part_max_hours),
            hours_isw=hours(part_max_hours),
            hours_cons=hours(part_max_hours),
        )


def generate_lecturers(fake):
    for _ in range(random.randint(15, 25)):

        sex = random.getrandbits(1)

        first = fake.first_name_male() if sex else fake.first_name_female()
        last = fake.last_name_male() if sex else fake.last_name_female()
        patro = fake.middle_name_male() if sex else fake.middle_name_female()

        lecturer = Lecturer.objects.create(
            first_name=first,
            surname=last,
            patronymic=patro if random.getrandbits(1) else None
        )

        for _ in range(random.randint(1, 3)):
            rand_discipline = random.randint(
                Discipline.objects.first().pk,
                Discipline.objects.last().pk
            )
            discipline = Discipline.objects.get(pk=rand_discipline)
            lecturer.disciplines.add(discipline)

        lecturer.save()


def generate_groups(fake):
    for _ in range(random.randint(15, 25)):
        Group.objects.create(
            number=fake.plate_letter() + fake.plate_number_extra(),
            students_count=random.randint(18, 25),
            syllabus_id=Syllabus.objects.first().pk,
        )


def generate_classrooms(fake):
    for _ in range(random.randint(15, 25)):
        Classroom.objects.create(
            number=random.randint(100, 999),
            type=fake.audience_type() if random.getrandbits(1) else None,
            seats_count=random.randint(15, 50),
        )


def generate_schedule():
    for semester in range(1, 9):
        for group in range(Group.objects.first().pk, Group.objects.last().pk):
            for odd_even in range(0, 2):
                for day in range(1, random.randint(4, 7)):
                    for period in range(1, random.randint(3, 7)):

                        rand_discipline = random.randint(
                            Discipline.objects.first().pk,
                            Discipline.objects.last().pk
                        )
                        # TODO выбор преподавателя по конкретной дисциплине
                        rand_lecturer = random.randint(
                            Lecturer.objects.first().pk,
                            Lecturer.objects.last().pk
                        )

                        # TODO выбор аудитории в зависимости от количества студентов
                        rand_classroom = random.randint(
                            Classroom.objects.first().pk,
                            Classroom.objects.last().pk
                        )

                        Schedule.objects.create(
                            lecturer_id=rand_lecturer,
                            discipline_id=rand_discipline,
                            group_id=group,
                            classroom_id=rand_classroom,
                            week_day=day,
                            period=period,
                            type=random.randint(1, 4),
                            semester=semester,
                            even_week=bool(odd_even)
                        )


class Command(BaseCommand):
    help = "Test data generation"

    def handle(self, *args, **options):
        try:
            call_command('wipedata')

            Direction.objects.create(
                code="09.02.07",
                name="Информационные системы и программирование"
            )

            Syllabus.objects.create(
                year="2021/2022",
                specialty_code="11111111",
                specialty_name="Информационные системы и программирование",
                direction_id=Direction.objects.first().pk
            )

            fake = Faker('ru_RU')
            fake.add_provider(Provider)

            generate_disciplines(fake)
            generate_lecturers(fake)
            generate_groups(fake)
            generate_classrooms(fake)
            generate_schedule()

        except Exception as e:
            print(str(e))
