from NetworkLibrary.PcapngLib.PcapngHelpers import *
from NetworkLibrary.UtilityLib.Utility import *
from Options import Options

import struct

class Packet:
	def __init__(self,section):
		self.section = section
		self.block_type_int = PACKET_BLOCK_INT
		self.block_type_packed = struct.pack("%sI" % (self.section.sectionHeader.endianness),self.block_type_int)

		self.block_total_length_first_int = 0
		self.block_total_length_first_packed = "\x00\x00\x00\x00"

		self.interface_id_packed = "\x00\x00"
		self.interface_id_int = 0
		self.drops_count_packed = "\x00\x00"
		self.drops_count_int = 0
		self.timestamp_high_packed = "\x00\x00\x00\x00"
		self.timestamp_high_int = 0
		self.timestamp_low_packed = "\x00\x00\x00\x00"
		self.timestamp_low_int = 0
		self.captured_len_packed = "\x00\x00\x00\x00"
		self.captured_len_int = 0
		self.packet_len_packed = "\x00\x00\x00\x00"
		self.packet_len_int = 0
		
		self.options = None
		self.block_total_length_last_int = 0
		self.block_total_length_last_packed = "\x00\x00\x00\x00"

		self.block_size = PACKET_BLOCK_BODY_SIZE_FIXED

	def Read(self,inp):
		self.block_total_length_first_packed = inp.read(4)
		self.block_total_length_first_int = struct.unpack("%sI" % (self.section.sectionHeader.endianness),self.block_total_length_first_packed)[0]

		self.interface_id_packed = inp.read(2)
		self.interface_id_int = struct.unpack("%sH"%(self.section.sectionHeader.endianness),self.interface_id_packed)[0]

		self.drops_count_packed = inp.read(2)
		self.drops_count_int = struct.unpack("%sH"%(self.section.sectionHeader.endianness),self.drops_count_packed)[0]

		self.timestamp_high_packed = inp.read(4)
		self.timestamp_high_int = struct.unpack("%sI"%(self.section.sectionHeader.endianness),self.timestamp_high_packed)[0]

		self.timestamp_low_packed = inp.read(4)
		self.timestamp_low_int = struct.unpack("%sI"%(self.section.sectionHeader.endianness),self.timestamp_low_packed)[0]
		
		self.timestamp = (self.timestamp_high_int<<32)|self.timestamp_low_int

		self.captured_len_packed = inp.read(4)
		self.captured_len_int = struct.unpack("%sI"%(self.section.sectionHeader.endianness),self.captured_len_packed)[0]
		
		self.packet_len_packed = inp.read(4)
		self.packet_len_int = struct.unpack("%sI"%(self.section.sectionHeader.endianness),self.packet_len_packed)[0]

		if self.captured_len_int > self.block_total_length_first_int-PACKET_BLOCK_BODY_SIZE_FIXED:
			Warning("EnhancedPacket.Read : self.captured_len_int (%d) exceeds the block boundaries (block size: %d-%d)" % (self.captured_len_int,self.block_total_length_first_int,PACKET_BLOCK_BODY_SIZE_FIXED))
			self.captured_len_int = self.block_total_length_first_int-PACKET_BLOCK_BODY_SIZE_FIXED

		self.packet_data = inp.read(self.captured_len_int)
		self.block_size += len(self.packet_data)

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

	def Write(self,out):
		out.write(self.block_total_length_first_packed)
		out.write(self.interface_id_packed)
		out.write(self.drops_count_packed)
		out.write(self.timestamp_high_packed)
		out.write(self.timestamp_low_packed)
		out.write(self.captured_len_packed)
		out.write(self.packet_len_packed)
		out.write(self.packet_data)
		if self.options:
			self.options.Write(out)
		out.write(self.block_total_length_last_packed)

	def __repr__(self):
		ret=""

		ret+="Block Type: 0x%08x (Packet)\n" % (self.block_type_int) 
		ret+="Block Total Length First: %d\n" % (self.block_total_length_first_int)
		ret+="Block Total Length Last: %d\n" % (self.block_total_length_last_int)
		ret+="Interface Id: %d\n" % (self.interface_id_int)
		ret+="Drops Count: %d\n" % (self.drops_count_int)
		ret+="Timestamp High: 0x%08x (%d)\n" % (self.timestamp_high_int,self.timestamp_high_int)
		ret+="Timestamp Low: 0x%08x (%d)\n" % (self.timestamp_low_int,self.timestamp_low_int)
		#ret+= "Timestamp: %s\n" % ()
		ret+="Captured Length: %d\n" % (self.captured_len_int)
		ret+="Packet Length: %d\n" % (self.packet_len_int)
		ret+="Packet Data\n\t%s\n" % (HexDump(self.packet_data).replace("\n","\n\t"))
		if self.options:
			ret+="Options\n"
			ret+="\t%s\n" % (("%s"%self.options).replace("\n","\n\t"))

		return ret[:-1]