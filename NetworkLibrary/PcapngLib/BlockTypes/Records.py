from NetworkLibrary.UtilityLib.Utility import *
from NetworkLibrary.PcapngLib.PcapngHelpers import *
import struct

class Records:
	def __init__(self,section):
		self.section = section
		self.records = []
		self.size = 0

	def Read(self,inp):
		start = inp.tell()

		recordType = struct.unpack("%sH"%(self.section.sectionHeader.endianness),inp.read(2))[0]
		recordLength = struct.unpack("%sH"%(self.section.sectionHeader.endianness),inp.read(2))[0]
		while not (recordType == 0 and recordLength == 0):
			value = inp.read(recordLength)
			self.records.append((recordType,recordLength,value))

			if recordLength%4:
				inp.read(4-(recordLength%4))
			recordType = struct.unpack("%sH"%(self.section.sectionHeader.endianness),inp.read(2))[0]
			recordLength = struct.unpack("%sH"%(self.section.sectionHeader.endianness),inp.read(2))[0]

		self.records.append((recordType,recordLength,""))

		self.size = inp.tell()-start

	def Write(self,out):
		for recordType,recordLength,value in self.records:
			out.write(struct.pack("%sH" % (self.section.sectionHeader.endianness),recordType))
			out.write(struct.pack("%sH" % (self.section.sectionHeader.endianness),recordLength))
			out.write(value)

	def __repr__(self):
		ret = ""

		for recordType,recordLength,value in self.records:
			try:
				ret += "Type: 0x%04x (%s)\n" % (recordType,records_type_to_str[recordType])
			except KeyError:
				ret += "Type: 0x%04x (%d)\n" % (recordType,recordType)
			ret += "Length: 0x%04x (%d)\n" % (recordLength,recordLength)
			if value:
				try:
					ret += "Value: %s\n" % (record_value_to_str[recordType](value))
				except KeyError:
					ret += "Value:\n\t%s\n" % (HexDump(value).replace("\n","\n\t"))

			ret += "\n"

		return ret[:-2]