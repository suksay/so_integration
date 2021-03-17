#!/bin/sh
# ============LICENSE_START=======================================================
#  Copyright (C) 2021 Nordix Foundation.
# ================================================================================
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============LICENSE_END=========================================================

echo "Creating nfvo database . . ." 1>/tmp/mariadb-nfvodb.log 2>&1

mysql -uroot -p$MYSQL_ROOT_PASSWORD << 'EOF' || exit 1
DROP DATABASE IF EXISTS `nfvo`;
CREATE DATABASE /*!32312 IF NOT EXISTS*/ `nfvo` /*!40100 DEFAULT CHARACTER SET latin1 */;
DROP USER IF EXISTS 'nfvouser';
CREATE USER 'nfvouser';
GRANT ALL on nfvo.* to 'nfvouser' identified by 'nfvo123' with GRANT OPTION;
FLUSH PRIVILEGES;
EOF

echo "Created nfvo database . . ." 1>>/tmp/mariadb-nfvodb.log 2>&1
