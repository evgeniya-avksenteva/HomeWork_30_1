from urllib.parse import urlparse

from django.core.exceptions import ValidationError


def validate_allowed_url(value):
    """
    Проверяет, что в ссылке присутствует домен youtube.com.
    Если ссылка ведет на другой ресурс — вызывает ValidationError.
    """
    parsed_url = urlparse(value)
    domain = parsed_url.netloc.lower()
    # Разрешаем ссылки, где домен содержит 'youtube.com'
    if "youtube.com" not in domain and "youtu.be" not in domain:
        raise ValidationError(
            "Использованы сторонние ресурсы, разрешены только ссылки на youtube.com"
        )
