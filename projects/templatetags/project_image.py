from django import template

register = template.Library()


@register.simple_tag
def project_image_tag(project, request, *args):
    return project.get_responsive_image_url(request)
