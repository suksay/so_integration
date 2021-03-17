import get_neighbords
import get_elines
import get_qinqlinks
import get_vlan_nec

def lldp_info_retrieve():
    #Retrieving LLDP tables for NEC and Huawei devices
    try:
        print('Retrieving LLDP tables from devices...')
        get_neighbords.get()
        print('LLDP Retrieving : Success')
    except  Exception as ex:
        print('Error while retrieving LLDP Infos -> %s' % ex)
        pass

#QinQ Links and E-Lines retrieving 
def huawei_links():
    try :
        print('Retrieving QinQ tables from RTN devices...')
        get_qinqlinks.update()
        print('Retrieving Eline tables from RTN devices...')
        get_elines.update()
        print('Huawei Links Retrieving : Success')
    except  Exception as ex:
        print('Error while retrieving Huawei Links Infos -> %s' % ex)
        pass

#NEC VLAN configurations retrieving
def nec_vlans():
    try:
        print('Retrieving VLAN config from NEC devices...')
        get_vlan_nec.updata_vlan()
        print('NEC Vlans Retrieving : Success')
    except Exception as ex:
        print('Error while retrieving NEC devices configuration  -> %s' % ex)
        pass




#run in workflow
if __name__ == "__main__":
    lldp_info_retrieve()
    huawei_links()
    nec_vlans()

