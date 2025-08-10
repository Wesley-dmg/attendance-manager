from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_checkbox_as_button(field, selected_values):
    is_checked = str(field.data) in selected_values
    checked_class = "active" if is_checked else ""

    html = f"""
    <label class="btn btn-outline-primary w-100 mb-2 {checked_class}">
      {field.tag}
      {field.choice_label}
    </label>
    """
    return mark_safe(html)
