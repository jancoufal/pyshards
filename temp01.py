raw_data_1 = """Red,
RG,
RGB,
BGR,
RGBA,
BGRA,
Red_Integer,
RG_Integer,
RGB_Integer,
BGR_Integer,
RGBA_Integer,
BGRA_Integer,
Stencil_Index,
Depth_Component,
Depth_Stencil"""

raw_data_2 = """#define GL_RED
#define GL_RG
#define GL_RGB
#define GL_BGR
#define GL_RGBA
#define GL_BGRA
#define GL_RED_INTEGER
#define GL_RG_INTEGER
#define GL_RGB_INTEGER
#define GL_BGR_INTEGER
#define GL_RGBA_INTEGER
#define GL_BGRA_INTEGER
#define GL_STENCIL_INDEX
#define GL_DEPTH_COMPONENT
#define GL_DEPTH_STENCIL"""


def main():
	rd1 = [l.strip(',') for l in raw_data_1.split("\n")]
	rd2 = [l.strip('#define ') for l in raw_data_2.split("\n")]
	for _1 in zip(rd1, rd2):
		print("\t\t{ EPixelChannelFormat::%s, %s }," % (_1[0], _1[1]))

	# keywords = [l.split()[0].strip() for l in raw_data.split("\n") if l.strip().startswith("GL_")]

	# for k in keywords:
		# print("\t\t{ EInputKey::%s, %s }," % (k[9:].title(), k))
		# print("\t\t{ EInputMouseButton::%s, %s }," % (k[17:].title(), k)) # mouse

		# translate map, enum values, hint file defines
		# print("\t\t{ ERendererBufferTarget::%s, %s }," % (k[3:][:-7].title(), k))
		# print("\t\t%s," % (k[3:][:-7].title()))
		# print("#define", k)

		# print("\t\t{ ERendererApiError::%s, %s }," % (k[3:-1].title(), k[:-1]))
		# print("\t\t%s" % (k[3:-1].title()))
		# print("#define", k[:-1])


if __name__ == "__main__":
	main()
