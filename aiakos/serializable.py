from functools import partial, wraps
from itertools import chain


def fields(Cls):
	return {k: type for k, type in chain.from_iterable(cls.Fields.__dict__.items() if hasattr(cls, 'Fields') else () for cls in Cls.__mro__) if not k.startswith('_')}


class newobjectmethod:

	def __init__(self, method):
		self.method = method

	def __get__(self, instance, owner):
		return_instance = False

		if not instance:
			instance = owner()
			return_instance = True

		p = partial(self.method, instance)

		@wraps(p)
		def method(*args, **kwargs):
			p(*args, **kwargs)
			if return_instance:
				return instance

		return method



class Set(frozenset):
	__slots__ = ()

	@classmethod
	def unserialize(Set, data):
		return Set(data)

	def serialize(self):
		return list(self)


class Container:

	def __init__(self):
		for k, _type in fields(self.__class__).items():
			if not hasattr(self, k):
				setattr(self, k, None)

	@newobjectmethod
	def unserialize(self, data):
		if not data:
			data = {}

		for k, _type in fields(self.__class__).items():
			v = data.get(k)
			if _type and hasattr(_type, 'unserialize'):
				print(k, _type, v)
				v = _type.unserialize(v)
			setattr(self, k, v)

	def serialize(self):
		data = {}
		for k, _type in fields(self.__class__).items():
			v = getattr(self, k, None)
			if _type and hasattr(_type, 'serialize'):
				v = _type.serialize(v)
			if v is not None:
				data[k] = v
		return data
