from django import template


register = template.Library()


@register.filter(name='has_like')
def has_like(value, user_id):
    if value.likes.filter(id=user_id):
        return True
    else:
        return False
