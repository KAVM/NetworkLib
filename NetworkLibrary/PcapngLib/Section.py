from NetworkLibrary.UtilityLib.Utility import *
from NetworkLibrary.UtilityLib.Linktypes import *
from PcapngHelpers import *
from BlockTypes import *

import binascii
import struct
import os
import sys

class Section:
	'''
		A section contains a section header, interfaces, and blocks associated with interfaces

		Args:

		Attributes:
			
	'''
	def __init__(self):
		self.sectionHeader = None
		self.blocks = []
		self.interfaces = []

	def Read(self,inp):
		self.ReadSectionHeader(inp)
		self.ReadBlocks(inp)

	def ReadSectionHeader(self,inp):
		start = inp.tell()
		self.sectionHeader = SectionHeader.SectionHeader(self)
		self.sectionHeader.Read(inp)
		if not self.sectionHeader.is_valid:
			Critical("Section.ReadSectionHeader : Block at offset %d was not a section header!\nBlock 1:\n\t%s"%(start,("%s"%(self.sectionHeader)).replace("\n","\n\t")))
		self.blocks.append(self.sectionHeader)

	def ReadBlocks(self,inp):
		currPtr = inp.tell()
		inp.seek(0,2)
		sizeOfInp = inp.tell()
		inp.seek(currPtr)

		if inp.tell() < sizeOfInp - 4:
			blockType = inp.read(4)
			inp.seek(-4,1)

		while inp.tell() < sizeOfInp-4 and blockType != SECTION_HEADER_BLOCK_PACKED:
			block=self.ReadBlock(inp)
			block.Read(inp)
			self.blocks.append(block)

			if self.blocks[-1].block_total_length_last_int != self.blocks[-1].block_total_length_first_int:
				Warning("Total block lengths (first %d and last %d) do not match. File may be corrupt!" % (self.blocks[-1].block_total_length_first_int,self.blocks[-1].block_total_length_last_int))

			if self.blocks[-1].block_type_int == INTERFACE_DESCRIPTION_BLOCK_INT:
				self.interfaces.append(self.blocks[-1])

			if inp.tell() < sizeOfInp - 4:
				blockType = inp.read(4)
				inp.seek(-4,1)
			
	def ReadBlock(self,inp):
		blockType = struct.unpack("%sI"%(self.sectionHeader.endianness),inp.read(4))[0]

		if blockType == INTERFACE_DESCRIPTION_BLOCK_INT:
			blockObject = InterfaceDescription.InterfaceDescription(self)
		elif blockType == ENHANCED_PACKET_BLOCK_INT:
			blockObject = EnhancedPacket.EnhancedPacket(self)
		elif blockType == SIMPLE_PACKET_BLOCK_INT:
		 	blockObject = SimplePacket.SimplePacket(self)
		elif blockType == NAME_RESOLUTION_BLOCK_INT:
		 	blockObject = NameResolution.NameResolution(self)
		elif blockType == INTERFACE_STATISTICS_BLOCK_INT:
		 	blockObject = InterfaceStatistics.InterfaceStatistics(self)
		elif blockType == PACKET_BLOCK_INT:
		 	blockObject = Packet.Packet(self)
		else:
			Warning("Unrecognized Block Type: 0x%08x" % (blockType))
			blockObject = Unknown.Unknown(self,blockType)

		return blockObject

	def __repr__(self):
		ret =""

		for blockIndex in xrange(len(self.blocks)):
			ret += "Block %d\n" % (blockIndex)
			ret += "--------%s\n" % ("-"*len(str(blockIndex)))
			ret += "\t%s\n\n" % (("%s"%(self.blocks[blockIndex])).replace("\n","\n\t"))

		return ret