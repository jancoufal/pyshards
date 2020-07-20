import xml.sax as sax


def main():
	# handler_definitions = {
	# 	"registry": HandlerRegistry,
	# 	"registry>types": HandlerTypes,
	# 	"registry>types>type": HandlerType,
	# }

	# g = HandlerGlXml.create(handler_definitions)
	g = HandlerStructScanner.create()
	sax.parse("gl.xml", handler=SaxXmlHandler(g), errorHandler=None)
	print(str(g))


class SaxXmlHandler(sax.ContentHandler):
	def __init__(self, handler):
		self._handler = handler
		# self._handler = StructScanner(None)
		self._data = ""

	def startElement(self, tag, attributes):
		self._data = ""
		self._handler = self._handler.get_handler(tag, attributes)

	def endElement(self, tag):
		self._handler = self._handler.finish(tag, self._data)

	def characters(self, content):
		self._data += content.strip()


class HandlerBase(object):
	def __init__(self, parent_handler, tag, attributes):
		self._parent = parent_handler
		self.tag = tag
		self.attributes = attributes
		self.data = None

	def get_handler(self, tag, attributes):
		raise NotImplementedError

	def finish(self, tag, data):
		if tag != self.tag:
			raise AssertionError(f"Tags does not match ({self.tag}, {tag}")

		self.data = data
		self._parent.on_child_finish(self)
		return self._parent

	def on_child_finish(self, child):
		raise NotImplementedError


class HandlerStructScanner(HandlerBase):
	@classmethod
	def create(cls):
		return cls(None, None, None)

	def __init__(self, parent_handler, tag, attributes):
		super(HandlerStructScanner, self).__init__(parent_handler, tag, attributes)
		self._paths = dict()

	def __str__(self):
		return str(self._paths)

	def get_handler(self, tag, attributes):
		return HandlerStructScanner(self, tag, attributes)

	def on_child_finish(self, child):
		self._accumulate_path(child.tag)

	def _accumulate_path(self, child_tag_path):
		if self._parent is not None:
			p = self.tag + ">" + child_tag_path
			self._parent._accumulate_path(p)
		else:
			self._paths.setdefault(child_tag_path, 0)
			self._paths[child_tag_path] += 1


class HandlerNoOp(HandlerBase):
	def _accept(self, tag, content):
		pass


"""
class HandlerGlXml(HandlerBase):
	@classmethod
	def create(cls, handler_definitions):
		return cls(None, None, None)

	def _get_handler_factory(self):
		return {
			"registry": HandlerRegistry,
		}

	def _accept(self, tag, content):
		print(f"HandlerGlXml > {tag=}, {content=}")


class HandlerRegistry(HandlerBase):
	def _get_handler_factory(self):
		return {
			"types": HandlerTypes,
		}

	def _accept(self, tag, content):
		print(f"HandlerRegistry > {tag=}, {content=}")


class HandlerTypes(HandlerBase):
	def _get_handler_factory(self):
		return {
			"type": HandlerType,
		}

	def _accept(self, tag, content):
		print(f" HandlerTypes > {tag=}, {content=}")


class HandlerType(HandlerBase):
	def _get_handler_factory(self):
		return {
		}

	def _accept(self, tag, content):
		print(f"  HandlerType > {tag=}, {content=}")


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
"""

if __name__ == "__main__":
	main()
