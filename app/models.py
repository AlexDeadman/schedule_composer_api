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


class Direction(Model):
    code = CharField(
        max_length=8,
        verbose_name="Код",
        validators=[
            RegexValidator(
                regex=r"^\d{2}\.\d{2}\.\d{2}$",
                message="Wrong format"
            )
        ]
    )
    name = TextField(verbose_name="Название")

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
                message="Wrong format"
            )
        ]
    )
    specialty_code = TextField(verbose_name="Код специальности")
    specialty_name = TextField(verbose_name="Название специальности")
    direction = ForeignKey(Direction, on_delete=CASCADE, verbose_name="Направление")

    def __str__(self):
        return f"{self.year} {self.specialty_name}"

    class Meta:
        verbose_name = "Учебный план"
        verbose_name_plural = "Учебные планы"


class Discipline(Model):
    name = TextField(verbose_name="Название")
    code = TextField(verbose_name="Код")
    syllabus = ForeignKey(Syllabus, on_delete=CASCADE, verbose_name="Учебный план")
    cycle = TextField(verbose_name="Цикл")

    hours_total = SmallIntegerField(verbose_name="Всего часов", validators=[gte_zero])
    hours_lec = SmallIntegerField(verbose_name="Лек.", validators=[gte_zero], null=True, blank=True)
    hours_pr = SmallIntegerField(verbose_name="Прак.", validators=[gte_zero], null=True, blank=True)
    hours_la = SmallIntegerField(verbose_name="Лаб.", validators=[gte_zero], null=True, blank=True)
    hours_isw = SmallIntegerField(verbose_name="СРС", validators=[gte_zero], null=True, blank=True)
    hours_cons = SmallIntegerField(verbose_name="Конс.", validators=[gte_zero], null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"


class Lecturer(Model):
    first_name = TextField(verbose_name="Имя")
    surname = TextField(verbose_name="Фамилия")
    patronymic = TextField(null=True, blank=True, verbose_name="Отчество")
    disciplines = ManyToManyField(Discipline, verbose_name="Дисциплины")

    def __str__(self):
        return f"{self.surname} {self.first_name} {self.patronymic or ''}"

    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"


class Group(Model):
    number = CharField(
        max_length=5,
        verbose_name="Номер",
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Zа-яА-ЯёЁ]{1}\d{4}$",
                message="Wrong format"
            )
        ]
    )
    students_count = IntegerField(verbose_name="Количество студентов", validators=[gte_zero])
    syllabus = ForeignKey(Syllabus, on_delete=CASCADE, verbose_name="Учебный план")

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Classroom(Model):
    number = CharField(
        max_length=3,
        verbose_name="Номер",
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{3}$",
                message="Wrong format"
            )
        ]
    )
    type = TextField(null=True, blank=True, verbose_name="Тип аудитории")
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

LECTURE_BEGIN = (
    (1, '8:20'),
    (2, '10:00'),
    (3, '11:40'),
    (4, '13:30'),
    (5, '15:20'),
    (6, '17:00'),
)

LECTURE_TYPE = (
    (1, 'Лек.'),
    (2, 'Лаб.'),
    (3, 'Прак.'),
    (4, 'СРС'),
)


class Schedule(Model):
    lecturer = ForeignKey(Lecturer, on_delete=CASCADE, verbose_name="Преподаватель")
    discipline = ForeignKey(Discipline, on_delete=CASCADE, verbose_name="Дисциплина")
    group = ForeignKey(Group, on_delete=CASCADE, verbose_name="Группа")
    classroom = ForeignKey(Classroom, on_delete=CASCADE, verbose_name="Аудитория")
    lecture_type = SmallIntegerField(choices=LECTURE_TYPE, verbose_name="Тип занятия")

    semester = SmallIntegerField(verbose_name="Семестр", validators=[gt_zero])
    week_parity = BooleanField(verbose_name="Неделя чёт/нечёт")
    day_of_the_week = SmallIntegerField(choices=DAYS_OF_WEEK, verbose_name="День недели")
    lecture_begin = SmallIntegerField(choices=LECTURE_BEGIN, verbose_name="Начало пары")

    def __str__(self):
        return f"Семестр: {self.semester} Группа: {self.group} День: {self.day_of_the_week} Пара: {self.lecture_begin}"

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписание"
