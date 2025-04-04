from datetime import datetime
from decimal import Decimal, InvalidOperation


def validate_date(date_string: str) -> bool:
    try:
        datetime.strptime(date_string, "%d.%m.%Y")
        return True
    except ValueError:
        return False


def validate_amount(amount_string: str) -> bool:
    try:
        value = Decimal(amount_string)
        return value >= 0
    except InvalidOperation:
        return False
