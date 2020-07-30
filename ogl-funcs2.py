import queue
from enum import Enum, unique


def main():
	gl_registry = GlRegistry.create_from_file("gl.xml")

	# just for fun
	if False:
		manufacturer_histogram = dict()
		for c in command_list:
			k = c.manufacturer
			if k not in manufacturer_histogram.keys():
				manufacturer_histogram[k] = 0
			manufacturer_histogram[k] = manufacturer_histogram[k] + 1
		print("manufacturers histogram:")
		for m in Manufacturer:
			print(f"{m.value}: {manufacturer_histogram.get(m, 0)}x")

	# picked commands (all predicates must be met)
	print(f"picked commands count: {len(gl_registry.commands)}")

	# gather used base types in base command list
	type_histogram = dict()
	for c in gl_registry.commands:
		for pbt in c.get_params_base_types():
			if pbt not in type_histogram.keys():
				type_histogram[pbt] = 0
			type_histogram[pbt] = type_histogram[pbt] + 1
	if False:
		for t in type_histogram:
			print(f"{t} ({type_histogram[t]}x)")

	for c in gl_registry.commands:
		# format single gl function header & implementation

		if c.name.startswith("glSampleCoveragex"):
			print(c.get_header())
			print(">", c.get_header(gl_registry.types_lut))


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
		return cls(read_xml_to_nodes(filename))

	def __init__(self, nodes):
		self._nodes = nodes

		self.all_commands = self._parse_sub_childs("commands", "command", GlFunction)
		self.commands = GlRegistry._filter_by_predicates(self.all_commands, GlRegistry.PICKED_COMMANDS_PREDICATES)

		self.all_types = self._parse_sub_childs("types", "type", GlType)
		self.types = GlRegistry._filter_by_predicates(self.all_types, GlRegistry.PICKED_TYPES_PREDICATES)
		self.types_lut = {t.gl_type: t.base_type for t in self.types}

		self.all_groups = self._parse_sub_childs("groups", "group", GlGroup)
		self.group_lut = {g.name: g for g in self.all_groups}

	def _parse_sub_childs(self, main_node_name, child_node_name, wrapper_class):
		main_node = find_in_childs_single(self._nodes, main_node_name)
		return [wrapper_class.create_from_entry(n) for n in find_in_childs_many(main_node, child_node_name)]

	@staticmethod
	def _filter_by_predicates(input_iterable, predicates):
		return list(filter(lambda t: all(map(lambda p: p(t), predicates)), input_iterable))


class GlFunction(object):
	@classmethod
	def create_from_entry(cls, entry):
		proto = find_in_childs_single(entry, "proto")
		return cls(
			(proto if proto.value is not None else find_in_childs_single(proto, "ptype")).value.strip(),
			find_in_childs_single(proto, "name").value.strip(),
			[GlFunctionParam.create_from_entry(_) for _ in find_in_childs_many(entry, "param")]
		)

	def __init__(self, return_type, name, param_list):
		self.return_type = return_type
		self.name = name
		self.params = param_list
		self.param_str = self.get_param_string()
		self.manufacturer = Manufacturer.find_manufacturer(name)

	def __str__(self):
		return f"{self.return_type} {self.name}({self.param_str})".strip()

	def get_params_base_types(self):
		return [p.base_type for p in self.params]

	def get_param_string(self, type_translation_table=None):
		return ", ".join(map(lambda p: p.get_param_str(type_translation_table), self.params))

	def get_header(self, type_translation_table=None):
		return_type = self.return_type
		if type_translation_table is not None:
			return_type = type_translation_table.get(return_type, return_type)
		return f"{return_type} {self.name}({self.get_param_string(type_translation_table)})".strip()


class GlFunctionParam(object):
	@classmethod
	def create_from_entry(cls, entry):
		ptype = find_in_childs_single_optional(entry, "ptype")
		return cls(
			entry.value.strip() if entry.value is not None and ptype is not None else "",
			(ptype.value if ptype is not None else entry.value).strip(),
			ptype.tail.strip() if ptype is not None else "",
			find_in_childs_single(entry, "name").value.strip()
		)

	def __init__(self, modif_bef, param_type, modif_aft, name):
		self._type_modif_bef = modif_bef
		self._type_modif_aft = modif_aft
		self.base_type = param_type
		self.name = name
		self.type = self._get_param_type()
		self.param_str = self.get_param_str()

	def _get_param_type(self, base_type_translation_map=None):
		tran_table = {} if base_type_translation_map is None else base_type_translation_map
		return f"{self._type_modif_bef} {tran_table.get(self.base_type, self.base_type)}{self._type_modif_aft}".strip()

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
			lambda n: find_in_childs_single_optional(n, "apientry") is not None,
		}

		is_special = any(map(lambda p: p(entry), special_type_predicates))
		return cls(
			is_special,
			None if is_special else GlType._parse_base_type(entry),
			None if is_special else find_in_childs_single(entry, "name").value.strip()
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
			[n.attrib.get("name") for n in find_in_childs_many(entry, "enum")]
		)

	def __init__(self, name, comment, enum_values):
		self.name = name
		self.comment = comment
		self.values = enum_values

	def __str__(self):
		return f"{self.name}, {self.comment}, {str(self.values)}"


def find_in_childs_many(node, tag):
	return [ch for ch in node.childs if ch.tag == tag]


def find_in_childs_single(node, tag):
	childs = find_in_childs_many(node, tag)
	if len(childs) == 1:
		return childs.pop()
	error_message = f"Wanted to find single item '{tag}' in {node}, but found {len(childs)}."
	raise AssertionError(error_message)


def find_in_childs_single_optional(node, tag):
	childs = find_in_childs_many(node, tag)
	child_count = len(childs)
	if child_count == 0:
		return None
	if child_count == 1:
		return childs.pop()

	error_message = f"Wanted to find optionally single item '{tag}' in {node}, but found {len(childs)}."
	raise AssertionError(error_message)


def has_child(node, tag):
	for ch in node.childs:
		if ch.tag == tag:
			return True
	return False


def read_xml_to_nodes(xml_file):
	import xml.etree.ElementTree as et

	xml_root = et.parse(xml_file).getroot()
	root_node = Node.from_xml_element(None, xml_root)
	q = queue.Queue()
	q.put((xml_root, root_node))
	while not q.empty():
		xml_node, node_holder = q.get()
		for child_node in xml_node:
			node_holder.childs.append(child_holder := Node.from_xml_element(node_holder, child_node))
			q.put((child_node, child_holder))

	return root_node


class Node(object):
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


if __name__ == "__main__":
	main()
