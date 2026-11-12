"""
Security and safe template interpolation for ReportForge.
Strictly disallows arbitrary code execution and restricts filesystem access.
"""

from __future__ import annotations
import re
from pathlib import Path
from typing import Any, Dict, Optional
from ..core.exceptions import SecurityError


# Matches expressions like {{ customer.name }} or {{ invoice_id | uppercase }}
VAR_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_.]+)(?:\s*\|\s*([a-zA-Z0-9_:]+))?\s*\}\}")


def get_nested_value(data: Dict[str, Any], path: str) -> Any:
    """
    Safely retrieves a value from a nested dictionary using dot notation (e.g. 'order.customer.name').
    Never executes expressions or accesses private attributes (__...).
    """
    if not path or not isinstance(data, dict):
        return None

    keys = path.split(".")
    current: Any = data

    for key in keys:
        if key.startswith("_"):
            # Block access to private Python attributes (__class__, etc.)
            raise SecurityError(f"Access to private attribute '{key}' is forbidden.")

        if isinstance(current, dict):
            current = current.get(key)
        elif isinstance(current, (list, tuple)):
            try:
                idx = int(key)
                current = current[idx]
            except (ValueError, IndexError):
                return None
        else:
            return None

        if current is None:
            return None

    return current


def interpolate_text(text: str, data: Dict[str, Any]) -> str:
    """
    Replaces {{ path }} expressions in text with corresponding values from the data context.
    Optionally applies simple format filters like {{ total | currency }}.
    """
    if not text or "{{" not in text:
        return text

    from .formatters import apply_formatter

    def replace_match(match: re.Match) -> str:
        var_path = match.group(1).strip()
        filter_name = match.group(2).strip() if match.group(2) else None

        val = get_nested_value(data, var_path)
        if val is None:
            return ""

        if filter_name:
            return apply_formatter(val, filter_name)
        return str(val)

    return VAR_PATTERN.sub(replace_match, text)


def validate_safe_path(requested_path: str, allowed_base_dir: Optional[str] = None) -> Path:
    """
    Validates that a requested file path does not escape the allowed base directory.
    Protects against directory traversal attacks (e.g. ../../etc/passwd).
    """
    if ".." in requested_path:
        raise SecurityError(f"Path traversal detected in path: {requested_path}")

    p = Path(requested_path)
    if p.is_absolute() and allowed_base_dir is None:
        raise SecurityError(f"Absolute paths not permitted in templates: {requested_path}")

    if allowed_base_dir:
        base = Path(allowed_base_dir).resolve()
        resolved = (base / requested_path).resolve()
        try:
            resolved.relative_to(base)
        except ValueError:
            raise SecurityError(f"Access to path outside base directory forbidden: {requested_path}")
        return resolved

    return p
