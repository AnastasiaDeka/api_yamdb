"""Утилиты для работы с email в проекте."""
import uuid
from django.core.mail import send_mail


def send_email(user, email_type='confirmation', code=None) -> None:
    """Отправка email с кодом подтверждения."""
    if email_type == 'confirmation':
        if code is None:
            if not user.confirmation_code:
                user.confirmation_code = str(uuid.uuid4())
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
