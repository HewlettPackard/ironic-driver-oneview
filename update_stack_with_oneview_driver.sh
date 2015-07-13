# Copyright 2015 Hewlett-Packard Development Company, L.P.
# Copyright 2015 Universidade Federal de Campina Grande
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

OPENSTACK_HOME=/opt/stack
REPOSITORY_HOME=${REPOSITORY_HOME:-~/ironic_drivers}
IRONIC_HOME=${IRONIC_HOME:-$OPENSTACK_HOME/ironic}


delete_if_exists() {
  if [ -f $1 ]; then
    rm $1;
  elif [ -L $1 ]; then
    unlink $1
  elif [ -d $1 ]; then
    rm -rf $1
  fi
}

echo "Updating repository"
echo "Repository Updated"

echo "Deleting and Copying oneview.py"
delete_if_exists $IRONIC_HOME/ironic/drivers/oneview.py
cp $REPOSITORY_HOME/ironic/ironic/drivers/oneview.py $IRONIC_HOME/ironic/drivers/oneview.py
echo "oneview.py copied"

echo "Deleting and Copying oneview"
delete_if_exists $IRONIC_HOME/ironic/drivers/modules/oneview

mkdir $IRONIC_HOME/ironic/drivers/modules/oneview
cp $REPOSITORY_HOME/ironic/ironic/drivers/modules/oneview/* $IRONIC_HOME/ironic/drivers/modules/oneview/
echo "oneview copied"

echo "Deleting and Copying test_oneview.py"
delete_if_exists $IRONIC_HOME/ironic/tests/drivers/oneview
mkdir $IRONIC_HOME/ironic/tests/drivers/oneview
cp $REPOSITORY_HOME/ironic/ironic/tests/drivers/oneview/* $IRONIC_HOME/ironic/tests/drivers/oneview
echo "oneview tests copied"
