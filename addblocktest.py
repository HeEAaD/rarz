#!/usr/bin/env python

import os
from zlib import crc32
from struct import pack,unpack

BUFFER_SIZE = 4 * 1024
BLOCK_SIZE = 128 * 1024
TEST_FILE = '/test/File.mkv'
RAR_FILE = '/test/test1.rar'
MARK_HEAD = 'Rar!\x1a\x07\x00'
MAIN_HEAD = '\xcf\x90s\x00\x00\r\x00\x00\x00\x00\x00\x00\x00'
FILE_HEAD = '+)t\xc0\x90*\x00\x8b\xef\xfeg\x8b\xef\xfeg\x03\n\x18\xc7\xe4\x05[\xb5D\x140\x08\x00\xed\x81\x00\x00File.mkv\x00\xc0'
ENDARC_HEAD = '\xc4\x3d\x7b\x00\x40\x07\x00'
FILL_BYTE = '\x00'

def writeOffsetBlock(size):
	offset_block = '\x7c\x00\x00'
	offset_block += pack('H',size)
	offset_block_crc = crc32(offset_block) & 0xffffffff
	offset_block_start = rar.tell()

	print offset_block_start

	rar.write('\x00\x00'+offset_block)

	for i in range(2 + len(offset_block),size):
		offset_block += FILL_BYTE
		rar.write(FILL_BYTE)
		offset_block_crc = crc32(FILL_BYTE,offset_block_crc) & 0xffffffff

	offset_block_end = rar.tell()
	rar.seek(offset_block_start)
	rar.write(pack('H',offset_block_crc & 0xffff))
	rar.seek(offset_block_end)

if __name__ == '__main__':
	file_size = os.path.getsize(TEST_FILE)

	if file_size < BLOCK_SIZE:
		print 'I\'m not aligning files which are smaller than {0} bytes.'.format(BLOCK_SIZE)
		exit(1)


	rar = open(RAR_FILE,'w')
	rar.write(MARK_HEAD)
	rar.write(MAIN_HEAD)

	# file_head_length = 34
	# file_head_length += len(TEST_FILE.split('/')[-1])
	#
	# if file_size > 0xffffffff:
	# 	file_head_length += 8
	file_head_length = len(FILE_HEAD)

	offset_to_insert = BLOCK_SIZE - len(MARK_HEAD) - len(MAIN_HEAD) - file_head_length
	print "offset: {0}".format(offset_to_insert)


	while offset_to_insert >= 0xffff:
		writeOffsetBlock(0xffff)
		offset_to_insert -= 0xffff

	writeOffsetBlock(offset_to_insert)

	rar.write(FILE_HEAD)

	with open(TEST_FILE,'r') as f:
		while True:
			b = f.read(BUFFER_SIZE)

			if not b:
				break

			rar.write(b)

	rar.write(ENDARC_HEAD)
	rar.close()
