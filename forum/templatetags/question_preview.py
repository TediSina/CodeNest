import re

from django import template


register = template.Library()

_OPENING_BACKTICK_FENCE = re.compile(r'^ {0,3}(`{3,})[^`]*$')
_CLOSING_BACKTICK_FENCE = re.compile(r'^ {0,3}(`{3,})[ \t]*$')


@register.filter
def without_fenced_code(value):
    """Remove backtick-fenced code blocks from a Markdown preview."""
    visible_lines = []
    fence_length = None

    for line in str(value or '').splitlines(keepends=True):
        if fence_length is None:
            opening_fence = _OPENING_BACKTICK_FENCE.match(line.rstrip('\r\n'))
            if opening_fence:
                fence_length = len(opening_fence.group(1))
                continue

            visible_lines.append(line)
            continue

        closing_fence = _CLOSING_BACKTICK_FENCE.match(line.rstrip('\r\n'))
        if closing_fence and len(closing_fence.group(1)) >= fence_length:
            fence_length = None

    return ''.join(visible_lines)
