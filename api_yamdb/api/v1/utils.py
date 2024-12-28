"""Утилиты для работы с email в проекте."""
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator


def send_email(user) -> None:
    """Отправка email с кодом подтверждения."""
    code = default_token_generator.make_token(user)

    subject = 'Ваш код подтверждения'
    message = f'Ваш код: {code}'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
