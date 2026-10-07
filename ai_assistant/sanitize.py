import re

_SECRET_PATTERN = re.compile(
    r"""(?i)\b(username|user[_ -]?name|password|passwd|secret|token|api[_-]?key|authorization)\b"""
    r"""(\s*[:=]\s*)(?:"[^"]*"|'[^']*'|[^\s,;]+)"""
)
_BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_SSN_PATTERN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
_PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)"
)
_INPUT_VALUE_PATTERN = re.compile(
    r"""(?is)(<input\b[^>]*?\bvalue\s*=\s*)(?:"[^"]*"|'[^']*'|[^\s>]+)"""
)


def sanitize_text(text: str, *, limit: int = 12_000) -> str:
    sanitized = _SECRET_PATTERN.sub(r"\1\2[REDACTED]", text)
    sanitized = _BEARER_PATTERN.sub("Bearer [REDACTED]", sanitized)
    sanitized = _EMAIL_PATTERN.sub("[EMAIL REDACTED]", sanitized)
    sanitized = _SSN_PATTERN.sub("[SSN REDACTED]", sanitized)
    sanitized = _PHONE_PATTERN.sub("[PHONE REDACTED]", sanitized)
    return sanitized[:limit]


def sanitize_dom(text: str, *, limit: int = 12_000) -> str:
    without_form_values = _INPUT_VALUE_PATTERN.sub(r'\1"[REDACTED]"', text)
    return sanitize_text(without_form_values, limit=limit)
