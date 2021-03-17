import json
import quicksnmp
from pysnmp import hlapi
from pyconfig import *
import os
from aai_requests import *
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('aai_templates/'))

p_interface = env.get_template('p-interface.json')
l_interface = env.get_template('l-interface.json')
physical_link = env.get_template('physical-link.json')

def get_hua_id_from_inventory(ne_id, hosts):
    for ne in hosts:
        if ne['model-customization-id'] == ne_id :
            return ne['device-id']


def get_huawei_neighbors(ip_address, hosts):
    links = []
    serie_fulloutdor = [92, 138, 151, 160]
    hosts_ids = [ne['device-id'] for ne in hosts]

    ne_serie = str(quicksnmp.get_oid(str(ip_address), hua_ne_serie,credentials)[0][-1])
    if int(ne_serie) in serie_fulloutdor:
        """
            Case of full outdor NE
        """
        if_links = quicksnmp.get_table_oids(str(ip_address),hua_link_search_table, credentials)
        for link in if_links :
            link_i = dict()
            link_i["local_int_index"]  = ""
            link_i["local_intf"] = str(link[1][-1]) +"/"+ str(link[2][-1]) +"/"+ str(link[3][-1])
            link_i["neighbor"] =  get_hua_id_from_inventory(str(link[4][-1]), hosts)
            link_i["neighbor_intf"] = str(link[5][-1]) +"/"+ str(link[6][-1]) +"/"+ str(link[7][-1])
            links.append(link_i)    

    neighbors=quicksnmp.get_table(ip_address, lldp_table_hua,credentials) #For NE Interface with LLDP
    for link in neighbors:
        link_i = dict()
        if str(link[0][1]) != "Not received":
            link_i["local_int_index"]= link[0][0][-1]
            link_i["local_intf"]= str(link[0][0][-4])+'/'+str(link[0][0][-3])+'/'+str(link[0][0][-2])
            link_i["neighbor"]= '0x'+(link[0][1].prettyPrint()).replace('-','').lower()
            neighbor=[chassis for chassis in hosts_ids if link_i["neighbor"][:-4] in chassis]
            if neighbor != [] :
                link_i["neighbor"]=neighbor[0]
                n_int = str(link[1][1]).split(' ')
                if len(n_int) == 3 : link_i["neighbor_intf"]=n_int[1]
                else : link_i["neighbor_intf"]=n_int[0]
                links.append(link_i)
    return links 

def get_nec_neighbords(ip_address, hosts):
    links = []
    neighbors=quicksnmp.get_table(ip_address, lldp_table_named_oid,credentials)
    hosts_ids = [ne['device-id'] for ne in hosts]

    for link in neighbors:
        link_i = dict()
        """
            link[0][1]  : value of lldpremChassisId 
            link[1][1]  : value of lldpremPortDesc

        """
        if str(link[1][1]) != "Not received" :
            link_i["local_int_index"]= link[0][0][-2]
            loc_port_desc='.1.0.8802.1.1.2.1.3.7.1.4.'+str(link_i["local_int_index"]) #Can't do it with MIBS because of an exceeding ValueConstraint on NEC devices
            link_i["local_intf"]= str(quicksnmp.get_oid(ip_address,loc_port_desc,credentials)[0][1])
            link_i["neighbor"]= link[0][1].prettyPrint()
            neighbor=[chassis for chassis in hosts_ids if link_i["neighbor"][:-4] in chassis]
            if neighbor != [] :
                link_i["neighbor"]=neighbor[0]
                #for exemple  if lldpremPortDesc = "FastEthernet 1/255/4 Interface"
                # n_int = str(link[1][1]).split(' ') = ['FastEthernet', '1/255/4', 'Interface']
                n_int = str(link[1][1]).split(' ')
                if len(n_int) == 3 : link_i["neighbor_intf"]=n_int[1]
                else : link_i["neighbor_intf"]=n_int[0]
                if link_i["local_intf"] != 'NMS':
                    links.append(link_i)
    return links


def neighborships_in_aai(neighborships_data, devices):

    def extract_opposite_site(nodeB_id, nodeB_int,nodeA_id, nodeA_int):
        for element in neighborships_data[nodeB_id]:
            if nodeA_id == element['neighbor'] and nodeA_int == element['neighbor_intf'] and nodeB_int == element['local_intf'] :
                nodeB_int_index = element['local_int_index']
                neighborships_data[nodeB_id].pop(neighborships_data[nodeB_id].index(element))

                return nodeB_int_index

    #links = []
    for device_id in neighborships_data:
        
        if neighborships_data[device_id] != [] :
            for element in neighborships_data[device_id] :

                nodeB_index = extract_opposite_site(element["neighbor"],element["neighbor_intf"],device_id,element["local_intf"])

                if nodeB_index != None :

                    #Create Device A p-interface and l-interface
                    URL_DEVICE_A_P_INTF = URL_GET_PNFS +'/pnf/{pnf_name}/p-interfaces/p-interface/{interface_name}'.format(pnf_name=device_id, interface_name=element['local_int_index'])
                    p_interf_A_data = json.loads(p_interface.render(interface_name=element['local_int_index'], equip_identifier=element["local_intf"]))

                    URL_DEVICE_A_L_INTF = URL_DEVICE_A_P_INTF + '/l-interfaces/l-interface/{interface_id}'.format(interface_id=element['local_int_index'])
                    l_interf_A_data = json.loads(l_interface.render(interface_id=element['local_int_index'], interface_name=element["local_intf"]))

                    req_p_interf_A = put_request(URL_DEVICE_A_P_INTF, p_interf_A_data)
                    req_l_interf_A = put_request(URL_DEVICE_A_L_INTF, l_interf_A_data)

                    #Create Device B p-interface and l-interface
                    URL_DEVICE_B_P_INTF = URL_GET_PNFS +'/pnf/{pnf_name}/p-interfaces/p-interface/{interface_name}'.format(pnf_name=element["neighbor"], interface_name=nodeB_index)
                    p_interf_B_data = json.loads(p_interface.render(interface_name=nodeB_index, equip_identifier=element["neighbor_intf"]))
                    
                    URL_DEVICE_B_L_INTF = URL_DEVICE_B_P_INTF + '/l-interfaces/l-interface/{interface_id}'.format(interface_id=nodeB_index)
                    l_interf_B_data = json.loads(l_interface.render(interface_id=nodeB_index, interface_name=element["neighbor_intf"]))

                    req_p_interf_B = put_request(URL_DEVICE_B_P_INTF, p_interf_B_data)
                    req_l_interf_B = put_request(URL_DEVICE_B_L_INTF, l_interf_B_data)

                    #Make neighborship with physical-link
                    link_name = devices[device_id] +'_'+element["local_int_index"]+'-'+devices[element["neighbor"]]+'_'+nodeB_index
                    URL_P_LINK = URL_GET_PHYSICAL_LINK + '/physical-link/{link_name}'.format(link_name=link_name)
                    physical_link_data = json.loads(physical_link.render(link_name=link_name, device_A_id=device_id , device_A_interf_name=element['local_int_index'], device_B_id=element["neighbor"], device_B_interf_name=nodeB_index))
                    req_link = put_request(URL_P_LINK, physical_link_data)


def get():

    devices = get_request(URL_GET_DEVICES)[1]['device']

    neighborships = dict()

    for device in devices:
        links = []
        address=device['system-ipv4']
        vendor=device['vendor']
        """
        Different SNMP processing according to vendor.
        """
        if 'nec' in vendor:
            nec_links = get_nec_neighbords(address, devices)
            links.extend(nec_links)
        if vendor=='huawei':
            hua_links = get_huawei_neighbors(address, devices)
            links.extend(hua_links)
            
        if links != [] : neighborships[id]=links 
    

    neighborships_in_aai(neighborships, devices)
    


    #print(neighborships)


