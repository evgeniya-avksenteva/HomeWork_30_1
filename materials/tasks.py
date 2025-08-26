from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_course_update_email(user_email, course_title):
    subject = f"Обновление курса: {course_title}"
    message = f"Здравствуйте! В курсе '{course_title}' появились новые материалы. Заходите и изучайте!"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)
