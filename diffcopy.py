import argparse
import filecmp
import os
import shutil
from fnmatch import fnmatch


def argParseDirectory(path):
	if os.path.isdir(path):
		return os.path.abspath(path)
	else:
		raise argparse.ArgumentTypeError('%r is not valid direcotry.' % path)


def argParseMaskList(masks):
	return masks.split('|')


def md5sum(filename, blocksize=16384):
	hash = hashlib.md5()
	with open(filename, 'rb') as f:
		for block in iter(lambda: f.read(blocksize), b''):
			hash.update(block)
	return hash.hexdigest()


def match_files(src, mask_list):
	for root, dirs, files in os.walk(src):
		for file in list(filter(lambda file: any([fnmatch(file, mask) for mask in mask_list]), files)):
			yield file


def mcopy(src, dst, mask_list):
	if os.path.samefile(src, dst):
		raise ValueError('Destination directory is same as the source.')

	while True:
		print('')
		print('source      :', src)
		print('destination :', dst)
		print('masks       :', mask_list)

		if len(input('Copy (enter = copy, anything else = break)? ')) != 0:
			break

		file_count = copy_count = 0
		for file in match_files(src, mask_list):

			file_count += 1

			# if destination file exists, copy only when md5 is different
			src_file = os.path.join(src, file)
			dst_file = os.path.join(dst, file)

			if os.path.isfile(dst_file) and filecmp.cmp(src_file, dst_file, shallow=False):
				continue

			print(file)
			shutil.copy2(src_file, dst_file)
			copy_count += 1

		print('')
		print('Files matched: %d, copied %d' % (file_count, copy_count))


if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog='diffcopy',
									 description='Copies specified files with different content from source to destination.')
	parser.add_argument('--mask', default='*.*', type=argParseMaskList,
						help='File masks (splitted by pipe character "|"). Default "*.*".')
	parser.add_argument('--src', required=True, type=argParseDirectory, help='Source directory.')
	parser.add_argument('--dst', required=True, type=argParseDirectory, help='Destination directory.')
	args = parser.parse_args()

	mcopy(args.src, args.dst, args.mask)
