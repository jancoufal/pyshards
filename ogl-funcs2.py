import queue
from enum import Enum, unique
from typing import Dict, Iterable, Callable


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

	glog = GlOutputGenerator(gl_registry, "GlRInternal")
	# glog.write_interface_file(lambda l: output["i"].append(l))
	glog.write_header_file(lambda l: output["h"].append(l))
	glog.write_implementation_file(lambda l: output["cpp"].append(l))

	for l in output["cpp"]:
		print(l)


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

		self.all_commands = self._parse_sub_childs("commands", "command", GlFunction)
		self.commands = GlRegistry._filter_by_predicates(self.all_commands, GlRegistry.PICKED_COMMANDS_PREDICATES)

		self.all_types = self._parse_sub_childs("types", "type", GlType)
		self.types = GlRegistry._filter_by_predicates(self.all_types, GlRegistry.PICKED_TYPES_PREDICATES)
		self.types_lut = {t.gl_type: t for t in self.types}

		self.all_groups = self._parse_sub_childs("groups", "group", GlGroup)
		self.groups_lut = {g.name: g for g in self.all_groups}

	def _parse_sub_childs(self, main_node_name, child_node_name, wrapper_class):
		main_node = self._nodes.find_in_childs_single(main_node_name)
		return [wrapper_class.create_from_entry(n) for n in main_node.find_in_childs_many(child_node_name)]

	@staticmethod
	def _filter_by_predicates(input_iterable, predicates):
		return list(filter(lambda t: all(map(lambda p: p(t), predicates)), input_iterable))


class GlFunction(object):
	@classmethod
	def create_from_entry(cls, entry):
		proto = entry.find_in_childs_single("proto")
		return cls(
			(proto if proto.value is not None else proto.find_in_childs_single("ptype")).value.strip(),
			proto.find_in_childs_single("name").value.strip(),
			[GlFunctionParam.create_from_entry(_) for _ in entry.find_in_childs_many("param")],
			dict(entry.attrib) if entry.attrib is not None else {}
		)

	def __init__(self, return_type, name, param_list, attributes):
		self.return_type = return_type
		self.name = name
		self.params = param_list
		self.param_str = self.get_param_string()
		self.manufacturer = Manufacturer.find_manufacturer(name)
		self.attributes = attributes

	def __str__(self):
		return f"{self.return_type} {self.name}({self.param_str})".strip()

	def get_params_base_types(self):
		return [p.base_type for p in self.params]

	def get_param_string(self, type_translation_table=None):
		return ", ".join(map(lambda p: p.get_param_str(type_translation_table), self.params))

	def get_header(self, type_translation_table=None, name_modifier=None):
		return_type = self.return_type
		if type_translation_table is not None and return_type in type_translation_table:
			return_type = type_translation_table[return_type].base_type
		funtion_name = self.name
		if name_modifier is not None:
			funtion_name = name_modifier(funtion_name)
		return f"{return_type} {funtion_name}({self.get_param_string(type_translation_table)})".strip()


class GlFunctionParam(object):
	@classmethod
	def create_from_entry(cls, entry):
		ptype = entry.find_in_childs_single_optional("ptype")
		return cls(
			entry.value.strip() if entry.value is not None and ptype is not None else "",
			(ptype.value if ptype is not None else entry.value).strip(),
			ptype.tail.strip() if ptype is not None else "",
			entry.find_in_childs_single("name").value.strip(),
			dict(entry.attrib) if entry.attrib is not None else {}
		)

	def __init__(self, modif_bef, param_type, modif_aft, name, attributes):
		self._type_modif_bef = modif_bef
		self._type_modif_aft = modif_aft
		self.base_type = param_type
		self.name = name
		self.type = self._get_param_type()
		self.param_str = self.get_param_str()
		self.attributes = attributes

	def _get_param_type(self, base_type_translation_map=None):
		base_type = self.base_type
		if base_type_translation_map is not None and base_type in base_type_translation_map:
			base_type = base_type_translation_map[self.base_type].base_type
		return f"{self._type_modif_bef} {base_type}{self._type_modif_aft}".strip()

	def get_param_str(self, base_type_translation_map=None):
		return f"{self._get_param_type(base_type_translation_map)} {self.name}"

	def __str__(self):
		return self.param_str


class GlType(object):
	@classmethod
	def create_from_entry(cls, entry):

		# if any of the predicate is met, then it is a special (unhandled) case
		special_type_predicates = {
			lambda n: "typedef struct" in n.value if n.value is not None else False,
			lambda n: len({"name", "comment"} & n.attrib.keys()) > 0,
			lambda n: n.attrib.get("requires", "") == "GLintptr",
			lambda n: n.find_in_childs_single_optional("apientry") is not None,
		}

		is_special = any(map(lambda p: p(entry), special_type_predicates))
		return cls(
			is_special,
			None if is_special else GlType._parse_base_type(entry),
			None if is_special else entry.find_in_childs_single("name").value.strip()
		)

	@staticmethod
	def _parse_base_type(entry):
		if entry.value is None:
			return None

		remove_list = ["typedef"]
		is_khronos = entry.attrib.get("requires", "") == "khrplatform"
		if is_khronos:
			remove_list.append("khronos_")

		base_type = entry.value
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
			[n.attrib.get("name") for n in entry.find_in_childs_many("enum")]
		)

	def __init__(self, name, comment, enum_values):
		self.name = name
		self.comment = comment
		self.values = enum_values

	def __str__(self):
		return f"{self.name}, {self.comment}, {str(self.values)}"


class GlOutputGenerator(object):
	def __init__(self, gl_registry: GlRegistry, wrapper_class):
		self._gl = gl_registry
		self._cpp_class = wrapper_class

	def write_header_file(self, writer_functor):
		GlWriterHeader(self._gl, self._cpp_class).write(writer_functor)

	def write_implementation_file(self, writer_functor):
		GlWriterImplementation(self._gl, self._cpp_class).write(writer_functor)

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
	def __init__(self, gl_registry: GlRegistry, wrapper_class):
		self._gl = gl_registry
		self._cpp_class = wrapper_class
		self._w = None

	def write(self, writer_functor):
		self._w = writer_functor
		self._groups(self._gl.groups_lut)
		self._type_map(self._gl.types_lut)
		self._command_headers(self._gl.commands)

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

	def _type_map(self, types:Dict[str, GlType]):
		GlOutputGenerator.writer_title(self._w, "OpenGL type translations")
		for k in sorted(types.keys()):
			t = types[k]
			if t.manufacturer is None:
				self._w(f"\t// {t.gl_type} => {t.base_type}")

	def _command_headers(self,  commands:Iterable[GlFunction]):
		GlOutputGenerator.writer_title(self._w, "OpenGL commands")
		for command in commands:
			self._command_head(command)

	def _command_head(self, gl_func:GlFunction):
		self._w("")
		self._w("\t//")
		self._w("\t// " + gl_func.name)
		self._w("\t//")
		self._w("\t// params:")
		if len(gl_func.params) == 0:
			self._w("\t//   no params")
		for gl_param in gl_func.params:
			gl_param_str = gl_param.get_param_str()
			if len(gl_param.attributes) > 0:
				gl_param_str += f", attributes: {str(gl_param.attributes)}"
			self._w(f"\t//   {gl_param_str}")
		self._w("\t//")
		self._w(f"\t{gl_func.get_header(self._gl.types_lut, GlOutputGenerator.gl_prefix_remover())} override;")


class GlWriterImplementation(object):
	def __init__(self, gl_registry: GlRegistry, wrapper_class):
		self._gl = gl_registry
		self._cpp_class = wrapper_class
		self._w = None

	def write(self, writer_functor):
		self._w = writer_functor
		self._commands(self._gl.commands)

	def _commands(self, commands: Iterable[GlFunction]):
		for gl_command in commands:
			self._command(gl_command)

	def _command(self, command: GlFunction):
		self._w(f"")
		self._w(f"\t{command.get_header(self._gl.types_lut, GlOutputGenerator.gl_prefix_remover())}")
		self._w("\t{")
		self._w(f"\t\t{command.get_header()};")
		self._w("\t}")


class Node(object):
	@classmethod
	def load_xml(cls, filename):
		import xml.etree.ElementTree as et

		xml_root = et.parse(filename).getroot()
		root_node = Node.from_xml_element(None, xml_root)
		q = queue.Queue()
		q.put((xml_root, root_node))
		while not q.empty():
			xml_node, node_holder = q.get()
			for child_node in xml_node:
				node_holder.childs.append(child_holder := Node.from_xml_element(node_holder, child_node))
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
		self.childs = list()

	def __str__(self):
		return f"{self.tag}, '{self.value.strip() if self.value is not None else ''}', child count: {len(self.childs)}"

	def find_in_childs_many(self, tag):
		return [ch for ch in self.childs if ch.tag == tag]

	def find_in_childs_single(self, tag):
		childs = self.find_in_childs_many(tag)
		if len(childs) == 1:
			return childs.pop()
		error_message = f"Wanted to find single item '{tag}' in {self}, but found {len(childs)}."
		raise AssertionError(error_message)

	def find_in_childs_single_optional(self, tag):
		childs = self.find_in_childs_many(tag)
		child_count = len(childs)
		if child_count == 0:
			return None
		if child_count == 1:
			return childs.pop()

		error_message = f"Wanted to find optionally single item '{tag}' in {self}, but found {len(childs)}."
		raise AssertionError(error_message)


if __name__ == "__main__":
	main()
