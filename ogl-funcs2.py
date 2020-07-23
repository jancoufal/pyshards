import queue
from enum import Enum, unique


def main():
	gl_registry = read_xml_to_nodes("gl.xml")
	# print(gl_registry)

	# generate functions
	commands_registry = find_in_childs_single(gl_registry, "commands")
	command_list = [GlFunction.create_from_entry(n) for n in find_in_childs_many(commands_registry, "command")]
	print(f"commands count: {len(command_list)}")

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
	command_predicates = {
		lambda c: c.manufacturer is None,
		lambda c: not c.name.startswith("glDebugMessageCallback"),
		lambda c: not c.name.startswith("glSampleCoveragex"),
	}
	picked_command_list = list(filter(lambda c: all(map(lambda pred: pred(c), command_predicates)), command_list))
	print(f"picked commands count: {len(picked_command_list)}")

	# gather used base types in base command list
	type_histogram = dict()
	for c in picked_command_list:
		for pbt in c.get_params_base_types():
			if pbt not in type_histogram.keys():
				type_histogram[pbt] = 0
			type_histogram[pbt] = type_histogram[pbt] + 1
	if False:
		for t in type_histogram:
			print(f"{t} ({type_histogram[t]}x)")

	# gather types
	types_registry = find_in_childs_single(gl_registry, "types")
	type_list = [GlType.create_from_entry(n) for n in find_in_childs_many(types_registry, "type")]

	# translatable types (all predicates must be met)
	picked_types_predicates = {
		# lambda t: t.manufacturer is None,
		lambda t: not t.is_special,
	}
	picked_type_list = list(filter(lambda t: all(map(lambda predicate: predicate(t), picked_types_predicates)), type_list))
	print(f"{len(picked_type_list)}")
	type_translation_map = {t.gl_type: t.base_type for t in picked_type_list}

	for ttm in type_translation_map:
		print(ttm, type_translation_map[ttm])
	# print(type_translation_map)


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


class GlFunctionParam(object):
	@classmethod
	def create_from_entry(cls, entry):
		ptype = find_in_childs_single_optional(entry, "ptype")
		return cls(
			entry.value.strip() if entry.value is not None else "",
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
			lambda n: "typedef struct" in n.value,
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
		if entry.attrib.get("requires", "") == "khrplatform":
			remove_list.append("khronos_")

		base_type = entry.value
		for r in remove_list:
			if base_type.startswith(r):
				base_type = base_type[len(r):].strip()

		special_cases_lut = {
			"float_t": "float",
			"intptr_t": "int*",
			"ssize_t": "size_t*",
		}

		return special_cases_lut.get(base_type, base_type)

	def __init__(self, is_special, base_type, gl_type):
		self.is_special = is_special
		self.base_type = base_type
		self.gl_type = gl_type
		self.manufacturer = Manufacturer.find_manufacturer(gl_type)

	def __str__(self):
		return f"{self.base_type} ~ {self.gl_type}{' *' if self.is_special else ''} {self.manufacturer}"


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
