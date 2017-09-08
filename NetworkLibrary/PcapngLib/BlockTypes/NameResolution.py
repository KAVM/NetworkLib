from NetworkLibrary.PcapngLib.PcapngHelpers import *
from NetworkLibrary.UtilityLib.Utility import *
from Options import Options
from Records import Records

import struct

class NameResolution:
	def __init__(self,section):
		self.section = section
		self.block_type_int = NAME_RESOLUTION_BLOCK_INT
		self.block_type_packed = struct.pack("%sI" % (self.section.sectionHeader.endianness),self.block_type_int)

		self.block_total_length_first_int = 0
		self.block_total_length_first_packed = "\x00\x00\x00\x00"

		self.records = None

		self.options = None
		self.block_total_length_last_int = 0
		self.block_total_length_last_packed = "\x00\x00\x00\x00"

		self.block_size = NAME_RESOLUTION_BLOCK_BODY_SIZE_FIXED

	def Read(self,inp):
		self.block_total_length_first_packed = inp.read(4)
		self.block_total_length_first_int = struct.unpack("%sI" % (self.section.sectionHeader.endianness),self.block_total_length_first_packed)[0]

		self.records = Records(self.section)
		self.records.Read(inp)
		self.block_size += self.records.size
		
		#Align to 32 bit boundary
		while self.block_size%4 != 0 :
			self.block_size += 1
			inp.read(1)

		if self.block_total_length_first_int != self.block_size:
			self.options = Options(self.section,self.block_type_int)
			self.options.Read(inp)
			self.block_size += self.options.size

		self.block_total_length_last_packed = inp.read(4)
		self.block_total_length_last_int = struct.unpack("%sI" % (self.section.sectionHeader.endianness),self.block_total_length_last_packed)[0]

		if self.block_total_length_last_int != self.block_total_length_first_int:
			Warning("Total block lengths (first %d and last %d) do not match. File may be corrupt!" % (self.block_total_length_first_int,self.block_total_length_last_int))

	def Write(self,out):
		out.write(self.block_total_length_first_packed)
		if self.records:
			self.records.Write(out)
		if self.options:
			self.options.Write(out)
		out.write(self.block_total_length_last_packed)

	def __repr__(self):
		ret=""

		ret+="Block Type: 0x%08x (Name Resolution)\n" % (self.block_type_int) 
		ret+="Block Total Length First: %d\n" % (self.block_total_length_first_int)
		ret+="Block Total Length Last: %d\n" % (self.block_total_length_last_int)
		if self.records:
			ret += "Records\n"
			ret+="\t%s\n" % (("%s"%self.records).replace("\n","\n\t"))
		if self.options:
			ret+="Options\n"
			ret+="\t%s\n" % (("%s"%self.options).replace("\n","\n\t"))

		return ret[:-1]