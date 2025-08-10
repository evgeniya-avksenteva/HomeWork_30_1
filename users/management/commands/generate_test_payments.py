from django.core.management.base import BaseCommand
from users.models import Payment
from django.contrib.auth import get_user_model
from materials.models import Course, Lesson
import random
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate test payments'

    def handle(self, *args, **kwargs):
        users = list(User.objects.all())
        courses = list(Course.objects.all())
        lessons = list(Lesson.objects.all())

        for _ in range(10):
            user = random.choice(users)
            course_obj = random.choice(courses) if courses else None
            lesson_obj = random.choice(lessons) if lessons else None

            Payment.objects.create(
                user=user,
                payment_date=datetime.now() - timedelta(days=random.randint(0,30)),
                course=course_obj,
                lesson=lesson_obj,
                amount=random.uniform(50,200),
                payment_method=random.choice(['cash', 'bank_transfer'])
            )
        self.stdout.write("Test payments generated.")
