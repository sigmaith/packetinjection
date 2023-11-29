#!/usr/bin/env python

import dpkt
import socket
import sys
import os
import struct

import string
import time

# Some DNS constants 
_MDNS_LO_ADDR = '127.0.0.1'
_MDNS_ADDR = '224.0.0.251'
_MDNS_PORT = 5353;
_DNS_PORT = 53;
_DNS_TTL = 60 * 60; # one hour default TTL

# Version number for klee
version_no=3

PKT_FILTER1="_http._tcp.local"
KLEE_MODEL_VERSION="model_version"

# Type of Symbolic variable in mdns
MDNS_FLAG_FIELD="msg_flag"
MDNS_QUESTIONS_FIELD="msg_questions"
MDNS_AN_RRS_FIELD="msg_anrrs"
MDNS_AU_RRS_FIELD="msg_aurrs"
MDNS_ADD_RRS_FIELD="msg_addrrs"
MDNS_QUERIES_NAME_FIELD="msg_queries"
MDNS_QUERIES_DOMAIN_FIELD="msg_domain"
MDNS_ANSWERS_FIELD="msg_answers"
MDNS_ADDREC_FIELD="msg_addrecords"
MDNS_RR_INSTANCE="msg_insance"
MDNS_RR_SERVICE="msg_service"
MDNS_RR_DOMAIN="msg_domain"
MDNS_RR_TYPE="msg_type"
MDNS_RR_CLASS="msg_class"
MDNS_OFFSET_FIELD="sym-"

# Position of MDNS fields
MDNS_FLAG_POS=2
MDNS_QUESTIONS_POS=4
MDNS_AN_RRS_POS=6
MDNS_AU_RRS_POS=8
MDNS_ADD_RRS_POS=10
MDNS_QUERIES_NAME_POS=12
MDNS_QUERIES_DOMAIN_POS=24
MDNS_ANSWERS_POS=12
MDNS_ADDREC_POS=12
MDNS_OFFSET_POS=9999
MDNS_RR_INSTANCE_POS=13
MDNS_RR_SERVICE_POS=19
MDNS_RR_DOMAIN_POS=24
MDNS_RR_TYPE_POS=30
MDNS_RR_CLASS_POS=32


# Length of MDNS fields
MDNS_FLAG_LEN=2
MDNS_QUESTIONS_LEN=2
MDNS_AN_RRS_LEN=2
MDNS_AU_RRS_LEN=2
MDNS_ADD_RRS_LEN=2
MDNS_QUERIES_NAME_LEN=18
MDNS_QUERIES_DOMAIN_LEN=5
MDNS_ANSWERS_LEN=0
MDNS_ADDREC_LEN=0
MDNS_RR_INSTANCE_LEN=5
MDNS_RR_SERVICE_LEN=4
MDNS_RR_DOMAIN_LEN=5
MDNS_RR_TYPE=2
MDNS_RR_CLASS=2



class ZeroMdns(object):
   def __init__(self, bindaddress=None):

      self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
      self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255) 
      self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton("127.0.0.1"))

   def send(self, out, addr = _MDNS_ADDR, port = _MDNS_PORT):
   #"""Sends an outgoing packet."""
   # This is a quick test to see if we can parse the packets we generate
   #temp = DNSIncoming(out.packet())
#      print "Now send packet"
      try:
         bytes_sent = self.socket.sendto(out, (addr, port))
      except:
   # Ignore this, it may be a temporary loss of network connection
         print "Error"
         pass

   def close(self):
   #"""Ends the background threads, and prevent this instance from
   #servicing further queries."""
      self.socket.close()

class KTestError(Exception):
    pass

class KTest:
    @staticmethod
    def fromfile(path):
        if not os.path.exists(path):
            print "ERROR: file %s not found" % (path)
            sys.exit(1)
            
        f = open(path,'rb')
        hdr = f.read(5)
        if len(hdr)!=5 or (hdr!='KTEST' and hdr != "BOUT\n"):
            raise KTestError,'unrecognized file'
        version, = struct.unpack('>i', f.read(4))
        if version > version_no:
            raise KTestError,'unrecognized version'
        numArgs, = struct.unpack('>i', f.read(4))
        args = []
        for i in range(numArgs):
            size, = struct.unpack('>i', f.read(4))
            args.append(f.read(size))
            
        if version >= 2:
            symArgvs, = struct.unpack('>i', f.read(4))
            symArgvLen, = struct.unpack('>i', f.read(4))
        else:
            symArgvs = 0
            symArgvLen = 0

        numObjects, = struct.unpack('>i', f.read(4))
        objects = []
        for i in range(numObjects):
            size, = struct.unpack('>i', f.read(4))
            name = f.read(size)
            size, = struct.unpack('>i', f.read(4))
            bytes = f.read(size)
            objects.append( (name,bytes) )

        # Create an instance
        b = KTest(version, args, symArgvs, symArgvLen, objects)
        # Augment with extra filename field
        b.filename = path
        return b
    
    def __init__(self, version, args, symArgvs, symArgvLen, objects):
        self.version = version
        self.symArgvs = symArgvs
        self.symArgvLen = symArgvLen
        self.args = args
        self.objects = objects

        # add a field that represents the name of the program used to
        # generate this .ktest file:
        program_full_path = self.args[0]
        program_name = os.path.basename(program_full_path)
        # sometimes program names end in .bc, so strip them
        if program_name.endswith('.bc'):
          program_name = program_name[:-3]
        self.programName = program_name
        
def trimZeros(str):
    for i in range(len(str))[::-1]:
        if str[i] != '\x00':
            return str[:i+1]
    return ''


# Get a wanted packet from pcap file
# The packet will be manipulated in order to inject it to network
def get_packet( pcap_file ):

   f = open(pcap_file)
   pcap = dpkt.pcap.Reader(f)
 
   for ts, buf in pcap:
 # make sure we are dealing with IP traffic
 # ref: http://www.iana.org/assignments/ethernet-numbers
      try: eth = dpkt.ethernet.Ethernet(buf)
      except: continue
      if eth.type != 2048: continue

 # make sure we are dealing with UDP
 # ref: http://www.iana.org/assignments/protocol-numbers/
      try: ip = eth.data
      except: continue
      if ip.p != 17: continue

 # filter on UDP assigned ports for DNS
 # ref: http://www.iana.org/assignments/port-numbers
      try: udp = ip.data
      except: continue
#   if udp.sport != 5353 or udp.dport != 5353: continue
      if udp.dport != 5353: continue

 # make the dns object out of the udp data and check for it being a RR (answer)
 # and for opcode QUERY (I know, counter-intuitive)
      try: dns = dpkt.dns.DNS(udp.data)
      except: continue
      if dns.qr != dpkt.dns.DNS_Q: continue	# only pass query
      if dns.opcode != dpkt.dns.DNS_QUERY: continue	# only pass opcode is DNS_QUERY(0000) 

      if len(dns.qd) != 1: continue	# only pass query with just one query

 # now we're going to process and spit out responses based on record type
 # ref: http://en.wikipedia.org/wiki/List_of_DNS_record_types
      if dns.qd[0].name != PKT_FILTER1: continue	# only pass the packet having "_http._tcp.local" as its name

#      for query_data in dns.qd:
#         print "DNS request", query_data.name, "DNS type", query_data.type

      return ip


##########################################################################################
# Function name: get_object
# Input: klee test file
# Return: List of symbolic objects retrieved from klee test file
# Description: 
# Get objects and its value from a given klee test file. 
# Target packet will be modified according to retrieved objects and values from 
# this function. 
##########################################################################################
def get_object( klee_testfile ):
   
   b = KTest.fromfile( klee_testfile )
   pos = 0
   sym_objects = []    

#   print 'ktest file : %r' % klee_testfile
#   print 'num objects: %r' % len(b.objects)

   for i,(name,data) in enumerate(b.objects):
       if name == KLEE_MODEL_VERSION: continue
       str = data
       sym_objects.append( (name, data) )

#       print 'object %4d: name: %r' % (i, name)
#       print 'object %4d: size: %r' % (i, len(data))
#       print 'object %4d: data: %r' % (i, str)

#       if opts.writeInts and len(data) == 4: 
#           print 'object %4d: data: %r' % (i, struct.unpack('i',str)[0])
#       else:
#           print 'object %4d: data: %r' % (i, str)

   return sym_objects


def ByteToHex( byteStr ):
   """
   Convert a byte string to it's hex string representation e.g. for output.
   """    
   # Uses list comprehension which is a fractionally faster implementation than
   # the alternative, more readable, implementation below
   #   
   #    hex = []
   #    for aChar in byteStr:
   #        hex.append( "%02X " % ord( aChar ) )
   #
   #    return ''.join( hex ).strip()        
   return ''.join( [ "%02X" % ord( x ) for x in byteStr ] )

def HexToByte( hexStr ):
   """
   Convert a string hex byte values into a byte string. The Hex Byte values may
   or may not be space separated.
   """
   # The list comprehension implementation is fractionally slower in this case    
   #
   #    hexStr = ''.join( hexStr.split(" ") )
   #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
   #                                   for i in range(0, len( hexStr ), 2) ] )

   bytes = []
   hexStr = ''.join( hexStr )

   for i in range(0, len(hexStr), 2):
      bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )

   return ''.join( bytes )



##########################################################################################
# Function name: set_mdns_data
# Input: original dns packet, replace data value, position
# Return: Manipulated packet for network injection
# Description: 
# Get objects and its value from a given klee test file. 
# Target packet will be modified according to retrieved objects and values from 
# this function. 
##########################################################################################
def set_mdns_data ( s_dns_pkt, s_data, set_pos ): 
   s_dns_pkt_hex = ByteToHex(s_dns_pkt)
   s_data_hex = ByteToHex(s_data)
#   print "domain hex: ", s_data_hex

#   print "src: ", s_dns_pkt_hex
   m_dns_pkt_hex = s_dns_pkt_hex[0:set_pos*2] + s_data_hex + s_dns_pkt_hex[ (set_pos*2+len(s_data_hex)): len(s_dns_pkt_hex) ]
#   print "mod: ", m_dns_pkt_hex
#   print "s_data_hex: ", len(s_data_hex), ", data: ", len(s_data)
  
   return HexToByte(m_dns_pkt_hex)

##########################################################################################
# Function name: manipulate_packet
# Input: source packet (from pcap file) and symbolic objects (from klee test file)
# Return: Manipulated packet for network injection
# Description: 
# Get objects and its value from a given klee test file. 
# Target packet will be modified according to retrieved objects and values from 
# this function. 
##########################################################################################
def manipulate_packet( src_udp_pkt, sym_objs ):

   for i,(name,data) in enumerate(sym_objs):
#      print 'object %4d: name: %r' % (i, name)
#      print 'object %4d: size: %r' % (i, len(data))
#      print 'object %4d: data: %r' % (i, data)

      if name == MDNS_FLAG_FIELD:		#"msg_flag"
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_FLAG_POS ) 
      elif name == MDNS_QUESTIONS_FIELD: 	#"msg_questions"
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_QUESTIONS_POS ) 
      elif name == MDNS_AN_RRS_FIELD: 		#"msg_anrrs"
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_AN_RRS_POS ) 
      elif name == MDNS_ADD_RRS_FIELD:   	#"msg_addrrs"
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_ADD_RRS_POS ) 
      elif name == MDNS_QUERIES_NAME_FIELD: 	#"msg_queries"
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_QUERIES_NAME_POS ) 
      elif name == MDNS_QUERIES_DOMAIN_FIELD: 	#"msg_domain"
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_QUERIES_DOMAIN_POS ) 
      elif name == MDNS_ANSWERS_FIELD: 		#"msg_answers"
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_ANSWERS_POS ) 
      elif name == MDNS_ADDREC_FIELD: 		#"msg_addrecords"    
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_ADDREC_POS ) 
      elif name == MDNS_RR_INSTANCE: 		#"msg_instance"    
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_RR_INSTANCE_POS ) 
      elif name == MDNS_RR_SERVICE: 		#"msg_service"    
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_RR_SERVICE_POS ) 
      elif name == MDNS_RR_DOMAIN: 		#"msg_domain"    
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_RR_DOMAIN_POS ) 
      elif name == MDNS_RR_TYPE: 		#"msg_type"    
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_RR_TYPE_POS ) 
      elif name == MDNS_RR_CLASS: 		#"msg_type"    
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, MDNS_RR_CLASS_POS ) 

      elif name.startswith(MDNS_OFFSET_FIELD):        #"sym-"
         parse_name=name.split("-")
         src_udp_pkt.data = set_mdns_data( src_udp_pkt.data, data, int(parse_name[1]))

   # Set DNS id 2 bytes to 0
   #src_udp_pkt.data=set_mdns_data(src_udp_pkt.data,"0000", 0)
  
   return src_udp_pkt


##########################################################################################
# Function name: manipulate_packet
# Input: source packet (from pcap file) and symbolic objects (from klee test file)
# Return: Manipulated packet for network injection
# Description: 
# Get objects and its value from a given klee test file. 
# Target packet will be modified according to retrieved objects and values from 
# this function. 
##########################################################################################
def inject_replay_packet( inj_udp_pkt ):
   ip = dpkt.ip.IP(id=0, src=_MDNS_LO_ADDR, dst=_MDNS_ADDR, p=17)
   u = dpkt.udp.UDP(sport=_MDNS_PORT, dport=_MDNS_PORT)

   u.data = str(inj_udp_pkt.data)
   u.ulen += len(u.data)
   ip.data = u
   ip.len += len(u)

   mdns_socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
   mdns_socket.connect((_MDNS_LO_ADDR, _MDNS_PORT))


   mdns_socket.send(str(ip.data))

   print "Now injecting a packet into network\n"


def main(args):
   if len(sys.argv) != 3:
      print "Usage:\n", sys.argv[0], "filename.pcap filename.ktest"
      sys.exit()

   if os.path.exists(sys.argv[1]) == False: 
      print "Input pcap file, ", sys.argv[1], ", does not exist."
      sys.exit()

   if os.path.exists(sys.argv[2]) == False: 
      print "Input klee test file, ", sys.argv[2], ", does not exist."
      sys.exit()
   
# Get a packet we want to inject into network with modifications.
   inject_pkt = get_packet( sys.argv[1] )
#   print "IP's data (UDP)0: ", inject_pkt.data

# Get value and objects we want to modify from the given klee test file
   sym_objects = get_object( sys.argv[2] )

# Manipulate a packet to be injected into network with given symbolic objects
   if len(sym_objects) > 0: 
      inject_pkt.data = manipulate_packet( inject_pkt.data, sym_objects )

   print "Manipulated IP's data (UDP): ", inject_pkt.data

# Inject the manipulated packet into network

   udp_pkt = inject_pkt.data
#   dns_pkt = dpkt.dns.DNS(udp_pkt.data)

   zero_conf = ZeroMdns(_MDNS_LO_ADDR)
   zero_conf.send( udp_pkt.data, _MDNS_ADDR, _MDNS_PORT)
   zero_conf.close()

if __name__=='__main__':
    main(sys.argv)

