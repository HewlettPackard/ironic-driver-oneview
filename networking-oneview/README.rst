==================================================
HP OneView Mechanism Driver for Neutron ML2 plugin
==================================================

Overview
========
The mechanism driver interacts with Neutron and OneView to
dynamically reflect networking operations made by OpenStack on OneView. With
these operations it's possible to a OneView administrator to know what is
happening in OpenStack System which is running in the Data Center and also
automatizes some operations previously required to be manual.

The diagram below provides an overview of how Neutron and OneView will
interact using the OneView Mechanism Driver. OneView Mechanism
Driver uses HPE Oneview SDK for Python to provide communication between
Neutron and OneView through OneView's REST API.

Flows:
::

    +---------------------------------+
    |                                 |
    |       Neutron Server            |
    |      (with ML2 plugin)          |
    |                                 |
    |           +---------------------+
    |           |       OneView       |  Ironic API  +----------------+
    |           |      Mechanism      +--------------+     Ironic     |
    |           |       Driver        |              +----------------+
    +-----------+----------+----------+
                           |
                 REST API  |
                           |
                 +---------+---------+
                 |     OneView       |
                 +-------------------+


The OneView Mechanism Driver aims at having the Ironic-Neutron
integration for multi-tenancy working with nodes driven by the OneView
drivers for Ironic.

How the driver works
====================

The OneView Mechanism Driver considers that not all networking operations that
are performed in OpenStack need to be reflected in OneView. To identify if a certain
request should be executed by the driver it might check if the networks and ports are
related with networks/connections which should be reflected OneView.

For Network Operations, the driver checks if the physical provider-network
From Neutron network belongs to is defined as one of the "managed networks" of the
driver. The concept of "managed networks" refers to the networks configured in
the driver config file with a mapping to attached it to an Uplink Set in OneView.
Operations of Networks with no mappings are just ignored by the driver.

These mappings configuration can be made in the configuration file using the
"uplinkset_mappings" and "flat_net_mappings" attributes, as follows:

- "uplinkset_mappings" are used to define which provider networks from Neutron should be controlled by the OneView Mechanism Driver.
  The administrator defines comma-separated triples of [Provider_Network:Logical_Interconnect_Group_UUID:Uplink_Set_name] 
  to represent each desired mapping of a Neutron network to the Logical Interconnect Group's Uplink Set in which it will 
  be created in OneView. These mappings can be related to two types of Uplink Sets: “Ethernet” Uplink Sets to support VLAN
  networks or “Untagged” Uplink Sets to support flat network. In the former, OneView does not allow more than one network
  to use the same VLAN ID in the same Uplink Set and only one mapping is allowed per Logical Interconnect. In the latter,
  OneView restricts that only one network can be configured to use it.

- "flat_net_mappings" are used to define manual mappings of specific flat provider networks from Neutron to existing Untagged networks in OneView. This configuration can be done to allow OneView administrator to use a configured environment instead of create an entire new one interacting with OpenStack. When a network is mapped with "flat_net_mappings" no operations in OneView are performed since it is considered that all environment was correctly configured by OneView Administrator.

In the case of Port Operations, only ports related to managed networks and with
the "local_link_information" field populated are considered. When the driver
identifies that "local_link_information" exists in a given port, it checks if
it contains a Server Hardware UUID and boot information. The mech driver also
uses the information of the MAC address of the requested port to identify the
specific NIC of the Server Profile where the operation should be executed.
This information can be directly configured in the Neutron port or passed by
Ironic port field "local_link_connection".

Considering these restrictions, OneView Mechanism Driver is capable of:

- Create a network in OneView for each network in Neutron to physical provider-networks configured in the driver config file

- Add networks to Uplink Sets in OneView according to Uplink Set mappings defined to the physical provider-network in the driver config file

    - "Ethernet" Uplink Sets are used with "vlan" typed provider networks
    - "Untagged" Uplink Sets are used with "flat" typed provider networks
    - Other kinds of Uplink Sets neither other types of provider networks are used

- Manual mapping of Neutron flat networks onto specified pre-existing networks of OneView

    - This covers migration from the flat model to the multi-tenant model

- Create, remove and update connections in Server Profiles, implementing Neutron port binding

    - Works only with vif_type = baremetal
    - Expects Server Hardware UUID and boot priority in the local_link_information of the port

OneView Mechanism Driver also implements a fault tolerance process to guarantee
that all networks and ports that are present in Neutron are correctly reflected
in OneView. To ensure that, the verification is executed in the startup of the
mechanism driver to check if all the networks and ports which were managed in a
prior execution still need to be reflected and, in the same way, if new one
should be created in OneView based in the information from the configuration
file.

This synchronization process will consider the information of the networks
indicated to be managed by the mechanism driver
(uplink_set_mappings and flat_net_mappings) from the configuration file and
the information stored in the OneView Mechanism Driver tables present in
OpenStack Database.

Initially, mapped provider networks are obtained from the configuration file
and all networks belonging to them are obtained from Neutron. The mechanism
driver checks if these networks are present in its tables and if any of them is
missing they will be added in the database, created in the OneView and attached
to the configured Uplink Sets. After this verification, if any network not
present in the list obtained from Neutron still exists in the database they
will be erased from OneView and removed from the table.

In the same way, OneView Mechanism Driver checks the consistence of the ports
related with the managed networks with the connections of the server profiles
related with the server hardware used by OpenStack. As Neutron Ports stores
the “server_hardware_uuid” received by the local_link_information, the
Mechanism Driver gets the information for each port and check if the Server
Profile used by the indicated Server Hardware have a connection correctly
representing this port, and if not, creates it.

Ironic Configuration
====================
By default, Ironic is configured to use flat networks during deployment process.
In order to use Ironic-Neutron integration to provide networks isolation during
deployment, some configuration is necessary. In ironic.conf file the following
configuration should be done:

::

    [DEFAULT]
    enabled_network_interfaces = flat,noop,neutron
    default_network_interface = neutron

    [neutron]
    cleaning_network_uuid = neutron_cleaning_network_UUID
    provisioning_network_uuid = neutron_provisioning_network_UUID

As mentioned in the previous section, the OneView Mechanism Driver needs to receive
the “local_link_connection” from Ironic ports to perform networking ports operations.
Once Ironic ports don’t have any information stored by default, it’s necessary to
update existing ports with the desired data to data field as follow:

::

    ironic --ironic-api-version 1.22 port-update IRONIC_NODE_ID replace local_link_connection="{\"switch_id\": \"aa:bb:cc:dd:ee:ff\", \"port_id\": \"\", \"switch_info\": \"{'server_hardware_uuid': 'value', 'bootable':'true/false'}\"}"

In “local_link_connection”, switch_id and port_id are necessary to identify the specific
switch/port where the operation should be performed, but as OneView Mechanism Driver
doesn’t deals directly with switches, this information is not necessary. “switch_info”
attribute can receive any information and because of it, will be to configured with
information demanded by OneView Mechanism Driver. Two information need to be passed:
‘server_hardware_uuid’ and ‘bootable’. ‘server_hardware_uuid’ identifies in which
Server Hardware the connection to represent the new port will be created and ‘bootable’
indicates if this connection will be bootable or not. To identify the port where the
connection need to be created, the MAC address already configured in the Ironic port will be used.

Install using DevStack
======================

1. Install with PIP:
 
- Requirement: Python => 2.7.9

- To install the OneView Mechanism Driver, run:

::

  $ pip install networking-oneview

- Go to the Configuration section

2. Install with GIT:

- Make the git clone of the mech driver files for a folder of your choice <download_directory>:

::

    $ git clone git@git.lsd.ufcg.edu.br:ironic-neutron-oneview/networking-oneview.git

- Access the folder <networking-oneview>:

::

    $ cd networking-oneview

- Run:

::

    $ pip install .

- Go to the Configuration section


Configuration
=============

1. Making ml2_conf.ini file configurations:

- Edit the /etc/neutron/plugins/ml2/ml2_conf.ini file. Find the correspondent line and insert the word *oneview* as follow:

::

    mechanism_drivers = <others Drivers>,oneview

- Find the correspondent line and insert the words *flat,vlan* as follow:

::

    tenant_network_types = vxlan,flat,vlan

- Find the correspondent line and insert the flat physical networks:

::

    [ml2_type_flat]

    flat_networks = public,<flat-physical-network1-name>,<flat-physical-network2-name>*

- Find the correspondent line and insert the vlan physical networks:

::

    [ml2_type_vlan]

    network_vlan_ranges = public,<vlan-physical-network1-name>,<vlan-physical-network2-name>

2. ml2_conf_oneview.ini file configurations:

::

  Edit the /etc/neutron/plugins/ml2/ml2_conf_oneview.ini file.

“ov_refresh_interval” is used to configure the period (in seconds) in which the mechanism driver will execute the periodic synchronization to check if any inconsistence exists between Neutron and OneView and correct them if possible. This attribute is optional and if not configured the default value is 3600 seconds.

To set TLS options for the communication with OneView, it is necessary to download the credentials(appliance.com.crt) from OneView.

- Examples of the lines are:

::

    oneview_host=1.2.3.4

    username=admin

    password=password

    uplinkset_mappings=PHYSNET1:LOGICAL_INTERCCONECT_GROUP_UUID:UPLINK_NAME1,PHYSNET2:LOGICAL_INTERCCONECT_GROUP_UUID:UPLINK_NAME2

    flat_net_mappings=PHYSNET3:ONEVIEW_NETWORK_ID,PHYSNET4:ONEVIEW_NETWORK_ID2

    ov_refresh_interval=3600

    tls_cacert_file = /home/ubuntu/certificate/appliance.com.crt

3. Restart Neutron and upgrade Database:

- Upgrade Database:

::

$ neutron-db-manage upgrade heads

- Restart the neutron service adding the new configuration file using '--config-file /etc/neutron/plugins/ml2/ml2_conf_oneview.ini'. Example:

::

$ /usr/local/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini --config-file /etc/neutron/plugins/ml2/ml2_conf_oneview.ini & echo $! >/opt/stack/status/stack/q-svc.pid; fg || echo "q-svc failed to start" | tee "/opt/stack/status/stack/q-svc.failure"

- If everything is well, the mechanism driver is working.

Install using OpenStack
=======================

To install the OneView Mechanism Driver, access the virtual environment Neutron Server Container, execute:

::

 $ sudo source /openstack/venvs/neutron-master/bin/activate

1. Install with PIP

- Requirement: Python => 2.7.9

- To install the OneView Mechanism Driver, run:

::

    $ pip install networking-oneview

- Go to the Configuration section

2. Install with GIT

- Make the git clone of the mech driver files for a folder of your choice <download_directory>:

::

    $ git clone git@git.lsd.ufcg.edu.br:ironic-neutron-oneview/networking-oneview.git

- Access the folder <networking-oneview>:

::

    $ cd networking-oneview

- Run:

::

    $ pip install .

- Go to the Configuration section

Configuration
=============

1. Making ml2_conf.ini file configurations:

- Edit the /etc/neutron/plugins/ml2/ml2_conf.ini file. Find the correspondent line and insert the word *oneview* as follow:

::

    mechanism_drivers = <others Drivers>,oneview

- Find the correspondent line and insert the words *flat,vlan* as follow:

  These following configurations need to be made on both containers (Neutron Server and Neutron Agent):

::

    tenant_network_types = vxlan,flat,vlan

- Find the correspondent line and insert the flat physical networks:

  These following configurations need to be made on both containers (Neutron Server and Neutron Agent):

::

    [ml2_type_flat]

    flat_networks = public,<flat-physical-network1-name>,<flat-physical-network2-name>*

- Find the correspondent line and insert the vlan physical networks:

  These following configurations need to be made on both containers (Neutron Server and Neutron Agent):

::

    [ml2_type_vlan]

    network_vlan_ranges = public,<vlan-physical-network1-name>,<vlan-physical-network2-name>

2. ml2_conf_oneview.ini file configurations:

::

  Edit the /etc/neutron/plugins/ml2/ml2_conf_oneview.ini file.

“ov_refresh_interval” is used to configure the period (in seconds) in which the mechanism driver will execute the periodic synchronization to check if any inconsistence exists between Neutron and OneView and correct them if possible. This attribute is optional and if not configured the default value is 3600 seconds.

To set TLS options for the communication with OneView, it is necessary to download the credentials(appliance.com.crt) from OneView.

- Examples of the lines are:

::

    oneview_host=1.2.3.4

    username=admin

    password=password

    uplinkset_mappings=PHYSNET1:LOGICAL_INTERCCONECT_GROUP_UUID:UPLINK_NAME1,PHYSNET2:LOGICAL_INTERCCONECT_GROUP_UUID:UPLINK_NAME2

    flat_net_mappings=PHYSNET3:ONEVIEW_NETWORK_ID,PHYSNET4:ONEVIEW_NETWORK_ID2

    ov_refresh_interval=3600

    tls_cacert_file = /home/ubuntu/certificate/appliance.com.crt

3. In Neutron Agent, edit /etc/neutron/plugins/ml2/linuxbridge_agent.ini to mapping neutron ports used by container as follow:

::

 [linux_bridge]
 physical_interface_mappings = <flat-physical-network1-name>:eth12,<vlan-physical-network1-name>:eth11

4. Restart Neutron and upgrade Database:

- Upgrade Database in virtual environment:

::

$ neutron-db-manage upgrade heads

- Edit the /etc/systemd/system/neutron-server.service file.

::

 - In the line ExecStart=/openstack/venvs/neutron-master/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini --log-file=/var/log/neutron/neutron-server.log

 - Change to ExecStart=/openstack/venvs/neutron-master/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini --config-file /etc/neutron/plugins/ml2/ml2_conf_oneview.ini --log-file=/var/log/neutron/neutron-server.log

- Restart the neutron service, execute:

::

 systemctl daemon-reload && service neutron-server restart

Restart the neutron-agent container:

::

  service neutron-linuxbridge-agent restart

- If everything is well, the mechanism driver is working.

5. Configuring haproxy timeout in the outside container (host):

- To set the time on haproxy, edit the files:

::

- Edit /etc/haproxy/conf.d/00-haproxy and /etc/haproxy/haproxy.cfg files

- In the defaults section of the files, change the following lines to:

::

    timeout client 5000s
    timeout connect 10s
    timeout server 5000s

Restart the haproxy service:

::

 systemctl restart haproxy.service

License
=======

OneView ML2 Mechanism Driver is distributed under the terms of the Apache
License, Version 2.0. The full terms and conditions of this license are detailed
in the LICENSE file.

Contributing
============

You know the drill. Fork it, branch it, change it, commit it, and pull-request
it. We are passionate about improving this project, and glad to accept help to
make it better. However, keep the following in mind:

-  Contributed code must have the same license of the repository.

- We reserve the right to reject changes that we feel do not fit the scope of this project, so for feature additions, please open an issue to discuss your ideas before doing the work.

- If you would like to contribute to the development of OpenStack, you must follow the steps in this page:

    http://docs.openstack.org/infra/manual/developers.html

- Once those steps have been completed, changes to OpenStack should be submitted for review via the Gerrit
  tool, following the workflow documented at:

    http://docs.openstack.org/infra/manual/developers.html#development-workflow
