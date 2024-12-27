"""Утилиты для работы с email в проекте."""

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail


def send_email(user, code=None) -> None:
    """Отправка email с кодом подтверждения."""
    if code is None:
        code = default_token_generator.make_token(user)
        user.confirmation_code = code
        user.save()

    subject = 'Ваш код подтверждения'
    message = f'Ваш код: {code}'

    send_mail(
        subject,
        message,
        'admin@yamdb.com',
        [user.email],
        fail_silently=False,
    )
