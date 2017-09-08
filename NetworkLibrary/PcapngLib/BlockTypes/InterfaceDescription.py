from NetworkLibrary.PcapngLib.PcapngHelpers import *
from NetworkLibrary.UtilityLib.Linktypes import *
from NetworkLibrary.UtilityLib.Utility import *
from Options import Options

import struct

class InterfaceDescription:
	def __init__(self,section):
		self.section = section
		self.block_type_int = INTERFACE_DESCRIPTION_BLOCK_INT
		self.block_type_packed = struct.pack("%sI" % (self.section.sectionHeader.endianness),self.block_type_int)

		self.block_total_length_first_int = 0
		self.block_total_length_first_packed = "\x00\x00\x00\x00"

		self.link_type_int = 0
		self.link_type_packed = "\x00\x00"
		self.reserved_int = 0
		self.reserved_packed = "\x00\x00"
		self.snaplen_int = 0
		self.snaplen_packed = "\x00\x00\x00\x00"

		self.options = None
		self.block_total_length_last_int = 0
		self.block_total_length_last_packed = "\x00\x00\x00\x00"

		self.block_size = INTERFACE_DESCRIPTION_BLOCK_BODY_SIZE_FIXED

	def Read(self,inp):
		self.block_total_length_first_packed = inp.read(4)
		self.block_total_length_first_int = struct.unpack("%sI" % (self.section.sectionHeader.endianness),self.block_total_length_first_packed)[0]

		self.link_type_packed = inp.read(2)
		self.link_type_int = struct.unpack("%sH"%(self.section.sectionHeader.endianness),self.link_type_packed)[0]
		self.reserved_packed = inp.read(2)
		self.reserved_int = struct.unpack("%sH"%(self.section.sectionHeader.endianness),self.reserved_packed)[0]
		self.snaplen_packed = inp.read(4)
		self.snaplen_int = struct.unpack("%sI"%(self.section.sectionHeader.endianness),self.snaplen_packed)[0]

		if self.block_total_length_first_int != self.block_size:
			self.options = Options(self.section,self.block_type_int)
			self.options.Read(inp)
			self.block_size += self.options.size

		self.block_total_length_last_packed = inp.read(4)
		self.block_total_length_last_int = struct.unpack("%sI" % (self.section.sectionHeader.endianness),self.block_total_length_last_packed)[0]

	def Write(self,out):
		out.write(self.block_total_length_first_packed)
		out.write(self.link_type_packed)
		out.write(self.reserved_packed)
		out.write(self.snaplen_packed)
		if self.options:
			self.options.Write(out)
		out.write(self.block_total_length_last_packed)

	def __repr__(self):
		ret=""
		
		ret+="Block Type: 0x%08x (Interface Description)\n" % (self.block_type_int) 
		ret+="Block Total Length First: %d\n" % (self.block_total_length_first_int)
		ret+="Block Total Length Last: %d\n" % (self.block_total_length_last_int)
		try:
			ret+="Link Type: %s (0x%04x)\n" % (linkTypeIntToStr[self.link_type_int],self.link_type_int)
		except KeyError:
			ret+="Link Type: Unknown (0x%04x)\n" % (self.link_type_int)
		ret+="Reserved: 0x%04x\n" % (self.reserved_int)
		ret+="Snap Length: %d\n" % (self.snaplen_int)
		if self.options:
			ret+="Options\n"
			ret+="\t%s\n" % (("%s"%self.options).replace("\n","\n\t"))

		return ret[:-1]