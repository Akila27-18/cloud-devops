# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def range_filter(value):
    """Creates a range for the given value."""
    return range(int(value))
