from datetime import datetime, timezone
import re


def format_date(date_obj):
    return str(date_obj) if date_obj else None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return bool(re.match(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", email or ""))


def sanitize_string(value):
    return value.strip() if value else value


def parse_date(date_string):
    if not date_string:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_string, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def is_valid_color(color):
    return bool(color and len(color) == 7 and color.startswith("#"))


def process_task_data(data, existing_task=None):
    result = {}

    if "title" in data:
        title = (data["title"] or "").strip()
        if not title:
            return None, "Título não pode ser vazio"
        if len(title) < 3 or len(title) > 200:
            return None, "Título deve ter entre 3 e 200 caracteres"
        result["title"] = title

    if "description" in data:
        result["description"] = data["description"]

    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return None, "Status inválido"
        result["status"] = data["status"]

    if "priority" in data:
        try:
            priority = int(data["priority"])
        except (TypeError, ValueError):
            return None, "Prioridade inválida"
        if priority < 1 or priority > 5:
            return None, "Prioridade deve ser entre 1 e 5"
        result["priority"] = priority

    if "due_date" in data:
        if data["due_date"]:
            parsed = parse_date(data["due_date"])
            if not parsed:
                return None, "Data inválida"
            result["due_date"] = parsed
        else:
            result["due_date"] = None

    if "tags" in data:
        tags = data["tags"]
        result["tags"] = ",".join(tags) if isinstance(tags, list) else tags

    return result, None


VALID_STATUSES = ["pending", "in_progress", "done", "cancelled"]
VALID_ROLES = ["user", "admin", "manager"]
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = "#000000"
