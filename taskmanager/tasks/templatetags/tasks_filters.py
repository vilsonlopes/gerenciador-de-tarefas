from django import template
from django.db.models import Count, Case, When, FloatField

register = template.Library()


@register.filter
def percent_complete(tasks):
    if tasks.exists():
        aggregation = tasks.aggregate(total=Count('id'), done=Count(Case(When(status='DONE', then=1))))
        percent_done = (aggregation['done'] / aggregation['total']) * 100
        return percent_done
    else:
        return 0
