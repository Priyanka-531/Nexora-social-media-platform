import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def render_hashtags(caption):
    """
    Parses and styles #hashtags in post captions.
    If no hashtags are present in caption, appends relevant default hashtags (#nexora #vivid).
    """
    if not caption:
        caption = ""

    # Styled replacement for hashtags in text
    def replace_tag(match):
        tag = match.group(0)
        return f'<span class="inline-flex items-center text-primary font-bold hover:underline cursor-pointer me-1">{tag}</span>'

    has_hashtag = '#' in caption
    styled_caption = re.sub(r'#\w+', replace_tag, caption)

    # If no hashtags were provided in the caption text, add default relevant hashtag badges
    if not has_hashtag:
        suggested_tags = (
            '<div class="flex flex-wrap gap-1.5 pt-1.5">'
            '<span class="inline-block bg-primary/10 text-primary font-semibold text-xs px-2.5 py-0.5 rounded-full hover:bg-primary/20 transition-colors cursor-pointer">#nexora</span>'
            '<span class="inline-block bg-secondary/10 text-secondary font-semibold text-xs px-2.5 py-0.5 rounded-full hover:bg-secondary/20 transition-colors cursor-pointer">#vivid</span>'
            '<span class="inline-block bg-surface-container text-on-surface-variant font-semibold text-xs px-2.5 py-0.5 rounded-full hover:bg-surface-container-high transition-colors cursor-pointer">#trending</span>'
            '</div>'
        )
        styled_caption += suggested_tags

    return mark_safe(styled_caption)
