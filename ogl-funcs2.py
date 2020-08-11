import queue
from enum import Enum, unique
from typing import Dict, Iterable


def main():
	gl_registry = GlRegistry.create_from_file("gl.xml")

	print_histograms = False

	# just for fun
	if print_histograms:
		manufacturer_histogram = dict()
		for c in gl_registry.all_commands:
			k = c.manufacturer
			if k not in manufacturer_histogram.keys():
				manufacturer_histogram[k] = 0
			manufacturer_histogram[k] = manufacturer_histogram[k] + 1
		print("manufacturers histogram:")
		for m in Manufacturer:
			print(f"{m.value}: {manufacturer_histogram.get(m, 0)}x")

	# gather used base types in base command list
	if print_histograms:
		type_histogram = dict()
		for c in gl_registry.commands:
			for pbt in c.get_params_base_types():
				if pbt not in type_histogram.keys():
					type_histogram[pbt] = 0
				type_histogram[pbt] = type_histogram[pbt] + 1
		print("used types histogram")
		for t in type_histogram:
			print(f"{t} ({type_histogram[t]}x)")

	# output
	output = {"i": list(), "h": list(), "cpp": list()}
	writer = {k: lambda l: output[k].append(l) for k in output.keys()}

	GlOutputGenerator(gl_registry, "GlRInternal")\
		.write_header(writer["h"]) \
		.write_interface(writer["i"]) \
		.write_implementation(writer["cpp"])

	for line in output["cpp"]:
		print(line)


@unique
class Manufacturer(Enum):
	_3DFX = "3DFX"
	AMD = "AMD"
	ANGLE = "ANGLE"
	APPLE = "APPLE"
	ARB = "ARB"
	ATI = "ATI"
	EXT = "EXT"
	GREMEDY = "GREMEDY"
	HP = "HP"
	IBM = "IBM"
	IMG = "IMG"
	INGR = "INGR"
	INTEL = "INTEL"
	KHR = "KHR"
	MESA = "MESA"
	NV = "NV"
	NVX = "NVX"
	OES = "OES"
	OVR = "OVR"
	QCOM = "QCOM"
	SGIS = "SGIS"
	SGIX = "SGIX"
	SUN = "SUN"

	@staticmethod
	def find_manufacturer(name):
		if name is not None:
			for e in Manufacturer:
				if name.endswith(e.value):
					return e
		return None


class GlRegistry(object):

	# picked commands (all predicates must be met)
	PICKED_COMMANDS_PREDICATES = {
		lambda command: command.manufacturer is None,
		lambda command: not command.name.startswith("glDebugMessageCallback"),  # too complicated header
		lambda command: not command.name.startswith("glFenceSync"),  # complicated return type
	}

	# picked types (all predicates must be met)
	PICKED_TYPES_PREDICATES = {
		# lambda t: t.manufacturer is None,
		lambda t: not t.is_special,  # too complicated to handle
	}

	@classmethod
	def create_from_file(cls, filename):
		return cls(Node.load_xml(filename))

	def __init__(self, nodes):
		self._nodes = nodes

		self.all_commands = self._parse_sub_children("commands", "command", GlFunction)
		self.commands = GlRegistry._filter_by_predicates(self.all_commands, GlRegistry.PICKED_COMMANDS_PREDICATES)

		self.all_types = self._parse_sub_children("types", "type", GlType)
		self.types = GlRegistry._filter_by_predicates(self.all_types, GlRegistry.PICKED_TYPES_PREDICATES)
		self.types_type_lut = {t.gl_type: t for t in self.types}
		self.types_lut = {t.gl_type: t.base_type for t in self.types}

		self.all_groups = self._parse_sub_children("groups", "group", GlGroup)
		self.groups_lut = {g.name: g for g in self.all_groups}

	def _parse_sub_children(self, main_node_name, child_node_name, wrapper_class):
		main_node = self._nodes.find_in_children_single(main_node_name)
		return [wrapper_class.create_from_entry(n) for n in main_node.find_in_children_many(child_node_name)]

	@staticmethod
	def _filter_by_predicates(input_iterable, predicates):
		return list(filter(lambda t: all(map(lambda p: p(t), predicates)), input_iterable))


class GlReturnType(object):
	@classmethod
	def create_from_entry(cls, proto_entry):
		ptype = proto_entry.find_in_children_single_optional("ptype")
		return cls(
			(proto_entry.value if ptype is not None and proto_entry.value is not None else "").strip(),
			(proto_entry if ptype is None else ptype).value.strip(),
			ptype.tail.strip() if ptype is not None else ""
		)

	def __init__(self, modifier_bef, return_type, modifier_aft):
		self.type_modifier_bef = modifier_bef
		self.return_type = return_type
		self.type_modifier_aft = modifier_aft


class GlFunctionParam(object):
	@classmethod
	def create_from_entry(cls, entry):
		ptype = entry.find_in_children_single_optional("ptype")
		return cls(
			entry.value.strip() if entry.value is not None and ptype is not None else "",
			(ptype.value if ptype is not None else entry.value).strip(),
			ptype.tail.strip() if ptype is not None else "",
			entry.find_in_children_single("name").value.strip(),
			dict(entry.attrib) if entry.attrib is not None else {}
		)

	def __init__(self, modifier_bef, param_type, modifier_aft, name, attributes):
		self.type_modifier_bef = modifier_bef
		self.type_modifier_aft = modifier_aft
		self.base_type = param_type
		self.name = name
		self.attributes = attributes


class GlFunction(object):
	@classmethod
	def create_from_entry(cls, entry):
		proto = entry.find_in_children_single("proto")
		return cls(
			GlReturnType.create_from_entry(proto),
			proto.find_in_children_single("name").value.strip(),
			[GlFunctionParam.create_from_entry(_) for _ in entry.find_in_children_many("param")],
			dict(entry.attrib) if entry.attrib is not None else {}
		)

	def __init__(self, return_type: GlReturnType, name, param_list: Iterable[GlFunctionParam], attributes: Dict[str, str]):
		self.return_type = return_type
		self.name = name
		self.params = param_list
		self.manufacturer = Manufacturer.find_manufacturer(name)
		self.attributes = attributes

	def get_params_base_types(self):
		return [p.base_type for p in self.params]


class GlType(object):
	@classmethod
	def create_from_entry(cls, entry):

		# if any of the predicate is met, then it is a special (unhandled) case
		special_type_predicates = {
			lambda n: "typedef struct" in n.value if n.value is not None else False,
			lambda n: len({"name", "comment"} & n.attrib.keys()) > 0,
			lambda n: n.attrib.get("requires", "") == "GLintptr",
			lambda n: n.find_in_children_single_optional("apientry") is not None,
		}

		is_special = any(map(lambda p: p(entry), special_type_predicates))
		return cls(
			is_special,
			None if is_special else GlType._parse_base_type(entry),
			None if is_special else entry.find_in_children_single("name").value.strip()
		)

	@staticmethod
	def _parse_base_type(entry):
		if entry.value is None:
			return None

		remove_list = ["typedef"]
		is_khronos = entry.attrib.get("requires", "") == "khrplatform"
		if is_khronos:
			remove_list.append("khronos_")

		base_type = entry.value.strip()
		for r in remove_list:
			if base_type.startswith(r):
				base_type = base_type[len(r):].strip()

		special_cases_lut = dict()

		if is_khronos:
			special_cases_lut.update({
				"float_t": "float",
				"intptr_t": "int32_t",  # "signed long int",
				"uintptr_t": "uint32_t",  # "unsigned long int",
				"ssize_t": "int32_t",  # win32 => "signed long int", win64 => "signed long long int"
				"usize_t": "uint32_t",  # win32 => "signed long int", win64 => "signed long long int"
				"stime_nanoseconds_t": "int64_t",
				"utime_nanoseconds_t": "uint64_t",
			})

		return special_cases_lut.get(base_type, base_type)

	def __init__(self, is_special, base_type, gl_type):
		self.is_special = is_special
		self.base_type = base_type
		self.gl_type = gl_type
		self.manufacturer = Manufacturer.find_manufacturer(gl_type)

	def __str__(self):
		return f"{self.base_type} ~ {self.gl_type}{' *' if self.is_special else ''} {self.manufacturer}"


class GlGroup(object):
	@classmethod
	def create_from_entry(cls, entry):
		return cls(
			entry.attrib.get("name"),
			entry.attrib.get("comment", ""),
			[n.attrib.get("name") for n in entry.find_in_children_many("enum")]
		)

	def __init__(self, name, comment, enum_values):
		self.name = name
		self.comment = comment
		self.values = enum_values

	def __str__(self):
		return f"{self.name}, {self.comment}, {str(self.values)}"


class GlFunctionParamFormatter(object):
	@classmethod
	def create(cls, gl_param: GlFunctionParam, gl_registry: GlRegistry):
		native_base_type = gl_registry.types_lut.get(gl_param.base_type, gl_param.base_type)
		full_native_type = GlFunctionParamFormatter._get_param_type_str(gl_param, native_base_type)
		full_gl_type = GlFunctionParamFormatter._get_param_type_str(gl_param, gl_param.base_type)
		attribute_str = "" if len(gl_param.attributes) == 0 else f", attributes: {str(gl_param.attributes)}"
		return cls(
			gl_param.name,
			f"{full_gl_type} {gl_param.name}",
			f"{full_native_type} {gl_param.name}",
			f"{full_native_type} {gl_param.name}{attribute_str}",
			f"static_cast<{full_gl_type}>({gl_param.name})"
		)

	@staticmethod
	def _get_param_str(gl_param: GlFunctionParam, param_type):
		return f"{GlFunctionParamFormatter._get_param_type_str(gl_param, param_type)} {gl_param.name}".strip()

	@staticmethod
	def _get_param_type_str(gl_param: GlFunctionParam, param_type):
		return f"{gl_param.type_modifier_bef} {param_type}{gl_param.type_modifier_aft}".strip()

	def __init__(self, param_name, gl_param_str, native_param_str, param_description, static_cast_str):
		self.name = param_name
		self.gl_param_str = gl_param_str
		self.native_param_str = native_param_str
		self.description = param_description
		self.static_cast_str = static_cast_str


class GlReturnTypeFormatter(object):
	@classmethod
	def create(cls, gl_return_type: GlReturnType, gl_registry: GlRegistry):
		native_return_type = gl_registry.types_lut.get(gl_return_type.return_type, gl_return_type.return_type)
		return cls(
			gl_return_type.return_type,
			native_return_type,
			GlReturnTypeFormatter._get_return_type_str(gl_return_type, gl_return_type.return_type),
			GlReturnTypeFormatter._get_return_type_str(gl_return_type, native_return_type)
		)

	@staticmethod
	def _get_return_type_str(gl_return_type: GlReturnType, return_type):
		return f"{gl_return_type.type_modifier_bef} {return_type}{gl_return_type.type_modifier_aft}".strip()

	def __init__(self, gl_return_type, non_gl_return_type, gl_return_str, non_gl_return_str):
		self.gl_return_type = gl_return_type
		self.non_gl_return_type = non_gl_return_type
		self.gl_return_str = gl_return_str
		self.non_gl_return_str = non_gl_return_str


class GlFunctionFormatter(object):
	@classmethod
	def create(cls, gl_function: GlFunction, gl_registry: GlRegistry):
		non_gl_name = GlFunctionFormatter.remove_gl_prefix(gl_function.name)
		return_value_formatter = GlReturnTypeFormatter.create(gl_function.return_type, gl_registry)
		param_formatters = [GlFunctionParamFormatter.create(p, gl_registry) for p in gl_function.params]
		params_list_str = ', '.join(map(lambda p: p.gl_param_str, param_formatters))
		params_native_list_str = ', '.join(map(lambda p: p.native_param_str, param_formatters))
		return cls(
			gl_function.name,
			non_gl_name,
			return_value_formatter,
			param_formatters,
			f"{return_value_formatter.gl_return_str} {gl_function.name}({params_list_str})",
			f"{return_value_formatter.non_gl_return_str} {non_gl_name}({params_native_list_str})",
		)

	@staticmethod
	def remove_gl_prefix(function_name):
		if function_name.startswith("gl"):
			return function_name[2].lower() + function_name[3:]
		else:
			raise ValueError("function '" + function_name + "' is not a 'gl' function.")

	def __init__(self, gl_name, non_gl_name, return_formatter, param_formatters, gl_header, native_header):
		self.gl_name = gl_name
		self.non_gl_name = non_gl_name
		self.return_formatter = return_formatter
		self.param_fmts = param_formatters
		self.gl_header = gl_header
		self.native_header = native_header


class GlOutputGenerator(object):
	def __init__(self, gl_registry: GlRegistry, wrapper_class: str):
		self._gl = gl_registry
		self._cpp_class = wrapper_class

	def write_header(self, writer_functor):
		GlWriterHeader(self._gl, self._cpp_class).write(writer_functor)
		return self

	def write_implementation(self, writer_functor):
		GlWriterImplementation(self._gl, self._cpp_class).write(writer_functor)
		return self

	def write_interface(self, writer_functor):
		writer_functor("write_interface not implemented")
		return self

	@staticmethod
	def gl_prefix_remover():
		def _impl(fn_name: str):
			if fn_name.startswith("gl"):
				return fn_name[2].lower() + fn_name[3:]
			else:
				raise ValueError("function '" + fn_name + "' is not a 'gl' function.")
		return _impl

	@staticmethod
	def writer_title(writer_functor, title):
		writer_functor("")
		writer_functor("")
		writer_functor("\t//")
		writer_functor("\t// " + title)
		writer_functor("\t//")
		writer_functor("")


class GlWriterHeader(object):
	def __init__(self, gl_registry: GlRegistry, wrapper_class: str):
		self._gl_registry = gl_registry
		self._cpp_class = wrapper_class
		self._w = None

	def write(self, writer_functor):
		self._w = writer_functor
		self._groups(self._gl_registry.groups_lut)
		self._type_map(self._gl_registry.types_type_lut)
		self._command_headers(self._gl_registry.commands)

	def _groups(self, groups: Dict[str, GlGroup]):
		GlOutputGenerator.writer_title(self._w, "Groups")
		for k in sorted(groups.keys()):
			g = groups[k]
			g_desc = g.name
			if g.comment is not None:
				g_desc += " (" + g.comment + ")"
			self._w(f"\t// Group: {g_desc}")
			self._w(f"\t// Values (x{len(g.values)}):")
			for v in g.values:
				self._w(f"\t//\t{v}")

	def _type_map(self, types: Dict[str, GlType]):
		GlOutputGenerator.writer_title(self._w, "OpenGL type translations")
		for k in sorted(types.keys()):
			t = types[k]
			if t.manufacturer is None:
				self._w(f"\t// {t.gl_type} => {t.base_type}")

	def _command_headers(self,  commands: Iterable[GlFunction]):
		GlOutputGenerator.writer_title(self._w, "OpenGL commands")
		for command in commands:
			self._command_head(command)

	def _command_head(self, gl_func: GlFunction):
		fmt = GlFunctionFormatter.create(gl_func, self._gl_registry)
		self._w("")
		self._w("\t//")
		self._w("\t// " + fmt.gl_name)
		self._w("\t//")
		self._w("\t// params:")
		if len(fmt.param_fmts) == 0:
			self._w("\t//   no params")
		else:
			for param_fmt in fmt.param_fmts:
				self._w(f"\t//   {param_fmt.description}")
		self._w("\t//")
		self._w(f"\t{fmt.native_header} override;")


class GlWriterImplementation(object):
	def __init__(self, gl_registry: GlRegistry, wrapper_class):
		self._gl_registry = gl_registry
		self._cpp_class = wrapper_class
		self._w = None

	def write(self, writer_functor):
		self._w = writer_functor
		self._commands(self._gl_registry.commands)

	def _commands(self, commands: Iterable[GlFunction]):
		for gl_command in commands:
			self._command(gl_command)

	def _command(self, command: GlFunction):
		fmt = GlFunctionFormatter.create(command, self._gl_registry)
		has_return = fmt.return_formatter.non_gl_return_type != "void"
		return_var_name = "res"
		return_var = f"{fmt.return_formatter.gl_return_str} {return_var_name} = " if has_return else ""

		self._w(f"")
		self._w(f"\t{fmt.native_header}")
		self._w("\t{")
		param_count = len(fmt.param_fmts)
		if param_count == 0:
			self._w(f"\t\t{return_var}{fmt.gl_name}();")
		else:
			self._w(f"\t\t{return_var}{fmt.gl_name}(")
			for i, p in enumerate(fmt.param_fmts):
				self._w(f"\t\t\t{p.static_cast_str}{',' if i < param_count - 1 else ''}")
			self._w(f"\t\t);")

		if has_return:
			self._w(f"")
			self._w(f"\t\treturn static_cast<{fmt.return_formatter.non_gl_return_str}>({return_var_name});")
		self._w("\t}")


class Node(object):
	@classmethod
	def load_xml(cls, filename):
		import xml.etree.ElementTree

		xml_root = xml.etree.ElementTree.parse(filename).getroot()
		root_node = Node.from_xml_element(None, xml_root)
		q = queue.Queue()
		q.put((xml_root, root_node))
		while not q.empty():
			xml_node, node_holder = q.get()
			for child_node in xml_node:
				node_holder.children.append(child_holder := Node.from_xml_element(node_holder, child_node))
				q.put((child_node, child_holder))

		return root_node

	@classmethod
	def from_xml_element(cls, parent_node, tree_element_node):
		return cls(
			parent_node,
			tree_element_node.tag,
			tree_element_node.attrib,
			tree_element_node.text,
			tree_element_node.tail
		)

	def __init__(self, parent, tag, attrib, value, tail):
		self.parent = parent
		self.tag = tag
		self.attrib = attrib
		self.value = value
		self.tail = tail
		self.children = list()

	def __str__(self):
		return f"{self.tag}, '{self.value.strip() if self.value is not None else ''}', child count: {len(self.children)}"

	def find_in_children_many(self, tag):
		return [ch for ch in self.children if ch.tag == tag]

	def find_in_children_single(self, tag):
		children = self.find_in_children_many(tag)
		if len(children) == 1:
			return children.pop()
		error_message = f"Wanted to find single item '{tag}' in {self}, but found {len(children)}."
		raise AssertionError(error_message)

	def find_in_children_single_optional(self, tag):
		children = self.find_in_children_many(tag)
		children_count = len(children)
		if children_count == 0:
			return None
		if children_count == 1:
			return children.pop()

		error_message = f"Wanted to find optionally single item '{tag}' in {self}, but found {len(children)}."
		raise AssertionError(error_message)


if __name__ == "__main__":
	main()
