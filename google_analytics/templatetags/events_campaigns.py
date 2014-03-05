from django import template
from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site

from django.template import Context, loader, Variable


register = template.Library()
Analytics = models.get_model('googleanalytics', 'analytics')


@register.simple_tag
def event_tag(category, action, label):
    t = loader.get_template('google_analytics/event_tag_template.html')
    c = Context({
        'category': category,
        'action': action,
        'label': label,
    })
    return t.render(c)


@register.simple_tag
def campaign_link(obj, *args, **kwargs):
    try:
        url = obj.get_absolute_url()
    except:
        msg = "Could not get absolute url for object"
        raise template.VariableDoesNotExist, msg

    required = ['source', 'medium', 'name']
    required_args = {}
    optional = ['term', 'content']
    optional_args = {}

    for arg in required:
        if kwargs.get(arg):
            required_args[arg] = kwargs.get(arg)
        else:
            required_args[arg] = getattr(
                settings,
                'GOOGLE_ANALYTICS_' + arg.upper(),
                None
            )
            if required_args[arg] is None:
                raise template.VariableDoesNotExist, "Missing " + arg

    # Basic check to see if url already has a query string
    if "?" in url:
        url += "&"
    else:
        url += "?"
    url += "utm_source=%s&amp;utm_medium=%s&amp;utm_campaign=%s" % (
        required_args['source'],
        required_args['medium'],
        required_args['name'],
    )

    for arg in optional:
        if kwargs.get(arg):
            optional_args[arg] = kwargs.get(arg)
        else:
            optional_args[arg] = getattr(
                settings,
                'GOOGLE_ANALYTICS_' + arg.upper(),
                None
            )

    if optional_args.get('term'):
        url += "&utm_term=" + optional_args['term']
    if optional_args.get('content'):
        url += "&utm_content=" + optional_args['content']
    return url
