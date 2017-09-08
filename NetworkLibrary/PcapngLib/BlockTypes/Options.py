from NetworkLibrary.UtilityLib.Utility import *
from NetworkLibrary.PcapngLib.PcapngHelpers import *
import struct

class Options:
	def __init__(self,section,blockType):
		self.section = section
		self.options_dict_type = blockType
		self.options = []
		self.size = 0

	def Read(self,inp):
		start = inp.tell()

		opCode = struct.unpack("%sH"%(self.section.sectionHeader.endianness),inp.read(2))[0]
		length = struct.unpack("%sH"%(self.section.sectionHeader.endianness),inp.read(2))[0]
		while not (opCode == 0 and length==0):
			value = inp.read(length)
			self.options.append((opCode,length,value))

			if length%4:
				inp.read(4-(length%4))

			opCode = struct.unpack("%sH"%(self.section.sectionHeader.endianness),inp.read(2))[0]
			length = struct.unpack("%sH"%(self.section.sectionHeader.endianness),inp.read(2))[0]

		self.options.append((opCode,length,""))

		self.size = inp.tell()-start

	def Write(self,out):
		for opcode,length,value in self.options:
			out.write(struct.pack("%sH" % (self.section.sectionHeader.endianness),opcode))
			out.write(struct.pack("%sH" % (self.section.sectionHeader.endianness),length))
			out.write(value)

	def __repr__(self):
		ret = ""

		for opcode,length,value in self.options:
			try:
				ret += "Opcode: 0x%04x (%s)\n" % (opcode,options_opcode_to_str[self.options_dict_type][opcode])
			except KeyError:
				ret += "Opcode: 0x%04x (%d)\n" % (opcode,opcode)
			ret += "Length: 0x%04x (%d)\n" % (length,length)
			if value:
				try:
					ret += "Value: %s\n" % (options_value_to_str[self.options_dict_type][opcode](value))
				except KeyError:
					ret += "Value:\n\t%s\n" % (HexDump(value).replace("\n","\n\t"))

			ret += "\n"

		return ret[:-2]