import json
from uuid import uuid4

from .openid_provider.flow import FlowMixin as AuthRequestMixin
from .serializable import Container


class BaseFlow:
	class Fields:
		id = None
		next = None


bases = (
	BaseFlow,
	AuthRequestMixin,
)


class Flow(Container, *bases):
	def __init__(self):
		self.id = uuid4().hex
		super().__init__()


class FlowMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		flows = request.session.setdefault('flows', {})

		initial_flow_id = None
		try:
			initial_flow_id = request.GET['flow']
			flow_data = flows[initial_flow_id]
		except KeyError:
			request.flow = None
		else:
			request.flow = Flow.unserialize(json.loads(flow_data))

		resp = self.get_response(request)

		# It's possible that session was flushed in get_response.
		flows = request.session.setdefault('flows', {})

		if initial_flow_id:
			try:
				del flows[initial_flow_id]
			except KeyError:
				pass
			request.session.modified = True

		if request.flow:
			flows[request.flow.id] = json.dumps(request.flow.serialize())
			request.session.modified = True

			if 'Location' in resp:
				if '?' in resp['Location']:
					resp['Location'] += '&flow=' + request.flow.id
				else:
					resp['Location'] += '?flow=' + request.flow.id

		return resp


def flow(request):
	return {
		'flow': request.flow
	}
