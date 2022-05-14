from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import *


def gte_zero(value):
    if value < 0:
        raise ValidationError(
            _('Should be greater than or equal to zero'),
            params={'value': value},
        )


def gt_zero(value):
    if value < 1:
        raise ValidationError(
            _('Should be greater than zero'),
            params={'value': value},
        )


default_validator = RegexValidator(regex=r"^[a-zA-Zа-яА-ЯёЁ\d\s\(\).-]+$")


class Direction(Model):
    code = CharField(
        max_length=8,
        verbose_name="Код",
        validators=[
            RegexValidator(
                regex=r"^\d{2}\.\d{2}\.\d{2}$",
                message="Wrong format (requires dd.dd.dd)"
            )
        ]
    )
    name = CharField(
        max_length=200,
        verbose_name="Название",
        validators=[default_validator]
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"


class Syllabus(Model):
    year = CharField(
        max_length=9,
        verbose_name="Год",
        validators=[
            RegexValidator(
                regex=r"^\d{4}\/\d{4}$",
                message="Wrong format (requires dddd/dddd)"
            )
        ]
    )
    specialty_code = CharField(
        max_length=100,
        verbose_name="Код специальности",
        validators=[default_validator]
    )
    specialty_name = CharField(
        max_length=200,
        verbose_name="Название специальности",
        validators=[default_validator]
    )
    direction = ForeignKey(Direction, on_delete=CASCADE, verbose_name="Направление")

    def __str__(self):
        return f"{self.year} {self.specialty_name}"

    class Meta:
        verbose_name = "Учебный план"
        verbose_name_plural = "Учебные планы"


class Discipline(Model):
    name = CharField(
        max_length=200,
        verbose_name="Название",
        validators=[default_validator]
    )
    code = CharField(
        max_length=100,
        verbose_name="Код",
        validators=[default_validator]
    )
    syllabus = ForeignKey(Syllabus, on_delete=CASCADE, verbose_name="Учебный план")
    cycle = CharField(
        max_length=50,
        verbose_name="Цикл",
        validators=[default_validator]
    )

    hours_total = SmallIntegerField(verbose_name="Всего часов", validators=[gte_zero])
    hours_lec = SmallIntegerField(verbose_name="Лек.", validators=[gte_zero], null=True)
    hours_pr = SmallIntegerField(verbose_name="Прак.", validators=[gte_zero], null=True)
    hours_la = SmallIntegerField(verbose_name="Лаб.", validators=[gte_zero], null=True)
    hours_isw = SmallIntegerField(verbose_name="СРС", validators=[gte_zero], null=True)
    hours_cons = SmallIntegerField(verbose_name="Конс.", validators=[gte_zero], null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"


class Lecturer(Model):
    name_validator = RegexValidator(regex=r"^[a-zA-Zа-яА-ЯёЁ-]+$")

    first_name = CharField(
        max_length=200,
        verbose_name="Имя",
        validators=[name_validator]
    )
    surname = CharField(
        max_length=200,
        verbose_name="Фамилия",
        validators=[name_validator]
    )
    patronymic = CharField(
        max_length=200,
        null=True,
        verbose_name="Отчество",
        validators=[name_validator]
    )

    def __str__(self):
        return f"{self.surname} {self.first_name} {self.patronymic or ''}"

    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"


class Group(Model):
    number = CharField(max_length=50, verbose_name="Номер", validators=[default_validator])
    students_count = IntegerField(verbose_name="Количество студентов", validators=[gte_zero])
    syllabus = ForeignKey(Syllabus, on_delete=CASCADE, verbose_name="Учебный план")

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Classroom(Model):
    number = CharField(
        max_length=100,
        verbose_name="Номер",
        unique=True,
        validators=[default_validator]
    )
    type = CharField(
        max_length=100,
        null=True,
        verbose_name="Тип аудитории",
        validators=[default_validator]
    )
    seats_count = SmallIntegerField(verbose_name="Количество мест", validators=[gte_zero])

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Аудитория"
        verbose_name_plural = "Аудитории"


DAYS_OF_WEEK = (
    (1, 'Понедельник'),
    (2, 'Вторник'),
    (3, 'Среда'),
    (4, 'Четверг'),
    (5, 'Пятница'),
    (6, 'Суббота'),
)

LECTURE_TYPE = (
    (1, 'Лек.'),
    (2, 'Лаб.'),
    (3, 'Прак.'),
    (4, 'СРС'),
)


class Schedule(Model):
    syllabus = ForeignKey(Syllabus, on_delete=CASCADE, verbose_name="Учебный план")
    semester = SmallIntegerField(verbose_name="Семестр", validators=[gt_zero])

    group = ForeignKey(Group, on_delete=CASCADE, verbose_name="Группа")
    even_week = BooleanField(verbose_name="Чётная неделя")
    week_day = SmallIntegerField(choices=DAYS_OF_WEEK, verbose_name="День недели")
    period = SmallIntegerField(verbose_name="Пара", validators=[gt_zero])

    discipline = ForeignKey(Discipline, on_delete=CASCADE, verbose_name="Дисциплина")
    lecturer = ForeignKey(Lecturer, on_delete=CASCADE, verbose_name="Преподаватель")
    classroom = ForeignKey(Classroom, on_delete=CASCADE, verbose_name="Аудитория")

    type = SmallIntegerField(choices=LECTURE_TYPE, verbose_name="Тип занятия")

    def __str__(self):
        return f"Уч. план: {self.syllabus.pk}, " \
               f"Семестр: {self.semester}, " \
               f"Группа: {self.group}, " \
               f"Чёт. неделя: {self.even_week}, " \
               f"День: {self.week_day}, " \
               f"Пара: {self.period}"

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписание"
