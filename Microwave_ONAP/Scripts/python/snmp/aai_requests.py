#                                                                            #
#                                                                            #
#                           AAI Requests function                            #
#                                                                            #
##############################################################################


import os, json
import requests

### GENERAL VARIABLES #####
AAI_ADDRESS = os.getenv('AAI_ADDRESS')
AAI_USERNAME = os.getenv('AAI_USERNAME')
AAI_PASSWORD = os.getenv('AAI_PASSWORD')

AAI_CREDENTIALS = (AAI_USERNAME, AAI_PASSWORD)

BASE_URL = "https://" + AAI_ADDRESS+ ":8447/aai/v19"

URL_GET_DEVICES = '/network/devices'
URL_GET_PNFS = '/network/pnfs'
URL_GET_PHYSICAL_LINK = '/network/physical-links'

HEADERS = {
    "Accept": "application/json",
    "Content-type": "application/json",
    "X-TransactionId" : "testaai",
    "X-FromAppId" : "AAI"

}

############ REQUESTS #############

def get_request(url):
    url = BASE_URL+url
    req = requests.get(url=url,headers=HEADERS, auth=AAI_CREDENTIALS, verify=False)
    if req.status_code != 200 :
        element = url.split('/')
        print('{} not exist'.format(element[-1].upper()))
    return req.status_code,req.json()


"""
def delete_request(url):
    req = requests.delete(url=url,headers=HEADERS, auth=auth, verifyexit()
    =False)
    
    if req.status_code != 200 :
        element = url.split('/')
        raise ApiError('{} not exist'.format(element[-1]))
    
    return req.json()
"""

def put_request(url,data):
    url = BASE_URL+url
    req = requests.put(url=url,headers=HEADERS, data=json.dumps(data), auth=AAI_CREDENTIALS, verify=False)
    element = url.split('/')
    if req.status_code != 201 :
        print('{} not create'.format(element[-1]))
    else :
        print('{} {} created !'.format(element[-1].upper(), element[-2] ))
    return req.status_code

"""
def patch_request(url):
    req = requests.get(url=url,headers=HEADERS, auth=auth, verify=False)
   
    if req.status_code != 200 :
        element = url.split('/')
        raise ApiError('{} not exist'.format(element[-1]))
    
    return req.json()
"""


def extract_neighbords_table():
    devices = list()
    req_get_devices = get_request(URL_GET_DEVICES)['device']
    if req_get_devices == 200 :
        devices = req_get_devices[1]['device']

    neighbordships = dict()

    for device in devices:
        URL_DEVICE_P_INTERFS = URL_GET_PNFS +'/pnf/{pnf_name}/p-interfaces'.format(pnf_name=device['device-id'])
        device_p_interfaces = list()
        req_get_p_interfaces = get_request(URL_DEVICE_P_INTERFS)  
        if req_get_p_interfaces == 200 :
            device_p_interfaces = req_get_p_interfaces[1]['p-interface']

        neighbordships[device['device-id']] = list()

        for p_interface in device_p_interfaces:
            link = dict()
            link['local_int_index'] = p_interface['equipment-identifier']
            link['local_intf'] = p_interface['interface-name']

            URL_P_LINK = '/network'+p_interface['relationship-list']['relationship'][0]['related-link'].split('network')[1]
            p_link = get_request(URL_P_LINK+'/relationship-list')[1]['relationship']
            
            #Get opposite infos
            for interf in p_link:
                if device['device-id'] != interf['relationship-data'][0]['relationship-value'] :
                    neigh_link = '/network'+ interf['related-link'].split('network')[1]
                    neigh  = get_request(neigh_link)[1]

                    link['neighbor']  = interf['relationship-data'][0]['relationship-value']
                    link['neighbor_intf'] = neigh['interface-name']

            neighbordships[device['device-id']].append(link)

    
    return neighbordships






