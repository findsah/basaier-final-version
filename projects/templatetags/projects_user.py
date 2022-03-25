from django import template
from projects.models import Donate
import decimal

register = template.Library()


@register.filter(name='usersFund')
def usersFund(project, user):
    donations = Donate.objects.filter(
        project=project, transaction__status="Approved",
        user=user)
    total_funded = decimal.Decimal('0.000')
    for d in donations:
        total_funded += d.amount
    return total_funded
