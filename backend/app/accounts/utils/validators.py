import re

import phonenumbers
from django.conf import settings


def validate_email(email: str) -> bool:
    return re.match(r'.+@.+', email)


def validate_phone(phone_str: str) -> bool:
    num = phonenumbers.parse(phone_str, settings.PHONENUMBER_DEFAULT_REGION)
    return phonenumbers.is_valid_number(num)
