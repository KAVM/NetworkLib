from NetworkLibrary.PcapngLib.PcapngHelpers import *
from NetworkLibrary.UtilityLib.Utility import *
from Options import Options

import struct
import binascii

class SectionHeader:
	def __init__(self,section):
		self.section = section
		self.block_type_int = 0
		self.is_valid = True
		self.block_type_packed = "\x00\x00\x00\x00"

		self.byte_order_packed = "\x1a\x2b\x3c\x4d"
		self.endianness = ">"

		self.block_total_length_first_int = 0
		self.block_total_length_first_packed = "\x00\x00\x00\x00"
		self.major_version_int = 0
		self.major_version_packed = "\x00\x00"
		self.minor_version_int = 0
		self.minor_version_packed = "\x00\x00"
		self.section_length_int = 0
		self.section_length_packed = "\x00"*8
		self.options = None
		self.block_total_length_last_int = 0
		self.block_total_length_last_packed = "\x00\x00\x00\x00"

		self.block_size = SECTION_HEADER_BLOCK_BODY_SIZE_FIXED

	def Read(self,inp):
		self.block_type_packed = inp.read(4)
		self.block_type_int = struct.unpack(">I",self.block_type_packed)[0]
		if self.block_type_int != SECTION_HEADER_BLOCK_INT:
			self.is_valid = False
			return

		self.block_total_length_first_packed = inp.read(4)

		self.byte_order_packed = inp.read(4)
		if self.byte_order_packed == "\x1a\x2b\x3c\x4d":
			self.endianness=">"
		elif self.byte_order_packed == "\x4d\x3c\x2b\x1a":
			self.endianness="<"
		else:
			self.is_valid = False

		self.block_total_length_first_int = struct.unpack("%sI" % (self.endianness),self.block_total_length_first_packed)[0]
		
		self.major_version_packed = inp.read(2)
		self.major_version_int = struct.unpack("%sH"%(self.endianness),self.major_version_packed)[0]
		
		self.minor_version_packed = inp.read(2)
		self.minor_version_int = struct.unpack("%sH"%(self.endianness),self.minor_version_packed)[0]
		
		self.section_length_packed = inp.read(8)
		self.section_length_int = struct.unpack("%sq" % (self.endianness),self.section_length_packed)[0]
		
		if self.block_total_length_first_int != self.block_size: 
			self.options = Options(self.section,self.block_type_int)
			self.options.Read(inp)
			self.block_size += self.options.size

		self.block_total_length_last_packed = inp.read(4)
		self.block_total_length_last_int = struct.unpack("%sI" % (self.endianness),self.block_total_length_last_packed)[0]


	def Write(self,out):
		out.write(self.block_type_packed)
		out.write(self.block_total_length_first_packed)
		out.write(self.byte_order_packed)
		out.write(self.major_version_packed)
		out.write(self.minor_version_packed)
		out.write(self.section_length_packed)
		if self.options:
			self.options.Write(out)
		out.write(self.block_total_length_last_packed)

	def __repr__(self):
		ret = ""

		ret+="Block Type: 0x%08x (Section Header)\n" % (self.block_type_int) 
		ret+="Block Total Length First: %d\n" % (self.block_total_length_first_int)
		ret+="Block Total Length Last: %d\n" % (self.block_total_length_last_int)
		if self.byte_order_packed == "\x1a\x2b\x3c\x4d":
			ret+="Byte Order: 0x%s (Big-Endian)\n" % (binascii.hexlify(self.byte_order_packed))
		elif self.byte_order_packed == "\x4d\x3c\x2b\x1a":
			ret+="Byte Order: 0x%s (Little-Endian)\n" % (binascii.hexlify(self.byte_order_packed))
		else:
			ret+="Byte Order: 0x%s (Unknown)\n" % (binascii.hexlify(self.byte_order_packed))
		ret+="Version: %d.%d\n" % (self.major_version_int,self.minor_version_int)
		if self.section_length_int == -1:
			ret+="Section Length: %d (Not Specified)\n" % (self.section_length_int)	
		else:
			ret+="Section Length: %d\n" % (self.section_length_int)

		if self.options:
			ret+="Options\n"
			ret+="\t%s\n" % (("%s"%self.options).replace("\n","\n\t"))

		return ret[:-1]