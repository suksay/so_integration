from pysnmp import hlapi
from pysnmp.hlapi import *
from pysnmp.hlapi import SnmpEngine
import code
import itertools
import time
from pysnmp.smi import builder

# SNMPv3 alternative
'''
hlapi.UsmUserData('testuser', authKey='authenticationkey', privKey='encryptionkey', authProtocol=hlapi.usmHMACSHAAuthProtocol, privProtocol=hlapi.usmAesCfb128Protocol)
'''

"""
The aim of this file is to provide a bunch of methods as tools for SNMP operations.
What is called MIB or MIB entries in those methods are refering to text formatted OIDs.
There's many samples in the pyconfig.py file.
e.g : ('LLDP-MIB', 'lldpLocSysName', 0)
"""

#Potential deprecated method
def get_engine():
    mibBuilder = builder.MibBuilder()
    engine=SnmpEngine()
    builder_engine = engine.getMibBuilder()
    builder_engine.addMibSources(builder.DirMibSource('Scripts/python/snmp/mibs'))
    return engine


def set_oid(target, oids, credentials,data):
    """
    Send a set SNMP request for a single OID
    inputs:
        target (str) : Device IP address
        oids (str) : Single OID to set
        credentials (str) : SNMP Community
        data : Value to set. Must be casted according to rfc1902 OID type specification before calling
    outputs:
        SNMP response (dict)
    """
    port=161
    engine=hlapi.SnmpEngine()
    context=hlapi.ContextData()
    handler = hlapi.setCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        ObjectType(ObjectIdentity(oids),data)
    )
    return fetch(handler)



def get(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    """
    Send a get SNMP request for a MIB list
    inputs:
        target (str) : Device IP address
        oids (str) : List or single MIB tuple (see pyconfig.py for examples)
        credentials (str) : SNMP Community
        data : Value to set. Must be casted according to rfc1902 OID type specification before calling
    outputs:
        SNMP response (dict)
    """
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types_from_named_oid(oids)
    )
    return fetch(handler)

def get_oid(target, oid, credentials):
    """
    Send a set SNMP request for a single OID
    inputs:
        target (str) : Device IP address
        oid (str) : Single OID to get
        credentials (str) : SNMP Community
    outputs:
        SNMP response (dict)
    """
    port=161
    engine=hlapi.SnmpEngine()
    context=hlapi.ContextData()
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        ObjectType(ObjectIdentity(oid))
    )
    return fetch(handler)

#Not used in this project
def walk(target, oid, credentials,table):
    port=161
    engine=hlapi.SnmpEngine()
    context=hlapi.ContextData()
    result = list()
    for (errorIndication,
     errorStatus,
     errorIndex,
     varBinds) in hlapi.nextCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=not(table)
    ):
        if errorIndication:
            print('fail')
            time.sleep(1)
            
        elif errorStatus:
            print('fail')
            time.sleep(1)
            
        else:
            result.append(str(varBinds[0]))
    return result

#Not used in this project
def get_next(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.nextCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types_from_named_oid(oids)
    )
    return fetch(handler)


def get_oids(target, oids, credentials):
    """
    Send a get SNMP request for an OID list
    inputs:
        target (str) : Device IP address
        oids (str) : List of OIDs
        credentials (str) : SNMP Community
    outputs:
        SNMP response (dict)
    """
    port=161
    engine=hlapi.SnmpEngine()
    context=hlapi.ContextData()
    ObjectList=list()
    for oid in oids:
        ObjectList.append(ObjectType(ObjectIdentity(oid)))
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *ObjectList
    )
    return fetch(handler)

#oids_and_values => list((oid,value)) with casted values (e.g UnsignedInteger(value))
def add_row_oids(target, oids_and_values,credentials):
    """
    Send a set SNMP request for row creation (=list) using OIDs
    inputs:
        target (str) : Device IP address
        oids_and_values  list((oid,value)) : List of tuples
            -oid (str)
            -value : Casted value to set ( with respect for rfc1902 type specification )
        credentials (str) : SNMP Community
    outputs:
        SNMP response (dict)
    """
    port=161
    engine=hlapi.SnmpEngine()
    context=hlapi.ContextData()
    ObjectList=list()
    for oid,value in oids_and_values:
        ObjectList.append(ObjectType(ObjectIdentity(oid),value))
    handler = hlapi.setCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *ObjectList
    )
    return fetch(handler)

def add_row(target, oids_and_values,credentials):
    """
    Send a set SNMP request for row creation (=list) using MIB
    inputs:
        target (str) : Device IP address
        oids_and_values  list(MIB entry) : List of MIB entries (as tuples, see pyconfig.py for examples)
        credentials (str) : SNMP Community
    outputs:
        SNMP response (dict)
    """
    port=161
    engine=hlapi.SnmpEngine()
    context=hlapi.ContextData()
    ObjectList=list()
    handler = hlapi.setCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types_from_name_set(oids_and_values)
    )
    print(handler)
    return fetch(handler)

#Not used in this project
def get_bulk(target, oids, credentials, count, start_from=0, port=161,
             engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.bulkCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        start_from, count,
        *construct_object_types_from_named_oid(oids),
        lexicographicMode=True
    )
    return fetch(handler)

#Not used in this project
def get_bulk_auto(target, oids, credentials, count_oid, start_from=0, port=161,
                  engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    count = get(target, count_oid, credentials, port, engine, context)[count_oid][0]
    return get_bulk(target, oids, credentials, count, start_from, port, engine, context)


def get_table(target, oids, credentials, start_from=0, port=161,
              engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    """
    Send a get SNMP request for a table request
    inputs:
        target (str) : Device IP address
        oids (list) : List of unindexed MIB entries (e.g ('IF-MIB', 'ifDescr'))
        credentials (str) : SNMP Community
    outputs:
        SNMP response (dict)
    """          
    handler = hlapi.nextCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port),timeout=10),
        context,
        *construct_object_types_from_named_oid(oids),
        lexicographicMode=False
    )
    
    if len(oids) > 1 :
        return cut_array_to_table(fetch(handler),len(oids))

    else :
        return fetch(handler)

def get_table_oids(target, oids, credentials, start_from=0, port=161,
              engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    """
    Send a get SNMP request for a table request
    inputs:
        target (str) : Device IP address
        oids (list) : List of oids (e.g (['.1.1.2.4.5', '.1.1.2.4.7'))
        credentials (str) : SNMP Community
    outputs:
        SNMP response (dict)
    """
    ObjectList = list()
    for oid in oids :
        ObjectList.append(ObjectType(ObjectIdentity(oid)))            
    handler = hlapi.nextCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port),timeout=10),
        context,
        *ObjectList,
        lexicographicMode=False
    )
    
    if len(oids) > 1 :
        return cut_array_to_table(fetch(handler),len(oids))
    else :
        return fetch(handler)

def construct_object_types(list_of_oids):
    """
    Build a SNMP payload object from oids for get requests
    inputs:
        list_of_oids (list(str))
    outputs:
        SNMP payload for Get requests
    """
    object_types = []
    for oid in list_of_oids:
        object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid).addMibSource('./mibs')))
    return object_types


def construct_object_types_from_named_oid(list_of_oid_name_tuplets):
    """
    Build a SNMP payload object from MIB entries with /mibs files lookup for get requests
    inputs:
        list_of_oid_name_tuplets (list(tuple)) : List of MIB entries
    outputs:
        SNMP payload for Get requests
    """
    object_types = []
    for oid in list_of_oid_name_tuplets:
        addr = []
        for x in oid:
            addr.append(x)
        object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(*addr).addMibSource('./mibs')))
    return object_types

def construct_object_types_from_name_set(list_of_oid_name_tuplets):
    """
    Build a SNMP payload object from MIB entries with /mibs files lookup for set requests
    inputs:
        list_of_oid_name_tuplets (list(tuple)) : List of (MIB Entry, Value to set)
    outputs:
        SNMP payload for Set requests
    """
    object_types = []
    for oid,value in list_of_oid_name_tuplets:
        addr = []
        for x in oid:
            addr.append(x)
        object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(*addr).addMibSource('./mibs'),value))
    return object_types

#Parsing method for Table processing
def cut_array_to_table(data,collumns):
    result = []
    row = []
    collumn_index = 0
    for x in data:
        if collumn_index == 0:
            row.append(x)
            collumn_index = 1
        elif collumn_index < collumns:
            collumn_index = collumn_index + 1
            row.append(x)
            if collumn_index == collumns:
                result.append(row)
        else:
            collumn_index = 1
            row = [x] #starts new row

    return result


#SNMP responses manager
def fetch(handler):
    result = []

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in handler:

        if errorIndication:
            print(errorIndication)
            raise RuntimeError('Got SNMP error: {0}'.format(errorIndication))
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            raise RuntimeError('Got SNMP error: {0}'.format(errorStatus))
        else:
            for varBind in varBinds:
                result.append(varBind)

    print("DEBUG: len of result from fetch() " + str(len(result)) )
    return result

#Automatic OID value caster
#Still, I suggest using rfc1902 casts instead
def cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value
