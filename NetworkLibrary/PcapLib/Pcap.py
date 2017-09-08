from NetworkLibrary.UtilityLib.Utility import *
from NetworkLibrary.UtilityLib.Linktypes import *
from Record import Record

import binascii
import struct
import os

class Pcap:
	'''
		Object to interact with PCAP data. For more details on header information, please see https://wiki.wireshark.org/Development/LibpcapFileFormat

		Args:

		Attributes:
			endianness 				 (str): Endianness of the data to be written or read
			precision 				 (int): Whether MICROSECOND (1) or NANOSECOND (2) precision is used in time formats
			magic_number_packed		 (str): Magic string at beginning of pcap file
			version_major_packed	 (str): Major version string in PCAP header
			version_major_int		 (int): Integer representation of version_major_packed
			version_minor_packed	 (str): Minor version string in PCAP header
			version_minor_int		 (int): Integer representation of version_minor_packed
			this_zone_packed		 (str): This zone string in PCAP header.
			this_zone_int			 (int): Integer representation of this_zone_packed
			sigfigs_packed			 (str): Significant figures string in PCAP header
			sigfigs_int				 (int): Integer representation of sigfigs_packed
			snaplen_packed			 (str): Snapshot length  in PCAP header
			snaplen_int				 (int): Integer representation of snaplen_packed
			network_packed			 (str): Link layer header type in PCAP header
			network_int				 (int): Integer representation of network_packed
			network_string			 (str): Human readable string of link layer type in PCAP
			records 				(list): Record objects representing each captured frame in the PCAP
	'''
	def __init__(self):
		#Metadata about file
		self.endianness = ">"
		self.precision = None

		#Shared properties between reader and writer
		self.magic_number_packed = "\xa1\xb2\xc3\xd4"
		self.version_major_packed = "\x00\x02"
		self.version_major_int = 2
		self.version_minor_packed = "\x00\x04"
		self.version_minor_int = 4
		self.this_zone_packed = "\x00\x00\x00\x00"
		self.this_zone_int = 0
		self.sigfigs_packed = "\x00\x00\x00\x00"
		self.sigfigs_int = 0
		self.snaplen_packed = "\xff\xff\xff\xff"
		self.snaplen_int = 0xffffffff
		self.network_packed = LINKTYPE_ETHERNET_PACKED_BE
		self.network_int = LINKTYPE_ETHERNET_INT
		self.network_string = LINKTYPE_ETHERNET_STRING

		#Data from pcap
		self.records = []

	def ReadFile(self,f):
		'''
			Open and read a pcap file to fill the attributes of this Pcap object

			Args:
				f: A valid path to a PCAP file

			Return:

			Side Effects:
				magic_number_packed
				version_major_packed
				version_major_int
				version_minor_packed
				version_minor_int
				this_zone_packed
				this_zone_int
				sigfigs_packed
				sigfigs_int
				snaplen_packed
				snaplen_int
				network_packed
				network_int
				network_string
				records

			Caught Exceptions
				IOError -> Critical error leading to exit of program
		'''
		try:
			with open(f,'rb') as infile:
				self.ReadHeader(infile)
				for record in self.ReadPacketRecords(infile):
					self.records.append(record)
		except IOError:
			Critical("Unable to open file \"%s\"" % (f))

	def ReadHeader(self,inp):
		'''
			Read a file object and fill the header specific attributes of the pcap object

			Args:
				inp: A file input/output object

			Return:

			Side Effects:
				magic_number_packed
				version_major_packed
				version_major_int
				version_minor_packed
				version_minor_int
				this_zone_packed
				this_zone_int
				sigfigs_packed
				sigfigs_int
				snaplen_packed
				snaplen_int
				network_packed
				network_int
				network_string

			Caught Exceptions
				IOError -> Critical error leading to exit of program
				struct.error -> Critical error leading to exit of program
		'''
		try:
			self.magic_number_packed = inp.read(4)
			if self.magic_number_packed == "\xa1\xb2\xc3\xd4":
				self.endian = ">"
				self.precision = MICROSECOND
			elif self.magic_number_packed == "\xd4\xc3\xb2\xa1":
				self.endian="<"
				self.precision = MICROSECOND
			elif self.magic_number_packed == "\xa1\xb2\x3c\x4d":
				self.endian=">"
				self.precision = NANOSECOND
			elif self.magic_number_packed == "\x4d\x3c\xb2\xa1":
				self.endian="<"
				self.precision = NANOSECOND
			else:
				Critical("Unrecognized file magic %s" % (binascii.hexlify(self.magic_number_packed)))

			self.version_major_packed = inp.read(2)
			self.version_major_int = struct.unpack("%sH" % (self.endian),self.version_major_packed)[0]
			
			self.version_minor_packed = inp.read(2)
			self.version_minor_int = struct.unpack("%sH" % (self.endian),self.version_minor_packed)[0]
			
			self.this_zone_packed = inp.read(4)
			self.this_zone_int = struct.unpack("%si" % (self.endian),self.this_zone_packed)[0]
			
			self.sigfigs_packed = inp.read(4)
			self.sigfigs_int = struct.unpack("%sI" % (self.endian),self.sigfigs_packed)[0]
			
			self.snaplen_packed = inp.read(4)
			self.snaplen_int = struct.unpack("%sI" % (self.endian),self.snaplen_packed)[0]
			
			self.network_packed = inp.read(4)
			self.network_int = struct.unpack("%sI" % (self.endian),self.network_packed)[0]

		except IOError:
			Critical("Unable to read from file %s" % (inp))
		except struct.error:
			Critical("Not enough data to read header")

	def ReadPacketRecords(self,inp):
		'''
			Read a file object for all captured frames in the pcap

			Args:
				inp: A file input/output object

			Return:
				yields records (this function may be used as an iterator to iterate through very large Pcap files)

			Side Effects:
				records

			Caught Exceptions
				struct.error -> Nothing happens
				IOError -> Nothing happens
		'''
		currPtr = inp.tell()
		inp.seek(0,2)
		sizeOfInp = inp.tell()
		inp.seek(currPtr)

		try:
			while inp.tell() < sizeOfInp:
				record = Record(parent=self)
				record.ReadRecord(inp)
				if record.is_valid:
					yield record
		except struct.error:
			None
		except IOError:
			None

	def WriteFile(self,f,force=False):
		try:
			if os.path.isfile(f) and not force:
				ans=raw_input("File \"%s\" exists, would you like to overwrite (y/n)? " %(f))
				if ans not in ['y','Y','yes','Yes']:
					print "We will not overwrite file"
					return

			with open(f,'wb') as outfile:
				self.WriteHeader(outfile)
				self.WritePacketRecords(outfile)
		except IOError:
			Critical("Unable to open file \"%s\"" % (outf))
		except AttributeError:
			Critical("")

	def WriteHeader(self,out):
		try:
			out.write(self.magic_number_packed)
			out.write(self.version_major_packed)
			out.write(self.version_minor_packed)
			out.write(self.this_zone_packed)
			out.write(self.sigfigs_packed)
			out.write(self.snaplen_packed)
			out.write(self.network_packed)
		except IOError:
			Critical("Unable to write to file \"%s\"" % (outf))
		except AttributeError:
			Critical("")

	def WritePacketRecords(self,out):
		for record in self.records:
			record.WriteRecord(out)

	def append(self,packetData):
		'''
			Create a record with data==packetData and append to pcap records
		'''
		self.insert(packetData,len(self.records))
	
	def insert(self,position,packetData):
		'''
			Create a record with data==packetData and insert it into the pcap records list at position
		'''
		rec = Record(self)
		rec.CreateRecord(packetData)
		self.records.insert(position,rec)

	def pop(self,position):
		'''
			Remove record at index==position from pcap
		'''
		try:
			return self.records.pop(position)
		except IndexError:
			return

	def __getitem__(self,key):
		return self.records[key]

	def clear(self):
		'''
			Remove all records from pcap
		'''
		self.records = []

	def __repr__(self):
		ret = ""

		ret += "Magic Number: %s\n" % (binascii.hexlify(self.magic_number_packed))
		ret += "Version: %d.%d\n" % (self.version_major_int,self.version_minor_int)
		ret += "Time zone offset from GMT: %d seconds\n" % (self.this_zone_int)
		ret += "Timestamp accuracy: %d\n" % (self.sigfigs_int)
		if self.precision == MICROSECOND:
			ret += "Timestamp precision: Microseconds\n"
		else:
			ret += "Timestamp precision: Nanoseconds\n"
		ret += "Snapshot Length: %d bytes\n" % (self.snaplen_int)
		ret += "Network Type: %s\n" % (self.network_string)
		ret += "Number of Records: %d\n\n" % (len(self.records))
		for index in xrange(0,len(self.records)):
			ret += "Record %d\n" % (index)
			ret += "-------%s\n" % ("-"*len(str(index)))
			ret += "\t%s\n" % (("%s"%(self.records[index])).replace("\n","\n\t"))
			ret += "\n"

		return ret
