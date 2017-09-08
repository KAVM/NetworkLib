from NetworkLibrary.UtilityLib.Utility import *
import struct
import datetime

class Record:
	def __init__(self,parent, timestamp_seconds=0, timestamp_precision=0, capture_length=0, original_length=0, data=""):
		self.is_valid = True
		self.truncated = False
		self.parent = parent
		
		self.timestamp_seconds_int = timestamp_seconds&0xffffffff
		self.timestamp_seconds_packed = struct.pack("%sI" % (self.parent.endian),self.timestamp_seconds_int)

		self.timestamp_precision_int = timestamp_precision&0xffffffff
		self.timestamp_precision_packed = struct.pack("%sI" % (self.parent.endian),self.timestamp_precision_int)

		self.capture_length_int = capture_length&0xffffffff
		self.capture_length_packed = struct.pack("%sI" % (self.parent.endian),self.capture_length_int)
		
		self.original_length_int = original_length&0xffffffff
		self.original_length_packed = struct.pack("%sI" % (self.parent.endian),self.original_length_int)

		if self.capture_length_int < self.original_length_int:
			self.truncated = True

		self.data = data

	def ReadRecord(self,inp):
		try:
			self.timestamp_seconds_packed = inp.read(4)
			self.timestamp_seconds_int = struct.unpack("%sI" % (self.parent.endian),self.timestamp_seconds_packed)[0]

			self.timestamp_precision_packed = inp.read(4)
			self.timestamp_precision_int = struct.unpack("%sI" % (self.parent.endian),self.timestamp_precision_packed)[0]

			self.capture_length_packed = inp.read(4)
			self.capture_length_int = struct.unpack("%sI" % (self.parent.endian),self.capture_length_packed)[0]

			self.original_length_packed = inp.read(4)
			self.original_length_int = struct.unpack("%sI" % (self.parent.endian),self.original_length_packed)[0]

			if self.capture_length_int < self.original_length_int:
				self.truncated = True

			self.data = inp.read(self.capture_length_int)
		except struct.error:
			self.is_valid = False

	def WriteRecord(self,out):
		out.write(self.timestamp_seconds_packed)
		out.write(self.timestamp_precision_packed)
		out.write(self.capture_length_packed)
		out.write(self.original_length_packed)
		out.write(self.data)

	def CreateRecord(self,data):
		timenow = (datetime.datetime.utcnow()-datetime.datetime(1970,1,1))
		
		self.timestamp_seconds_int = int(timenow.total_seconds())
		self.timestamp_seconds_packed = struct.pack("%sI" % (self.parent.endian),self.timestamp_seconds_int)
		
		self.timestamp_precision_int = timenow.microseconds
		self.timestamp_precision_packed = struct.pack("%sI" % (self.parent.endian),self.timestamp_precision_int)

		self.capture_length_int = len(data)
		self.capture_length_packed = struct.pack("%sI" % (self.parent.endian),self.capture_length_int)

		self.original_length_int = len(data)
		self.original_length_packed = struct.pack("%sI" % (self.parent.endian),self.original_length_int)

		self.data = data

	def SetTimestampSeconds(self,ts):
		self.timestamp_seconds_int = ts&0xffffffff
		self.timestamp_seconds_packed = struct.pack("%sI" % (self.parent.endian),self.timestamp_seconds_int)

	def SetTimestampPrecision(self,tsp):
		self.timestamp_precision_int = tsp&0xffffffff
		self.timestamp_precision_packed = struct.pack("%sI" % (self.parent.endian),self.timestamp_precision_int)

	def SetCaptureLength(self,cap):
		self.capture_length_int = cap&0xffffffff
		self.capture_length_packed = struct.pack("%sI" % (self.parent.endian),self.capture_length_int)

	def SetOriginalLength(self,orig):
		self.original_length_int = orig&0xffffffff
		self.original_length_packed = struct.pack("%sI" % (self.parent.endian),self.original_length_int)

	def SetData(self,data):
		self.data=data

	def __repr__(self):
		ret = ""

		timeString = (datetime.datetime(1970,1,1)+datetime.timedelta(seconds=self.timestamp_seconds_int)).strftime("%m/%d/%Y %H:%M:%S")
		if self.parent.precision == MICROSECOND:
			timeString += ":%06d" % (self.timestamp_precision_int)
		else:
			timeString += ":%09d" % (self.timestamp_precision_int)
		timeString += " GMT"
		if self.parent.this_zone_int < 0:
			timeString+=" +"
			timeString += (datetime.datetime(1970,1,1)+datetime.timedelta(seconds=-1*self.parent.this_zone_int)).strftime("%H:%M:%S")
		elif self.parent.this_zone_int > 0:
			timeString +=" -"
			timeString += (datetime.datetime(1970,1,1)+datetime.timedelta(seconds=self.parent.this_zone_int)).strftime("%H:%M:%S")

		ret += "Timestamp       : %s\n" % (timeString)
		ret += "Capture Length  : %d bytes\n" % (self.capture_length_int)
		ret += "Original Length : %d bytes\n" % (self.original_length_int)
		ret += "Data:\n\t%s" % (HexDump(s=self.data,width=16).replace("\n","\n\t"))

		return ret