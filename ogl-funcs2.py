import xml.etree.ElementTree as et
import queue


def main():
	gl_registry = read_xml_to_nodes("gl.xml")
	print(gl_registry)


def read_xml_to_nodes(xml_file):
	xml_root = et.parse(xml_file).getroot()
	root_node = Node.from_xml_element(xml_root)
	q = queue.Queue()
	q.put((xml_root, root_node))
	while not q.empty():
		xml_node, node_holder = q.get()
		for child_node in xml_node:
			node_holder.childs.append(child_holder := Node.from_xml_element(child_node))
			q.put((child_node, child_holder))

	return root_node


class Node(object):
	@classmethod
	def from_xml_element(cls, tree_element_node):
		return cls(
			tree_element_node.tag,
			tree_element_node.attrib,
			tree_element_node.text
		)

	def __init__(self, tag, attrib, value):
		self.tag = tag
		self.attrib = attrib
		self.value = value
		self.childs = list()

	def __str__(self):
		return f"{self.tag}, '{self.value.strip() if self.value is not None else ''}', child count: {len(self.childs)}"


if __name__ == "__main__":
	main()
