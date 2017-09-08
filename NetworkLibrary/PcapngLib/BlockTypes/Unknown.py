from NetworkLibrary.UtilityLib.Utility import *

class Unknown:
	def __init__(self,section,blockType):
		self.section = section
		self.block_type_int = blockType

		self.block_type_packed = struct.pack("%sI" % (self.section.sectionHeader.endianness),self.block_type_int)
		self.block_total_length_first_int = 0
		self.block_total_length_first_packed = "\x00\x00\x00\x00"
		self.block_body = ""
		self.block_total_length_last_int = 0
		self.block_total_length_last_packed = "\x00\x00\x00\x00"

		self.block_size =12

	def Read(self,inp):
		self.block_total_length_first_packed = inp.read(4)

		self.block_total_length_first_int = struct.unpack("%sI" % (self.section.sectionHeader.endianness),self.block_total_length_first_packed)[0]
		self.block_body = inp.read(self.block_total_length_first_int-12)
		self.block_total_length_last_packed = inp.read(4)
		self.block_total_length_last_int = struct.unpack("%sI" % (self.section.sectionHeader.endianness),self.block_total_length_last_packed)[0]
		self.block_size = 12 + len(self.block_body)

	def Write(self,out):
		out.write(self.block_type_packed)
		out.write(self.block_totoal_length_first_packed)
		out.write(self.block_body)
		out.write(self.block_total_length_last_packed)

	def __repr__(self):
		ret =""

		ret += "Block Type					: 0x%08x (Unknown)\n" % (self.block_type_int)
		ret += "Block Total Length First	: %d\n" % (self.block_total_length_first_int)
		ret += "Block Data\n\t%s\n" % (HexDump(self.block_body).replace("\n","\n\t"))
		ret += "Block Total Length Last		: %d" % (self.block_total_length_last_int)

		return ret