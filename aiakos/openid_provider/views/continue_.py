from django.http import Http404
from django.views.generic import TemplateView


class ContinueView(TemplateView):
	template_name = 'openid_provider/continue.html'

	def dispatch(self, request):
		if not request.flow or not request.flow.auth_request:
			request.flow = None
			raise Http404

		return super().dispatch(request)

	def get(self, request):
		if not request.flow.auth_request.id_hint_valid:
			return super().get(request)

		return self.go(request)

	def post(self, request):
		return self.go(request)

	def go(self, request):
		auth_request = request.flow.auth_request
		request.flow = None
		return auth_request.respond({})
