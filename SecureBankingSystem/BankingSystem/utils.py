from django.http import HttpResponseRedirect
import urllib


def custom_redirect(url_name, *args, **kwargs):
	from django.core.urlresolvers import reverse
	url = reverse(url_name, args=args)
	params = urllib.urlencode(kwargs)
	return HttpResponseRedirect(url + "?%s" % params)


def do_get(request, param):
	if param in request:
		return request[param]
	return ""


class BankingException(Exception):
	pass
