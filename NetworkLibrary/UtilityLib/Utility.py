import traceback
from StringIO import StringIO
import struct
import binascii
import sys

MICROSECOND = 1
NANOSECOND = 2

def Critical(s):
	out=StringIO()
	traceback.print_exc(file=out)
	sys.stderr.write("%s\n" % (s))
	sys.stderr.write("%s\n" % (out.getvalue()))
	out.close()
	sys.exit()

def Warning(s):
	sys.stderr.write("WARNING : %s\n" % (s))

def HexDump(s,width = 16):
	ret = ""

	for c in xrange(0,len(s),width):
		currString = s[c:c+width]

		ret += "0x%08x |" % (c)
		for char in currString:
			ret += "%02x " % (ord(char))
		for i in xrange(0,width-len(currString)):
			ret += "   "
		ret += "|"
		for char in currString:
			if ord(char) >= 32 and ord(char)<=126:
				ret+=char
			else:
				ret+="."
		for i in xrange(0,width-len(currString)):
			ret += " "
		
		ret += "|\n"

	return ret[:-1]

def GetDate(i,degree=6):
	

	if degree == 6:
		delta = datetime.timedelta(microseconds=i)

	retDate = epoch+delta

	return retDate.strftime("%d %B %Y %H:%M:%S:%fZ")