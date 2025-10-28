import string
import random
from typing import Any, Dict
from django.core.mail import send_mail
from django.conf import settings

def generate_random_string(length: int = 10) -> str:
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def generate_order_id() -> str:
    return f"AC{generate_random_string(8).upper()}"

def generate_transaction_id() -> str:
    return f"TXN{generate_random_string(10).upper()}"

def send_notification_email(to_email: str, subject: str, message: str) -> bool:
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def format_currency(amount: float, currency: str = "KES") -> str:
    return f"{currency} {amount:,.2f}"

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import radians, cos, sin, asin, sqrt

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    r = 6371  # Radius of earth in kilometers
    return c * r

def validate_phone_number(phone: str) -> bool:
    import re
    pattern = r'^\+254[17]\d{8}$'
    return bool(re.match(pattern, phone))

class APIResponse:
    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200) -> Dict:
        return {
            "success": True,
            "message": message,
            "data": data,
            "status_code": status_code
        }

    @staticmethod
    def error(message: str = "Error", errors: Any = None, status_code: int = 400) -> Dict:
        return {
            "success": False,
            "message": message,
            "errors": errors,
            "status_code": status_code
        }