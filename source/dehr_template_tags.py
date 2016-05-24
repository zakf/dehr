# File: dehr_template_tags.py
# 
# Information on custom template tags:
#     https://docs.djangoproject.com/en/1.9/howto/custom-template-tags/
# 
# An old example file of tags that I wrote myself:
#     ~/progs/pts_git/pts/mysite/pts/templatetags/pts_tags.py
# 
# Normally I would use {% load dehr_template_tags %} directly under the 
# {% extends "base.html" %} statement at the top of the file. However, this 
# only works if I am using a Django App and settings.INSTALLED_APPS, but I am 
# not, I am rendering Django templates by hand. As such, the tag loader might 
# be broken. It might not be broken, but I will assume it is broken just in 
# case it breaks with a future release of Django. I will need to load this 
# tag file when I configure the Django Template Engine in build.py.

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def this_is_a_test():
    return "This test is working."


@register.simple_tag
def indent():
    return mark_safe('<div class="indent">')


@register.simple_tag
def endindent():
    return mark_safe('</div> <!-- div.indent -->')
