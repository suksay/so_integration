#                                                                            #
#                                                                            #
#            Create Models for Microwaves in AAI Database                    #
#                                                                            #
##############################################################################

from aai_requests import *

#Create the Main Model for Microwave => microwave-equipment-id

main_model_url = '/service-design-and-creation/models/model/{model_invariant_id}'.format(model_invariant_id = 'microwave-equipment-id')
main_model_data = {
    "model-invariant-id" : "microwave-equipment-id",
    "model-type" : "resource"
}
main_model_request = put_request(main_model_url, main_model_data)


#Create Huawei Microwave Model -> huawei-microwave

huawei_model_url = '/service-design-and-creation/models/model/{model_invariant_id}/model-vers/model-ver/{model_version_id}'.format(model_invariant_id = 'microwave-equipment-id', model_version_id='huawei-microwave')
huawei_model_data = {
    "model-version-id" : "huawei-microwave",
    "model-name" : "to-change",
    "model-version" : "to-change",
    "model-description" : "Model for Huawei Microwave Equipment"
}
huawei_model_request = put_request(huawei_model_url, huawei_model_data)


#Create NEC Microwave Model -> nec-microwave

nec_model_url = '/service-design-and-creation/models/model/{model_invariant_id}/model-vers/model-ver/{model_version_id}'.format(model_invariant_id = 'microwave-equipment-id', model_version_id='nec-microwave')
nec_model_data = {
    "model-version-id" : "nec-microwave",
    "model-name" : "to-change",
    "model-version" : "to-change",
    "model-description" : "Model for NEC Microwave Equipment"
}
nec_model_request = put_request(nec_model_url, nec_model_data)





 