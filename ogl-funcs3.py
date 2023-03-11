from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
class EnumClass:
	name: str
	underlying_type: str

@dataclass
class EnumValue:
	name: str
	value: str

	@property
	def cxx_name(self):
		n = self.name[3:].title()
		return "_" + n if n[0].isdigit() else n

	def __str__(self):
		return f"EnumValue({self.name=},{self.cxx_name=},{self.value=})"

def load_data(filename):
	def _parse_line(l: str):
		l = l.strip()
		if l.startswith("enum class"):
			return EnumClass(*(e.strip() for e in l[10:].split(":")))
		if l.startswith("GL_"):
			n, v = l.split("=")
			return EnumValue(n.strip(), v.split(",")[0].strip())
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
	used_values = set()
	for v in ev:
		prefix = "// " if v.value in used_values else ""
		used_values.add(v.value)
		writer(f"\t\t{prefix}{v.cxx_name},")
	writer("\t};")
	writer("")


def main():
	enum_open = None
	enum_values = list()
	with writer_context("ogl-funcs3.out") as out:
		for t in load_data("ogl-funcs3.txt"):
			if isinstance(t, EnumClass):
				if enum_open is not None:
					write_enum(out, enum_open, enum_values)
					enum_values = list()
				enum_open = t

			if isinstance(t, EnumValue):
				enum_values.append(t)

		if enum_open is not None:
			write_enum(out, enum_open, enum_values)


if __name__ == "__main__":
	main()
