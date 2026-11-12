"""
Data formatting utilities for ReportForge templates.
Formats numbers, currencies, dates, and percentages safely without code evaluation.
"""

from __future__ import annotations
import datetime
from typing import Any, Optional


def format_currency(
    value: Any, symbol: str = "$", decimals: int = 2, thousands_sep: str = ","
) -> str:
    """Format numeric value as currency: e.g. $1,500.00"""
    try:
        val = float(value)
        formatted = f"{val:,.{decimals}f}"
        if thousands_sep != ",":
            formatted = formatted.replace(",", "_").replace(".", thousands_sep).replace("_", ".")
        return f"{symbol}{formatted}"
    except (ValueError, TypeError):
        return str(value)


def format_number(value: Any, decimals: int = 2) -> str:
    """Format numeric value with thousands separator: e.g. 1,500.00"""
    try:
        val = float(value)
        return f"{val:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value: Any, decimals: int = 1) -> str:
    """Format value as percentage: e.g. 15.5%"""
    try:
        val = float(value)
        # If passed as 0.155, convert to 15.5%
        if 0.0 <= val <= 1.0:
            val = val * 100.0
        return f"{val:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)


def format_date(value: Any, target_format: str = "%d/%m/%Y") -> str:
    """Format ISO date string or datetime object into formatted string."""
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.strftime(target_format)
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y/%m/%d", "%d/%m/%Y"):
            try:
                dt = datetime.datetime.strptime(value.split("Z")[0], fmt)
                return dt.strftime(target_format)
            except ValueError:
                continue
    return str(value)


def apply_formatter(value: Any, format_spec: Optional[str]) -> str:
    """Route value through specified formatter."""
    if format_spec is None or format_spec == "":
        return str(value) if value is not None else ""

    spec = format_spec.strip().lower()
    if spec == "currency":
        return format_currency(value)
    elif spec.startswith("currency:"):
        symbol = format_spec.split(":", 1)[1]
        return format_currency(value, symbol=symbol)
    elif spec == "number":
        return format_number(value)
    elif spec == "percentage" or spec == "percent":
        return format_percentage(value)
    elif spec == "date":
        return format_date(value)
    elif spec.startswith("date:"):
        date_fmt = format_spec.split(":", 1)[1]
        return format_date(value, target_format=date_fmt)
    elif spec == "uppercase":
        return str(value).upper()
    elif spec == "lowercase":
        return str(value).lower()
    return str(value)
