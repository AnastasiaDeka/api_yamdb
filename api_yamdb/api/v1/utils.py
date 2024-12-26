"""Утилиты для работы с email в проекте."""

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail


def send_email(user, email_type='confirmation', code=None) -> None:
    """Отправка email с кодом подтверждения."""
    if email_type == 'confirmation':
        if code is None:

            token_generator = default_token_generator.make_token(user)
            user.confirmation_code = token_generator
            user.save()
            code = user.confirmation_code

        subject = 'Ваш код подтверждения'
        message = f'Ваш код: {code}'

        send_mail(
            subject,
            message,
            'admin@yamdb.com',
            [user.email],
            fail_silently=False,
        )
