import xml.sax as sax


def main():
	h = GlXmlHandler()
	sax.parse("gl.xml", h, errorHandler=None)
	print(str(h))


class GlXmlHandler(sax.ContentHandler):
	def __init__(self):
		self._handler = StructScanner(None)
		# self._handler = NoOpHandler(None)
		# self._handler = HandlerRoot(None)
		self._data = ""

	def startElement(self, tag, attributes):
		self._data = ""
		self._handler = self._handler.get_handler(tag, attributes)

	def endElement(self, tag):
		self._handler = self._handler.finish(tag, self._data)

	def characters(self, content):
		self._data += content.strip()


class HandlerBase(object):
	def __init__(self, parent_handler):
		self._parent = parent_handler

	def get_handler(self, tag, attributes):
		return self._get_handler(tag, attributes)

	def _get_handler(self, tag, attributes):
		raise NotImplementedError

	def finish(self, tag, content):
		self._parent._accept(tag, self._on_content(content))
		return self._parent

	def _on_content(self, content):
		return content

	def _accept(self, tag, content):
		raise NotImplementedError


class StructScanner(HandlerBase):
	def __init__(self, parent_handler):
		super(StructScanner, self).__init__(parent_handler)
		self._structure = dict()

	def __str__(self):
		return str(self._structure)

	def _get_handler(self, tag, att):
		self._structure[tag] = dict()
		return StructScanner(self)

	def _on_content(self, content):
		return self._structure

	def _accept(self, tag, content):
		self._structure[tag].update(content)


'''
class NoOpHandler(object):
	def __init__(self, ctx):
		self._ctx = ctx

	def get_handler(self, tag, attr):
		return NoOpHandler(self)

	def finish(self, tag, content):
		return self._ctx

	def accept(self, *args, **kwargs):
		pass


class HandlerRoot(object):
	def __init__(self):
		self._r = ""
		self._h = {
			"registry": HandlerRegistry(self)
		}

	def get_handler(self, tag, attr):
		return self._h.get(tag, NoOpHandler(self))

	def finish(self):
		return self._r

	def accept(self, anything):
		self._r = anything


class HandlerRegistry(object):
	def __init__(self, parent_handler):
		self._par = parent_handler
		self._h = {
			# "comment": HandlerComment(self),
			"types": HandlerTypes(self),
			# "groups": HandlerGroups(self),
			# "enums": HandlerEnums(self),
			# "commands": HandlerCommands(self),
			# "feature": HandlerFeature(self),
			# "extensions": HandlerExtension(self),
		}

	def get_handler(self, tag, attr):
		return self._h.get(tag, NoOpHandler(self))

	def finish(self, tag, content):
		self._par.accept(content)
		return self._par

	def accept(self, content):
		pass


class HandlerTypes(object):
	def __init__(self, parent_handler):
		self._par = parent_handler
		self._h = {}

	def get_handler(self, tag, attr):
		return self._h.get(tag, NoOpHandler(self))

	def finish(self, tag, content):
		self._par.accept(content)
		return self._par

	def accept(self, content):
		pass


class HandlerRegistry(object):
	def __init__(self, parent_handler):
		self._par = parent_handler
		self._h = {
			"comment": HandlerComment(self),
			"types": HandlerTypes(self),
			"groups": HandlerGroups(self),
			"enums": HandlerEnums(self),
			"commands": HandlerCommands(self),
			"feature": HandlerFeature(self),
			"extensions": HandlerExtension(self),
		}

class FnParam(object):
	def __init__(self, owning_command):
		self._components = list()
		self._owning_cmd = owning_command

	def __str__(self):
		return ", ".join(self._components)

	def __call__(self, d):
		self._components = d.strip()

	def consume(self, d):
		self._components = d.strip()

	def finish(self):
		self._owning_cmd.add_param(self)


class GlFunction(object):
	def __init__(self):
		self._ret_type = None
		self._fn_name = None
		self._params = list()
		self._handlers = {
			"proto": self.set_ret_type,
			"name": self.set_fn_name,
			"param": FnParam(self),
		}

	def set_ret_type(self, ret_type):
		self._ret_type = ret_type

	def set_fn_name(self, fn_name):
		self._fn_name = fn_name

	def new_param(self):
		return FnParam(self)

	def add_param(self, fn_param):
		self._params.append(fn_param)

	def get_handler(self, tag):
		return self._handlers[tag]

	def __str__(self):
		return f"{self._ret_type} {self._fn_name}"
'''

if __name__ == '__main__':
	main()
