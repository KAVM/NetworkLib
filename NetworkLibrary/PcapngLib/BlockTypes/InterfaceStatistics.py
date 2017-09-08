from NetworkLibrary.PcapngLib.PcapngHelpers import *
from NetworkLibrary.UtilityLib.Utility import *
from Options import Options

import struct

class InterfaceStatistics:
	def __init__(self,section):
		self.section = section
		self.block_type_int = INTERFACE_STATISTICS_BLOCK_INT
		self.block_type_packed = struct.pack("%sI" % (self.section.sectionHeader.endianness),self.block_type_int)

		self.block_total_length_first_int = 0
		self.block_total_length_first_packed = "\x00\x00\x00\x00"

		self.interface_id_packed = "\x00\x00\x00\x00"
		self.interface_id_int = 0
		self.timestamp_high_packed = "\x00\x00\x00\x00"
		self.timestamp_high_int = 0
		self.timestamp_low_packed = "\x00\x00\x00\x00"
		self.timestamp_low_int = 0
		
		self.options = None
		self.block_total_length_last_int = 0
		self.block_total_length_last_packed = "\x00\x00\x00\x00"

		self.block_size = INTERFACE_STATISTICS_BLOCK_BODY_SIZE_FIXED

	def Read(self,inp):
		self.block_total_length_first_packed = inp.read(4)
		self.block_total_length_first_int = struct.unpack("%sI" % (self.section.sectionHeader.endianness),self.block_total_length_first_packed)[0]

		self.interface_id_packed = inp.read(4)
		self.interface_id_int = struct.unpack("%sI"%(self.section.sectionHeader.endianness),self.interface_id_packed)[0]

		self.timestamp_high_packed = inp.read(4)
		self.timestamp_high_int = struct.unpack("%sI"%(self.section.sectionHeader.endianness),self.timestamp_high_packed)[0]

		self.timestamp_low_packed = inp.read(4)
		self.timestamp_low_int = struct.unpack("%sI"%(self.section.sectionHeader.endianness),self.timestamp_low_packed)[0]
		
		self.timestamp = (self.timestamp_high_int<<32)|self.timestamp_low_int

		if self.block_total_length_first_int != self.block_size:
			self.options = Options(self.section,self.block_type_int)
			self.options.Read(inp)
			self.block_size += self.options.size

		self.block_total_length_last_packed = inp.read(4)
		self.block_total_length_last_int = struct.unpack("%sI" % (self.section.sectionHeader.endianness),self.block_total_length_last_packed)[0]

	def __repr__(self):
		ret = ""

		ret+="Block Type: 0x%08x (Interface Statistics)\n" % (self.block_type_int) 
		ret+="Block Total Length First: %d\n" % (self.block_total_length_first_int)
		ret+="Block Total Length Last: %d\n" % (self.block_total_length_last_int)
		ret+="Interface Id: %d\n" % (self.interface_id_int)
		ret+="Timestamp High: 0x%08x (%d)\n" % (self.timestamp_high_int,self.timestamp_high_int)
		ret+="Timestamp Low: 0x%08x (%d)\n" % (self.timestamp_low_int,self.timestamp_low_int)
		#ret+= "Timestamp: %s\n" % ()
		if self.options:
			ret+="Options\n"
			ret+="\t%s\n" % (("%s"%self.options).replace("\n","\n\t"))

		return ret[:-1]