from pysnmp import hlapi
from pysnmp.smi.rfc1902 import rfc1902

"""
The aim of this file is to store MIB/OID values or generating function for SNMP operations
"""

####AAI CONFIG ########
_MW_INVARIANT_ID_ = 'microwave-equipment-id'
_HUAWEI_MW_VERSION_ID_ = 'huawei-microwave'
_NEC_MW_VERSION_ID_ = 'nec-microwave'

# TABLE ROW DEFINITIONS

#Default SNMP credentials
credentials = hlapi.CommunityData("Orange2020")

#Device name for NEC devices
sysName_named_oid = [('LLDP-MIB', 'lldpLocSysName', 0)]

#RTN device name
huawei_sysname = '.1.3.6.1.4.1.2011.2.25.4.30.21.1.1.0'

#Product type OID
nec_vr_type=".1.3.6.1.4.1.119.2.3.69.1.1.13.0"

hua_ne_serie =  ".1.3.6.1.4.1.2011.2.25.4.30.21.1.8.0"  #huaweo NE type
hua_ne_id =  ".1.3.6.1.4.1.2011.2.25.3.40.2.1.1.0"

"""
    We use oid of  OPTIX-RTN-IFBOARD-ATTRIB-MIB
"""
hua_link_search_table = [
    ".1.3.6.1.4.1.2011.2.25.4.40.3.10.4.1.9", #Source NeId
    ".1.3.6.1.4.1.2011.2.25.4.40.3.10.4.1.10", #Source BoardId
    ".1.3.6.1.4.1.2011.2.25.4.40.3.10.4.1.11", #Source SubId
    ".1.3.6.1.4.1.2011.2.25.4.40.3.10.4.1.12", #Source PortId
    ".1.3.6.1.4.1.2011.2.25.4.40.3.10.4.1.5", #Sink NeId
    ".1.3.6.1.4.1.2011.2.25.4.40.3.10.4.1.6", #Sink BoardId
    ".1.3.6.1.4.1.2011.2.25.4.40.3.10.4.1.7",#Sink SubId
    ".1.3.6.1.4.1.2011.2.25.4.40.3.10.4.1.8" #Sink PortId
]

#Not useful for MW
interfaces_table_named_oid = [
    ('IF-MIB', 'ifDescr'),
    ('IF-MIB', 'ifType'),
    ('IF-MIB', 'ifMtu'),
    ('IF-MIB', 'ifSpeed'),
    ('IF-MIB', 'ifPhysAddress'),
    ('IF-MIB', 'ifAdminStatus'),
    ('IF-MIB', 'ifOperStatus'),
    ('IF-MIB', 'ifHCInOctets'),
    ('IF-MIB', 'ifHCOutOctets'),
    ('IF-MIB', 'ifHighSpeed')
]

#NEC VLAN List table
get_nec_vlan_list = [
    ('IPE-COMMON-MIB','provVlanName')
]
#NEC EThernet itnerface list 
get_nec_eth_list  = [
    ('LLDP-MIB','lldpLocPortDesc')
]

#NEC VLAN List table
get_nec_vlan_config = [
    ('IPE-COMMON-MIB','provVlanCustomerPort')
]

#

def create_nec_vlan(vlan_id, vlan_name):
    oids = [
        (('IPE-COMMON-MIB','provVlanEquipmentMode','1'),rfc1902.Integer32(1)),
        (('IPE-COMMON-MIB','provVlanName',vlan_id),rfc1902.OctetString(vlan_name)),
        (('IPE-COMMON-MIB','provVlanNameRowstatus',vlan_id),rfc1902.Integer32(4))
    ]
    return oids

def delete_nec_vlan(vlan_id):
    oids = [
        (('IPE-COMMON-MIB','provVlanNameRowstatus',vlan_id),rfc1902.Integer32(6))
    ]
    return oids

def assign_nec_vlan(vlan_id, port_id):

    oids = [
        (('IPE-COMMON-MIB','provVlanCustomerPort',port_id,vlan_id),rfc1902.Integer32(3)),
        (('IPE-COMMON-MIB','provVlanCustomerRowstatus',port_id,vlan_id),rfc1902.Integer32(4))
    ]
    return oids

def remove_nec_vlan(vlan_id, port_id): 
    oids = [
        (('IPE-COMMON-MIB','provVlanCustomerRowstatus',port_id,vlan_id),rfc1902.Integer32(6))
    ]
    return oids


#Not useful
mgmt_table = [
    ('LLDP-MIB','lldpLocManAddrLen'),
    ('LLDP-MIB','lldpLocManAddrOID')
]


#NEC LLDP Port Config Status
nec_port_lldp_status = [
    ('LLDP-MIB', 'lldpPortConfigAdminStatus')
]

#Huawei LLDP Port Config Status
hua_port_lldp_status = [
    ('LLDP-MIB-HUAWEI', 'optixLldpWorkModle')
]

#LLDP Neighbors information table
lldp_table_named_oid = [
    ('LLDP-MIB', 'lldpRemChassisId'),
    ('LLDP-MIB', 'lldpRemPortDesc')
]

#Same thing for RTN devices
lldp_table_hua = [
    ('LLDP-MIB-HUAWEI', 'optixPKTLLDPChassisID'),
    ('LLDP-MIB-HUAWEI', 'optixPKTLLDPPortDescription')
]

snmp_ping = [('SNMPv2-MIB','sysName',0)]

def get_port_info_hua(port):
    """
    Generates the OID refering to 802.1<x> interface mode.
    The return value is either 1 for C-VLAN interfaces or 2 for S-VLAN interfaces

    inputs:
        port (str) : interface name ( format board/255/port )
    """
    port = str(port).split('/')
    print(port)
    port_info_hua = [
                    ('PORT-MIB','optixEthPortEncapType',port[0],port[1],port[2])
                    ]
    return port_info_hua

#Huawei QinQ Links Table
qinq_hua=[
            ('OPTIX-PKT-QINQLINK-MIB','optixQinqLinkIndex'),
            ('OPTIX-PKT-QINQLINK-MIB','optixQinqLinkBoardId'),
            ('OPTIX-PKT-QINQLINK-MIB','optixQinqLinkSubBdId'),
            ('OPTIX-PKT-QINQLINK-MIB','optixQinqLinkPortId'),
            ('OPTIX-PKT-QINQLINK-MIB','optixQinqLinkVlanId'),
            ('OPTIX-PKT-QINQLINK-MIB','optixQinqLinkRowStatus')
        ]


def get_qinq_row_oids(id,values):
    """
    Generates a table request for RTN QinQ Links creation
    inputs:
        id (str(int)) : QinQ link ID
        values (list(str)) : QinQ Link parameters. Watch out for the list ordering
            0- Board ID
            1- SubBoard ID (default 255)
            2- Port ID
            3- VLAN ID
    outputs:
        oids (list(tuple)): Ready-to-send OID list 
    """
    print(id,values)
    oids=[
    (('OPTIX-PKT-QINQLINK-MIB','optixQinqLinkRowStatus',id),rfc1902.Integer32(4)),
    (('OPTIX-PKT-QINQLINK-MIB','optixQinqLinkBoardId',id),rfc1902.Unsigned32(values[0])),
    (('OPTIX-PKT-QINQLINK-MIB','optixQinqLinkSubBdId',id),rfc1902.Unsigned32(values[1])),
    (('OPTIX-PKT-QINQLINK-MIB','optixQinqLinkPortId',id),rfc1902.Unsigned32(values[2])),
    (('OPTIX-PKT-QINQLINK-MIB','optixQinqLinkVlanId',id),rfc1902.Unsigned32(values[3]))]
    return oids

def get_eline_row_oids(id,board,subboard,port,vlan_num,vlan_str,name,qinqid,nms_id):
    """
    Generates a table request for RTN UNI-to-NNI E-Line creation
    inputs:
        id (str(int)) : E-LINE ID ( format ID.1.1 ). e.g 2.1.1
        board : Board ID
        subboard : SubBoard ID (default 255)
        port : Port ID
        vlan_num : Number of C-VLAN to allow
        vlan_str : Hexadecimal string containing the C-VLAN list (by bit indexing)
        name : Name shown in the LCT
        qinqid: QinQ Link ID to bridge
        nms_id : Service ID shown in LCT
    outputs:
        oids (list(tuple)): Ready-to-send OID list         
    """
    id = id.split('.')
    oids=[
            (('ELINE','optixUnitoNniElineRowStatus',*id),rfc1902.Integer(4)),
            (('ELINE','optixUnitoNniElineId',*id),rfc1902.Unsigned32(nms_id)),
            (('ELINE','optixUnitoNniElineName',*id),rfc1902.OctetString(name)),
            (('ELINE','optixUnitoNniElinePrtlthrough',*id),rfc1902.Integer(0)),
            (('ELINE','optixUnitoNniElineTagrole',*id),rfc1902.Integer(1)),
            (('ELINE','optixUnitoNniElineUniBid',*id),rfc1902.Unsigned32(board)),
            (('ELINE','optixUnitoNniElineUniSubBid',*id),rfc1902.Unsigned32(subboard)),
            (('ELINE','optixUnitoNniElineUniPortId',*id),rfc1902.Unsigned32(port)),
            (('ELINE','optixUnitoNniElineUniVlanNum',*id),rfc1902.Unsigned32(vlan_num)),
            (('ELINE','optixUnitoNniElineUniVlanlist',*id),rfc1902.OctetString(vlan_str)),
            (('ELINE','optixUnitoNniElineNniType',*id),rfc1902.Integer32(4)),
            (('ELINE','optixUnitoNniElineNniParaOne',*id),rfc1902.Unsigned32(0xffffffff)),
            (('ELINE','optixUnitoNniElineNniParaTwo',*id),rfc1902.Unsigned32(0xffffffff)),
            (('ELINE','optixUnitoNniElineNniParaThree',*id),rfc1902.Unsigned32(qinqid))
    ]
    return oids

def delete_eline_row_oids(id,board,subboard,port,vlan_num,vlan_str,name,qinqid,nms_index):
    """
    Generates the OID request to delete a specific E-LINE
    inputs:
        id : E-LINE ID ( format ID.NI_ID.NI_ID ). e.g 2.1.2
        other inputs are supposedly not useful
    outputs:
        oids (list(tuple)): Ready-to-send OID list         
    """
    id = id.split('.')
    oids=[
            (('ELINE','optixUnitoNniElineRowStatus',*id),rfc1902.Integer(6)),
    ]
    return oids

def get_nni2nni_row_oids(id,qinqid_a,qinqid_b,nms_id,name):
    """
    Generates a table request for RTN NNI-to-NNI E-Line creation
    inputs:
        id (str(int)) : E-LINE ID ( format ID.1.2 ). e.g 2.1.2
        qinqid_a: First QinQ Link ID to bridge
        qinqid_b : Second QinQ Link ID to bridge
        nms_id : Service ID shown in LCT
        name : Name shown in the LCT
    outputs:
        oids (list(tuple)): Ready-to-send OID list         
    """
    id = id.split('.')
    oids=[
            (('ELINE','optixNnitoNniElineRowStatus',*id),rfc1902.Integer(4)),
            (('ELINE','optixNnitoNniElineId',*id),rfc1902.Unsigned32(nms_id)),
            (('ELINE','optixNnitoNniElineName',*id),rfc1902.OctetString(name)),
            (('ELINE','optixNnitoNniElinePrtlthrough',*id),rfc1902.Integer(0)),
            (('ELINE','optixNnitoNniElineTagrole',*id),rfc1902.Integer(1)),
            (('ELINE','optixNnitoNniFirstNniType',*id),rfc1902.Integer32(4)),
            (('ELINE','optixNnitoNniFirstNniParaOne',*id),rfc1902.Unsigned32(0xffffffff)),
            (('ELINE','optixNnitoNniFirstNniParaTwo',*id),rfc1902.Unsigned32(0xffffffff)),
            (('ELINE','optixNnitoNniFirstNniParaThree',*id),rfc1902.Unsigned32(int(qinqid_a))),
            (('ELINE','optixNnitoNniSecondNniType',*id),rfc1902.Integer32(4)),
            (('ELINE','optixNnitoNniSecondNniParaOne',*id),rfc1902.Unsigned32(0xffffffff)),
            (('ELINE','optixNnitoNniSecondNniParaTwo',*id),rfc1902.Unsigned32(0xffffffff)),
            (('ELINE','optixNnitoNniSecondNniParaThree',*id),rfc1902.Unsigned32(int(qinqid_b)))
    ]
    return oids

def get_uni2uni_row_oids(id,name,board_a,subboard_a,port_a,board_b,subboard_b,port_b,vlan_num_a,vlan_num_b,vlan_str_a,vlan_str_b,nms_id):
    """
    Generates a table request for RTN UNI-to-UNI E-Line creation
    inputs:
        id (str(int)) : E-LINE ID ( format ID.1.2 ). e.g 2.1.2
        board_a : Board ID
        subboard_a : SubBoard ID (default 255)
        port_a : Port ID
        board_b : Second Board ID
        subboard_b : Second SubBoard ID (default 255)
        port_b : Second Port ID
        vlan_num_a : Number of C-VLAN to allow
        vlan_str_a : Hexadecimal string containing the C-VLAN list (by bit indexing)
        vlan_num_b
        vlan_str_b
        name : Name shown in the LCT
        nms_id : Service ID shown in LCT
    outputs:
        oids (list(tuple)): Ready-to-send OID list         
    """
    id = id.split('.')
    oids=[
            (('ELINE','optixUnitoUniElineRowStatus',*id),rfc1902.Integer(4)),
            (('ELINE','optixUnitoUniElineId',*id),rfc1902.Unsigned32(nms_id)),
            (('ELINE','optixUnitoUniElineName',*id),rfc1902.OctetString(name)),
            (('ELINE','optixUnitoUniElinePrtlthrough',*id),rfc1902.Integer(0)),
            (('ELINE','optixUnitoUniElineTagrole',*id),rfc1902.Integer(1)),
            # (('ELINE','optixUnitoUniElineMtu',*id),rfc1902.Unsigned32(1500)),
            #First Uni_a
            (('ELINE','optixUnitoUniElineFirstUniBid',*id),rfc1902.Unsigned32(board_a)),
            (('ELINE','optixUnitoUniElineFirstUniSubBid',*id),rfc1902.Unsigned32(subboard_a)),
            (('ELINE','optixUnitoUniElineFirstUniPortId',*id),rfc1902.Unsigned32(port_a)),
            (('ELINE','optixUnitoUniFirstUniVlanNum',*id),rfc1902.Unsigned32(vlan_num_a)),
            (('ELINE','optixUnitoUniFirstUniVlanlist',*id),rfc1902.OctetString(vlan_str_a)),
            #Second Uni_b
            (('ELINE','optixUnitoUniElineSecondUniBid',*id),rfc1902.Unsigned32(board_b)),
            (('ELINE','optixUnitoUniElineSecondUniSubBid',*id),rfc1902.Unsigned32(subboard_b)),
            (('ELINE','optixUnitoUniElineSecondUniPortId',*id),rfc1902.Unsigned32(port_b)),
            (('ELINE','optixUnitoUniSecondUniVlanNum',*id),rfc1902.Unsigned32(vlan_num_b)),
            (('ELINE','optixUnitoUniSecondUniVlanlist',*id),rfc1902.OctetString(vlan_str_b))

    ]
    return oids

#Potential duplicate
def delete_uni2uni_row_oids(id,nms_index):
    id = id.split('.')
    print("Trying to delete "+str(nms_index))
    oids=[
            (('ELINE','optixUnitoUniElineRowStatus',*id),rfc1902.Integer(6)),
    ]
    return oids

#OID list for Uni-To-Nni Table SNMP requests
eline_hua=[
            ('ELINE','optixUnitoNniElineIndex'),#0
            ('ELINE','optixUnitoNniElineUniId'),#1
            ('ELINE','optixUnitoNniElineNniId'),#2
            ('ELINE','optixUnitoNniElineId'),#3
            ('ELINE','optixUnitoNniElineName'),#4
            ('ELINE','optixUnitoNniElineUniBid'),#5
            ('ELINE','optixUnitoNniElineUniSubBid'),#6
            ('ELINE','optixUnitoNniElineUniPortId'),#7
            ('ELINE','optixUnitoNniElineUniVlanlist'),#8
            ('ELINE','optixUnitoNniElineNniParaThree'),#9
            ('ELINE','optixUnitoNniElineRowStatus')#10
        ]

#OID list for Nni-To-Nni Table SNMP requests
nni2nni_hua=[
            ('ELINE','optixNnitoNniElineIndex'),#0
            ('ELINE','optixNnitoNniFirstNniId'),#1
            ('ELINE','optixNnitoNniSecondNniId'),#2
            ('ELINE','optixNnitoNniElineId'),#3
            ('ELINE','optixNnitoNniElineName'),#4
            ('ELINE','optixNnitoNniFirstNniParaThree'),#5
            ('ELINE','optixNnitoNniSecondNniParaThree'),#6
            ('ELINE','optixNnitoNniElineRowStatus')#7
        ]


#OID list for Uni-To-Uni Table SNMP requests
uni2uni_hua=[
            ('ELINE','optixUnitoUniElineIndex'),#0
            ('ELINE','optixUnitoUniElineFirstUniId'),#1
            ('ELINE','optixUnitoUniElineSecondUniId'),#2
            ('ELINE','optixUnitoUniElineId'),#3
            ('ELINE','optixUnitoUniElineName'),#4
            ('ELINE','optixUnitoUniElineFirstUniBid'),#5
            ('ELINE','optixUnitoUniElineFirstUniSubBid'),#6
            ('ELINE','optixUnitoUniElineFirstUniPortId'),#7
            ('ELINE','optixUnitoUniFirstUniVlanlist'),#8
            ('ELINE','optixUnitoUniElineSecondUniBid'),#9
            ('ELINE','optixUnitoUniElineSecondUniSubBid'),#10
            ('ELINE','optixUnitoUniElineSecondUniPortId'),#11
            ('ELINE','optixUnitoUniSecondUniVlanlist'),#12
            ('ELINE','optixUnitoUniElineRowStatus')#13
]


def get_port_oid_hua(port):
    """
    Duplicate from get_port_info_hua() method
    In the future I would suggest to use get_port_info_hua instead
    """

    port = str(port).replace('/','.')
    port_info_hua = ['.1.3.6.1.4.1.2011.2.25.4.50.52.1.1.1.2.'+port,
                    '.1.3.6.1.4.1.2011.2.25.4.50.52.1.1.1.3.'+port,
                    '.1.3.6.1.4.1.2011.2.25.4.50.52.1.1.1.4.'+port
                    ]
    return port_info_hua

#NEC Chassis ID OID
lldp_id = [('LLDP-MIB', 'lldpLocChassisId', 0)]

#Huawei Chassis ID OID
lldp_hua_id = [('LLDP-MIB-HUAWEI', 'optixPKTLLDPSysMacAddr', 0)]


lldp_local_port_name = [('LLDP-MIB', 'lldpLocPortId', 0)]

#NEC LLDP interface configuration OIDs (see set_lldp_port_on)
lldp_port_status= [
                ('LLDP-MIB','lldpPortConfigPortNum'),
                ('LLDP-MIB','lldpPortConfigAdminStatus')]

#Potential deprecated function
def make_dict(names,values):
    result = dict()
    for i in range(len(names)):
        result[names[i]]=values[i]
    return result

def get_ne_with_id(device_id, hosts):
    for device in hosts:
        if device['device-id'] == device_id:
            return device