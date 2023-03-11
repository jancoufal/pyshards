from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
class EnumClass:
	name: str

	@property
	def underlying_type(self):
		return "unsigned int"

@dataclass
class EnumValue:
	name: str

	@property
	def cxx_name(self):
		n = self.name[3:].title()
		return "_" + n if n[0].isdigit() else n

	def __str__(self):
		return f"EnumValue({self.name=},{self.cxx_name=})"


def load_data(filename):
	def _parse_line(l: str):
		if l.startswith("    //"):
			return EnumClass(l[6:].strip())
		if l.startswith("    GL_"):
			return EnumValue(l.split("=")[0].strip())
		return None

	with open(filename, "rt") as fh:
		return filter(lambda o: o is not None, map(_parse_line, fh.readlines()))


@contextmanager
def writer_context(filename):
	def _writer(fh):
		def _impl(l):
			if fh is None:
				print(l)
			else:
				fh.write(l + "\n")
		return _impl

	fh = open(filename, "wt") if filename is not None else None
	try:
		yield _writer(fh)
	finally:
		if fh is not None:
			fh.close()


def write_enum(writer: callable, ec: EnumClass, ev: list[EnumValue]):
	writer(f"\tenum class {ec.name} : {ec.underlying_type}")
	writer("\t{")
	for v in ev:
		writer(f"\t\t{v.cxx_name},")
	writer("\t};")
	writer("")


def main():

	# empty enum: ColorMaterialFace,
	# SamplePatternSGIS enum values begins with a number,
	# discard enum: __UNGROUPED__,

	enum_open = None
	enum_values = list()
	with writer_context("ogl-funcs4.out") as out:
		for t in load_data("ogl-funcs4.txt"):
			if isinstance(t, EnumClass):
				if enum_open is not None and len(enum_values) > 0:
					write_enum(out, enum_open, enum_values)
					enum_values = list()
				enum_open = t

			if isinstance(t, EnumValue):
				enum_values.append(t)

		if enum_open is not None and len(enum_values) > 0 and enum_open.name != "__UNGROUPED__":
			write_enum(out, enum_open, enum_values)


if __name__ == "__main__":
	main()
