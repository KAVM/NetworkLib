from NetworkLibrary.UtilityLib.Utility import *
import Section

import binascii
import struct
import os
import sys

class Pcapng:
	'''
		Object to interact with PCAP Next Generation data. For more details on header information, please see https://www.winpcap.org/ntar/draft/PCAP-DumpFileFormat.html

		Args:

		Attributes:
			
	'''
	def __init__(self):
		# A pcapng file is a series of sections.
		self.sections=[]

	def ReadFile(self,f):
		try:
			with open(f,'rb') as infile:
				for section in self.ReadSections(infile):
					self.sections.append(section)
		except IOError:
			Critical("Unable to open file \"%s\"" % (f))

	def ReadSections(self,inp):
		currPtr = inp.tell()
		inp.seek(0,2)
		sizeOfInp = inp.tell()
		inp.seek(currPtr)

		while inp.tell() < sizeOfInp:
			section = Section.Section()
			section.Read(inp)
			yield section

	def WriteFile(self,f,force=False):
		try:
			if os.path.isfile(f) and not force:
				ans=raw_input("File \"%s\" exists, would you like to overwrite (y/n)? " %(f))
				if ans not in ['y','Y','yes','Yes']:
					print "We will not overwrite file"
					return

			with open(f,'wb') as outfile:
				self.WriteSections(outfile)
		except IOError:
			Critical("Unable to open file \"%s\"" % (outf))
		except AttributeError:
			Critical("")

	def WriteSections(self, out):
		for section in self.sections:
			section.Write(out)

	def __repr__(self):
		ret = ""

		ret += "Number of Sections: %d\n" % (len(self.sections))
		for index in xrange(len(self.sections)):
			ret += "Section %d\n" % (index)
			ret += "--------%s\n" % ("-"*len(str(index)))
			ret += "\t%s\n" % (("%s" % (self.sections[index])).replace("\n","\n\t"))

		return ret[:-1]