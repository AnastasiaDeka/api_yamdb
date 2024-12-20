import uuid
from django.core.mail import send_mail
from django.contrib.auth.models import User
from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

def send_email(user, email_type='confirmation', activation_link=None):
    """Функция для отправки email с кодом подтверждения или ссылкой активации."""
    
    if email_type == 'confirmation':
        if not user.confirmation_code:
            user.confirmation_code = str(uuid.uuid4())  # Генерация кода
        user.save()  # Обязательно сохраняем пользователя
        
        subject = 'Ваш код подтверждения'
        message = f'Ваш код: {user.confirmation_code}'
    
    elif email_type == 'activation':
        activation_token = serializer.dumps({'username': user.username}, salt='activation')
        activation_link = f'http://your-site.com/activate/{activation_token}/'

        subject = 'Activate your account'
        message = f'Click the link to activate your account: {activation_link}'

    send_mail(
        subject,
        message,
        'admin@yamdb.com',
        [user.email],
        fail_silently=False,
    )
