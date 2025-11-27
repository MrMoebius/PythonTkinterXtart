"""
Validadores de datos
"""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Valida un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Valida un teléfono (formato flexible)"""
    # Permite números, espacios, guiones y paréntesis
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    return cleaned.isdigit() and len(cleaned) >= 9


def validate_date(date_str: str) -> bool:
    """Valida una fecha en formato YYYY-MM-DD"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    
    try:
        from datetime import datetime
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_number(value: str, min_value: Optional[float] = None, 
                   max_value: Optional[float] = None) -> bool:
    """Valida un número"""
    try:
        num = float(value)
        if min_value is not None and num < min_value:
            return False
        if max_value is not None and num > max_value:
            return False
        return True
    except ValueError:
        return False


def validate_required(value: str) -> bool:
    """Valida que un campo no esté vacío"""
    return value.strip() != ""

