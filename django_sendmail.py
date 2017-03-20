from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def render_html(s):
	# TODO interpret h and p, so we'll have correct newlines.
	out = ""
	for line in strip_tags(s.replace('<li>', '- ')).splitlines():
		out += line.strip() + "\n"
	return out

def send_mail(to, template_name, context, site=None, request=None):
	if not site:
		site = get_current_site(request)

	context = dict(
		site_name = site.domain.capitalize(),
		**context
	)
	subject = render_to_string(template_name + '.subject', context).strip().replace("\n", " ")
	html = render_to_string(template_name + '.html', context).strip() + "\n"
	try:
		plain = render_to_string(template_name + '.txt', context).strip() + "\n"
	except TemplateDoesNotExist:
		plain = render_html(html).strip() + "\n"

	return mail.send_mail(subject, plain, settings.DEFAULT_FROM_EMAIL, [to], html_message=html)
