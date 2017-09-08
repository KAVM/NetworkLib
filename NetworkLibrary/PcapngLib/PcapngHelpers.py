import struct
import binascii
 
blockTypeIntToStr = {
	0x1:"INTERFACE_DESCRIPTION_BLOCK",
	0x2:"PACKET_BLOCK",
	0x3:"SIMPLEPACKET_BLOCK",
	0x4:"NAME_RESOLUTION_BLOCK",
	0x5:"INTERFACE_STATISTICS_BLOCK",
	0x6:"ENHANCED_PACKET_BLOCK",
	0x0a0d0d0a:"SECTION_HEADER_BLOCK"
}

INTERFACE_DESCRIPTION_BLOCK_INT=0x1
INTERFACE_DESCRIPTION_BLOCK_PACKED_BE=struct.pack(">I",0x1)
INTERFACE_DESCRIPTION_BLOCK_PACKED_LE=struct.pack("<I",0x1)
INTERFACE_DESCRIPTION_BLOCK_STRING="INTERFACE_DESCRIPTION_BLOCK"
INTERFACE_DESCRIPTION_BLOCK_BODY_SIZE_FIXED = 20

PACKET_BLOCK_INT=0x2
PACKET_BLOCK_PACKED_BE=struct.pack(">I",0x2)
PACKET_BLOCK_PACKED_LE=struct.pack("<I",0x2)
PACKET_BLOCK_STRING="PACKET_BLOCK"
PACKET_BLOCK_BODY_SIZE_FIXED = 32

SIMPLE_PACKET_BLOCK_INT=0x3
SIMPLE_PACKET_BLOCK_PACKED_BE=struct.pack(">I",0x3)
SIMPLE_PACKET_BLOCK_PACKED_LE=struct.pack("<I",0x3)
SIMPLE_PACKET_BLOCK_STRING="SIMPLE_PACKET_BLOCK"
SIMPLE_PACKET_BLOCK_BODY_SIZE_FIXED = 16

NAME_RESOLUTION_BLOCK_INT=0x4
NAME_RESOLUTION_BLOCK_PACKED_BE=struct.pack(">I",0x4)
NAME_RESOLUTION_BLOCK_PACKED_LE=struct.pack("<I",0x4)
NAME_RESOLUTION_BLOCK_STRING="NAME_RESOLUTION_BLOCK"
NAME_RESOLUTION_BLOCK_BODY_SIZE_FIXED = 12

INTERFACE_STATISTICS_BLOCK_INT=0x5
INTERFACE_STATISTICS_BLOCK_PACKED_BE=struct.pack(">I",0x5)
INTERFACE_STATISTICS_BLOCK_PACKED_LE=struct.pack("<I",0x5)
INTERFACE_STATISTICS_BLOCK_STRING="INTERFACE_STATISTICS_BLOCK"
INTERFACE_STATISTICS_BLOCK_BODY_SIZE_FIXED = 24

ENHANCED_PACKET_BLOCK_INT=0x6
ENHANCED_PACKET_BLOCK_PACKED_BE=struct.pack(">I",0x6)
ENHANCED_PACKET_BLOCK_PACKED_LE=struct.pack("<I",0x6)
ENHANCED_PACKET_BLOCK_STRING="ENHANCED_PACKET_BLOCK"
ENHANCED_PACKET_BLOCK_BODY_SIZE_FIXED = 32

SECTION_HEADER_BLOCK_INT=0x0a0d0d0a
SECTION_HEADER_BLOCK_PACKED=struct.pack(">I",0x0a0d0d0a)
SECTION_HEADER_BLOCK_STRING="SECTION_HEADER_BLOCK"
SECTION_HEADER_BLOCK_BODY_SIZE_FIXED = 28

options_opcode_to_str = {
	0x00000001:{
		0x0:"opt_endofopt",
		0x1:"opt_comment",
		0x2:"if_name",
		0x3:"if_description",
		0x4:"if_IPv4addr",
		0x5:"if_IPv6addr",
		0x6:"if_MACaddr",
		0x7:"if_EUIaddr",
		0x8:"if_speed",
		0x9:"if_tsresol",
		10:"if_tzone",
		11:"if_filter",
		12:"if_os",
		13:"if_fcslen",
		14:"if_tsoffset"
	},
	0x00000002:{
		0x0:"opt_endofopt",
		0x1:"opt_comment",
		0x2:"pack_flags",
		0x3:"pack_hash",
	},
	0x00000003:{
		0x0:"opt_endofopt",
		0x1:"opt_comment",
	},
	0x00000004:{
		0x0:"opt_endofopt",
		0x1:"opt_comment",
		0x2:"ns_dnsname",
		0x3:"ns_dnsIP4addr",
		0x4:"ns_dnsIP6addr",
	},
	0x00000005:{
		0x0:"opt_endofopt",
		0x1:"opt_comment",
		0x2:"isb_starttime",
		0x3:"isb_endtime",
		0x4:"isb_ifrecv",
		0x5:"isb_ifdrop",
		0x6:"isb_filteraccept",
		0x7:"isb_osdrop",
		0x8:"isb_usrdeliv",
	},
	0x00000006:{
		0x0:"opt_endofopt",
		0x1:"opt_comment",
		0x2:"epb_flags",
		0x3:"epb_hash",
		0x4:"epb_dropcount",
	},
	0x0a0d0d0a:{
		0x0:"opt_endofopt",
		0x1:"opt_comment",
		0x2:"shb_hardware",
		0x3:"shb_os",
		0x4:"shb_userappl",
	}
}

records_type_to_str = {
	0x0000:"nres_endofrecord",
	0x0001:"nres_ip4record",
	0x0002:"nres_ip6record"
}

def opt_if_tsresol(v):
	val = struct.unpack(">B",v[0])[0]
	try:
		if val&0x7f == 3:
			return "0x%02x (Timestamp precision is milliseconds)" % (val)
		elif val&0x7f == 6:
			return "0x%02x (Timestamp precision is microseconds)" % (val)
		elif val&0x7f == 9:
			return "0x%02x (Timestamp precision is nanoseconds)" % (val)
		else:
			return "Timestamp precision is 10^-%d seconds" % (val&0x7f)
	except ValueError:
		return "Invalid type for option if_tsresol: %s" % (binascii.hexlify(val))

options_value_to_str = {
	0x00000001:{
		0x9:lambda x : opt_if_tsresol(x)
	},
	0x00000002:{
	},
	0x00000003:{
	},
	0x00000004:{
	},
	0x00000005:{
	},
	0x00000006:{
	},
	0x0a0d0d0a:{
	}
}

record_value_to_str = {
}