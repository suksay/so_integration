# Microwave Manager 
LLDP Topology Discovery and L2 services provisionning.

CBA (Controller Blueprint Archive) source of the Microwave Manager project, dedicated to CDS.
This project requires at least a local installation of the Blueprints Processor and Command Executor (see ONAP CCSDK component)

Based on Python3.6 scripts (remote-python-executor components)

# Setup Environment

## Requirements
To install the environment, the machine must have the following tools:
- docker
- docker-compose
- zip & unzip

## Steps
After downloading this project directory, it will be necessary to launch the setup_env.sh script which executes according to the following steps :
1. Creation and startup of cds and aai services

```
    docker-compose up -d
```

2. Zipping and send CBA file (send_cba.sh in /Microwave_ONAP)

3. Init Project (init_project.sh)
    Run init-project workflow to create microwaves model in AAi and active GUI


# Workflow descriptions
## init-project
This workflow consists of creating the Huawei and Nec microwaves models.

#### Steps
1. Create main microwaves models, huawei and nec models (aai_init.py)

2. Active GUI Flask Server (gui.py)

#### Output
gui.py give server Flask status

## network-discovery
An SNMP Network Discovery and L2 configuration pulling can be done using the network-discovery workflow
#### Steps
1. Get_Address (get_address.py) :

    Multi-Threaded SNMP network discovery. Default network is 172.20.183.0/24

2. Get_Infos (get_infos.py) :

    Retrieve configuration data from discovered devices :

    - LLDP Neighborships via SNMP (get_neighbords.py)
    - Huawei RTN E-Lines and QinQ Links via SNMP (get_eline.py + get_qinqlinks.py)
    - NEC VR VLAN ports configuration via SSH (get_vlan_nec.py)

3. Make_Graph (make_graph.py) :
    Prepare environment for GUI

#### Output
get_info.py execution standard out. Gives details on scripts success (LLDP, Elines/QinQLinks and VLAN data pulling)

## path-finding
Single-step workflow that find every path available between two already discovered devices
#### Input
```json
"python-args":
{
    "device_a" : "<Start device ID>",
    "device_b" : "<End device ID>"
}
```
#### Step
1. Get_Paths (path_finding.py)

    Based on the device_a and device_b IDs and neighborships file, it uses a simple graph algorithm to find paths and save it on paths.json

#### Output
path_finding.py execution standard out. Gives a small report of found paths.

## config-path
Using already found paths and devices configuration, provides a VLAN-based L2 service along nodes and interfaces of the chosen path.

#### Input
```json
"python-args":
{
    "device_a" : "<Start device ID>",
    "device_b" : "<End device ID>",
    "interface_a" : "<Start interface name>",
    "interface_b" : "<End interface name>",
    "vlan" : "<VLAN or list of VLAN>",
    "path_number" : "<List index (in paths.json) of the chosen path>"
}
```
#### Step
1. Get_Paths (path_finding.py)
2. Configure_Path (configure_path.py)
    Get the chosen path and sequentially configure services on each nodes. 

    According to the device vendor and interfaces types (Ethernet, Modem). Here's a quick description of the algorithm behaviour : 
    #### Huawei
    Configurations are sent using SNMP (see quicksnmp.py and pyconfig.py)
    1. Ethernet ingress <-> Ethernet egress
        - Creates a Uni-to-Uni service (add_uni2uni.py) = both interfaces as C-VLAN
    2. Ethernet ingress <-> Modem egress (and reciprocally)
        - Creates a QinQ Link on the Modem Interface (add_qinq.py)
        - Creates a Uni-to-Nni service (add_uni2nni.py) = Ethernet as C-VLAN bridged to the QinQ Link
    3. Modem ingress <-> Modem egress
        - Creates a QinQ Link on both interfaces
        - Creates a Nni-to-Nni service (add_nni2nni.py) = Bridge between both QinQ Links
    #### NEC
    Configurations are sent using SNMP in th configure_nec.py script.
    
3. Get_Infos (get_infos.py) (Update infos)
#### Output
configure_path.py execution standard out. Gives the chosen path and returns of configurations 

# Example
Here's an example of CDS workflow call using curl. The blueprint name is "mw-manager". The called workflow is path-finding and requires arguments into the "path-finding-request" as following:
 ```console
curl --location --request POST 'http://<BLUEPRINTSPROCESSOR_IP>:<BLUEPRINTSPROCESSOR_PORT>/api/v1/execution-service/process' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic Y2NzZGthcHBzOmNjc2RrYXBwcw==' \
--data '{
    "actionIdentifiers": {
        "mode": "sync",
        "blueprintName": "mw-manager",
        "blueprintVersion": "1.0.0",
        "actionName": "path-finding"
    },
    "payload": {
        "path-finding-request" :{
            "python-args" : 
                {
                    "device_a":<DEVICE_A_ID>,
                    "device_b":<DEVICE_B_ID>
                }
        }
    },
    "commonHeader": {
        "subRequestId": "143748f9-3cd5-4910-81c9-a4601ff2ea58",
        "requestId": "e5eb1f1e-3386-435d-b290-d49d8af8db4c",
        "originatorId": "SDNC_DG"
    }
}'
```
