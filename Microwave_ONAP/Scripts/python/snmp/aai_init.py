#                                                                            #
#                                                                            #
#            Create Models for Microwaves in AAI Database                    #
#                                                                            #
##############################################################################

from aai_requests import *
from pyconfig import _MW_INVARIANT_ID_, _HUAWEI_MW_VERSION_ID_, _NEC_MW_VERSION_ID_

import json
from jinja2 import Environment, FileSystemLoader


env = Environment(loader=FileSystemLoader('aai_templates/'))

model_invariant = env.get_template('model-invariant.json')
model_version = env.get_template('model-version.json')

#Create the Main Model for Microwave => microwave-equipment-id

main_model_url = '/service-design-and-creation/models/model/{model_invariant_id}'.format(model_invariant_id=_MW_INVARIANT_ID_)
main_model_data = json.loads(model_invariant.render(model_invariant_id=_MW_INVARIANT_ID_, model_type="resource"))
main_model_request = put_request(main_model_url, main_model_data)


#Create Huawei Microwave Model -> huawei-microwave

huawei_model_url = '/service-design-and-creation/models/model/{model_invariant_id}/model-vers/model-ver/{model_version_id}'.format(model_invariant_id=_MW_INVARIANT_ID_, model_version_id=_HUAWEI_MW_VERSION_ID_)
huawei_model_data = json.loads(model_version.render(model_version_id=_HUAWEI_MW_VERSION_ID_, vendor="HUAWEI"))
huawei_model_request = put_request(huawei_model_url, huawei_model_data)


#Create NEC Microwave Model -> nec-microwave

nec_model_url = '/service-design-and-creation/models/model/{model_invariant_id}/model-vers/model-ver/{model_version_id}'.format(model_invariant_id=_MW_INVARIANT_ID_, model_version_id=_NEC_MW_VERSION_ID_)
nec_model_data = json.loads(model_version.render(model_version_id=_NEC_MW_VERSION_ID_, vendor="NEC"))
nec_model_request = put_request(nec_model_url, nec_model_data)





 