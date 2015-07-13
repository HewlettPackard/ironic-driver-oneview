# HP OneView driver for Ironic

## Introduction

[HP OneView][1] is a single integrated platform, packaged as an appliance that
implements a software-defined approach to manage physical infrastructure. The
appliance supports scenarios such as deploying bare metal servers and
hypervisor clusters from bare metal servers, for instance. In this context,
the *HP OneView driver* for Ironic integrates them both and enables the users
of OneView to use Ironic as a bare metal provider to their managed physical
hardware.

The driver implements the [core interfaces of an Ironic Driver][2] and uses
the [OneView Rest API][3] to provide communication between Ironic and
OneView.

In order to provide a better user experience, the driver offers additional
features when managing bare metal servers together with OneView:
* Automated Nova flavor creation based on OneView resources
* Automatic Ironic node inventory synchronization with OneView
* Handling of Ironic nodes that are in use by other OneView users
* Instance deployment using PXE

These features include external services that communicate with our driver and
the OneView appliance in order to provide a synchronization mechanism to
automatically synchronize Ironic nodes and OneView managed hardware.

What not to expect from the current driver:
* As Ironic only supports the use of flat networks on Kilo, don't expect to use
tenant networks on the deployed nodes
* Server storage is assumed to be consistent among all OneView based servers,
don't expect variance in physical storage to effect Ironic node scheduling

To provide a bare metal instance the agents involved in the process are three:
* Ironic service
* OneView appliance
* OneView driver

The role of Ironic is to serve as a bare metal provider to OneView's managed
physical hardware and to provide communication with other necessary OpenStack
services such as Nova and Glance. When Ironic receives a boot request coming
from Nova, it works together with the OneView driver to access a machine in
OneView, the driver being responsible for the communication with the OneView
appliance.

Once the deployment process starts, the deployment interface of the driver is
called by the *Ironic Conductor*, and then the driver is in charge of preparing
the selected Server Hardware object, the entity in OneView that represents a
machine, so that it can enter in the PXE process. After the driver preparation,
the Server Hardware enters in the [PXE process][4], and from that point the
machine communicates with the [TFTP][5] server to access the images to be
deployed and restarts twice in order to install the user image. When the machine
finishes this process, the OpenStack user will have SSH access to the machine
(attention to the use of a cloud-init script to provide credentials).

## Installation

In this tech preview we aim to support the Kilo version of Ironic. For new
installs of Ironic in a running Openstack Kilo cloud, follow
[these instructions][11].

If you want to test the driver in a Devstack setup with Ironic enabled,
follow [these instructions][6] to clone it and configure it (bear in mind that,
for testing purposes, you can leave some services such as Horizon enabled).
**Don't forget to checkout to the stable Kilo branch in your Devstack before
stacking.**

```
#In the devstack/ source directory

git checkout stable/kilo
bash stack.sh
```
The next step is to clone the OneView driver:

```
git clone https://git.lsd.ufcg.edu.br/ironicdrivers/ironic_drivers.git
```

Once the driver is cloned, in order to add the OneView driver code to Ironic's
code base, first set the following variables to the paths to your Ironic and
OneView driver directories:

```
REPOSITORY_HOME=<path to the driver repository>
IRONIC_HOME=<path to your existing Ironic>
```

Now in the *ironic_drivers* source directory run:

```
bash update_stack_with_oneview_driver.sh
```

### Adding the driver to setup.cfg

The *setup.cfg* file in Ironic still needs to be edited to include our driver.
Add the two entry lines below to *setup.cfg* in the Ironic source directory:

```
fake_oneview = ironic.drivers.oneview:FakeOneViewDriver
pxe_oneview = ironic.drivers.oneview:OneViewDriver
```

The *pxe_oneview* driver uses PXE for deployment whilst *fake_oneview* is a
fake driver, used for testing purposes.

After that, still in the Ironic source directory, execute *setup.py* to add the
drivers to Ironic's environment:

```
sudo python setup.py install
```

### Configuring ironic.conf

In */etc/ironic/ironic.conf*, add the driver to the *enabled_drivers* tag:

```
enabled_drivers = pxe_oneview
```

Now, in order to provide the credentials to access the OneView appliance,
add a [oneview] section to *ironic.conf* with the following fields

```
[oneview]

manager_url = https://my.oneview.com
username = my_username
password = my_password
allow_insecure_connections = false
tls_cacert_file = /my/cacert/path/if/any
max_retries = 20
```

* manager_url: refers to the address of the OneView appliance;
* username and password: the OneView credentials the driver is going to use;
* allow_insecure_connections: leave this *true* if you want the driver not to
validate the certificate provided by OneView in the TLS connection;
* tls_cacert_file: path to the CA certificate file; if blank, the system's
trust store will be used to validate certificates in secure connections;
* max_retries: max connection retries the driver uses to check if changes
occurred on OneView

Finally, **restart the ironic-conductor service** and you should have
Ironic ready to use our *pxe_oneview* driver.

In Openstack:

```
service ironic-conductor restart
```

In Devstack:

```
# Go to the devstack source directory

bash rejoin-stack.sh

# (Ctrl+a ") to change the screen
# Navigate to ir-cond (ironic-conductor service)
# (Ctrl+c) to stop the service
# (Up arrow, Enter) to restart the service
```

## Networking

For the sake of example, we assume that the network connecting Ironic and the
Enclosure has its configuration as shown in Figure 1.

![network](doc/images/network_layout.png?raw=true)

Figure 1. Example of a suitable network layout

Since Ironic currently only supports flat networks, all Server Profile
Templates must be configured so the first NIC is connected to the same network
and this network shall have an uplink port to the network where the
ironic-conductor is running (if it's not running from a blade in the same
enclosure).

To enable the flat network to be used in the deployment process, first, create
the following OpenVSwitch bridge and port:

```
sudo ovs-vsctl add-br br-em1
sudo ovs-vsctl add-port br-em1 em1
```

Next, configure the *Neutron ML2 plugin* following the Step 1 of this
[guide][7].

You can now create and configure a *Neutron flat network* and its *subnet*,
both of which will be associated to an instance at deploy time.

```
TENANT_ID=<your-tenant-id>
FLAT_NET_NAME=<name-of-your-flat-net>

neutron net-create --tenant-id $TENANT_ID $FLAT_NET_NAME --shared --provider:network_type flat --provider:physical_network physnet1

SUBNET_NAME=<name-of-your-subnet>

neutron subnet-create $FLAT_NET_NAME 192.168.2.0/24 --name $SUBNET_NAME --ip-version=4 --gateway=192.168.2.1 --enable-dhcp
```

To check if your network was successfully created in *Neutron*, run:

```
neutron net-list
```

Now, add the network IP and its subnet mask to the bridge br-em1 created
previously:

```
sudo ip addr add 192.168.2.1/24 dev br-em1
```

This way you are stating that all instances with this range of IPs belong to
this network.

Finally, **ensure [Ubuntu's Uncomplicated Firewall][12] is disabled** in order
to allow TFTP traffic and, therefore, perform a proper deployment:

```
sudo ufw disable
```

## Deploying

### Server Profiles in OneView

*Server Profiles* are logical entities that capture key aspects of a server
configuration, enabling the OneView users to provision converged hardware
infrastructure quickly and consistently. Information such as the type of
hardware the Server Profile is associated to, boot settings, BIOS/UEFI
settings, firmware configuration and network connections are encapsulated in
this entity.

*Server Profile Templates* (SPT) are Server Profiles not assigned to any Server
Hardware. At deploy time, they are cloned and assigned to a specific Server
Hardware.

In our scenario, Nova flavors are created based on SPTs and their
configurations. These SPTs in OneView must be configured according to the
following guidelines:

* Firmware: should be set to *Managed manually* in order to save time when
applying a Server Profile to a Server Hardware;
* Connections: flat network connecting the devices to a single switch;
* Physical MAC address: when applying a Server Profile to a Server Hardware a
physical MAC address needs to be provided since Ironic must know this
info prior to a Server Profile assignment; Also, the first NIC (Network
Interface Card) of an SPT should be always in the same network as
the machine with the Ironic service.

![server-profile](doc/images/ov_server_profile.png?raw=true)

Figure 2. Example of a Server Profile Template in OneView

### Creating deploy and user images

In order to create suitable images for bare metal provisioning, deploy and
user images, we suggest the use of [disk-image-builder][8].

To create kernel and ramdisk deploy images, run:

```
DEPLOY_IMAGES_NAME=<name-of-your-images>

ramdisk-image-create ubuntu deploy-ironic -o $DEPLOY_IMAGES_NAME
```

This will generate a *.kernel* and a *.initramfs* files which you should now
add to *Glance*, as follows

```
glance image-create --name <name-of-your-kernel-image> --is-public True --disk-format aki < $DEPLOY_IMAGES_NAME.kernel

glance image-create --name <name-of-your-ramdisk-image> --is-public True --disk-format ari < $DEPLOY_IMAGES_NAME.initramfs
```

Now, create the user image to be deployed

```
USER_IMAGES_NAME=<name-of-your-user-images>

DIB_CLOUD_INIT_DATASOURCES="ConfigDrive, OpenStack" disk-image-create -o $USER_IMAGES_NAME ubuntu baremetal dhcp-all-interfaces
```

The *DIB_CLOUD_INIT_DATASOURCES* parameter ensures all cloud-init
configuration is going to be applied to the deployed instance, including user
and password credentials, public key authentication and many other possible
[config options][9].

This will generate a *.initrd*, *.vmlinuz* and *.qcow2* files which will be
used to form your final user image when adding it to *Glance*, as follows

```
glance image-create --name <your-user-image-kernel-name> --is-public True --disk-format aki  < $USER_IMAGES_NAME.vmlinuz
USER_KERNEL_UUID=<id-of-kernel-image>

glance image-create --name <your-user-image-ramdisk-name> --is-public True --disk-format ari  < $USER_IMAGES_NAME.initrd
USER_RAMDISK_UUID=<id-of-ramdisk-image>

glance image-create --name <your-user-image-name> --is-public True --disk-format qcow2 --container-format bare --property kernel_id=$USER_KERNEL_UUID --property ramdisk_id=$USER_RAMDISK_UUID < $USER_IMAGES_NAME.qcow2
```

To check if your images were successfully added to *Glance*, run:

```
glance image-list
```

## Creating flavors

The process of creating Nova flavors based on OneView's SPTs is automated by
the `ov-flavor` script.

In order to run the script, you can use environment variables or use command
line parameters.

To use environment variables, if you have an `openrc` file to your cloud (if
you're using Devstack, there is one in its source directory), run:

```
source openrc $OS_USERNAME $OS_TENANT_NAME
```

If you don't have an `openrc` file, you'll need to set the following Openstack
variables:

```
OS_TENANT_NAME=<your-openstack-tenant-name>
OS_USERNAME=<your-openstack-username>
OS_PASSWORD=<your-openstack-password>
OS_AUTH_URL=<your-openstack-keystone-v2-api-url>
```

Then, set the credentials to access the OneView appliance:

```
OV_USERNAME=<your-oneview-username>
OV_PASSWORD=<your-oneview-password>
OV_ADDRESS=<https://your.oneview.address>
```

Go to *ironic_drivers/shell* and, if the credentials above are correctly set,
only run

```
bash ov-flavor.sh create-flavors
```

However, if you want to run it with inline parameters, run:

```
bash ov-flavor.sh --os-tenant-name <your-openstack-tenant-name> --os-username <your-openstack-username> --os-password <your-openstack-password> --os-auth-url <your-openstack-auth-url> --ov-username <your-oneview-username> --ov-password <your-oneview-password> --ov-address <https://your.oneview.address>
```

You should now be able to see the possible flavors to be created and a
prompt asking for the id of the flavor you want to create. The next step is to
choose the name of the flavor which can either be customised or the default
suggested by `ov-flavor`.

Press *Enter* and, if everything goes well, your flavor will be shown when
running:

```
$ nova flavor-list
+--------------------------------------+-----------------------------------------------+-----------+------+-----------+------+-------+-------------+-----------+
| ID                                   | Name                                          | Memory_MB | Disk | Ephemeral | Swap | VCPUs | RXTX_Factor | Is_Public |
+--------------------------------------+-----------------------------------------------+-----------+------+-----------+------+-------+-------------+-----------+
| 3ec7b46d-a5c0-4d8a-8fe6-baf75b6e3228 | ServerProfile7-Demo-32768MB-RAM_12_x86_64_120 | 32768     | 120  | 0         |      | 12    | 1.0         | True      |
+--------------------------------------+-----------------------------------------------+-----------+------+-----------+------+-------+-------------+-----------+
```

## Creating nodes

The process of creating, removing and putting Ironic nodes in maintenance mode
based on OneView Server Hardware objects is automatically performed by the
sync-service. OneView's [RabbitMQ][10] message bus is used to listen to events,
such as added and deleted Server Hardware objects. The sync-service processes
these events and takes the corresponding actions on Ironic.

### Configuring sync.conf

Copy the *ironic_drivers/sync-service/sync.conf.sample* as
*ironic_drivers/sync-service/sync.conf*  and configure it as follows:

```
[ironic]

default_deploy_kernel_id = <your-deploy-kernel-image-id>
default_deploy_ramdisk_id = <your-deploy-ramdisk-image-id>
default_sync_driver = pxe_oneview

[oneview]

manager_url = https://my.oneview.com
username = my_username
password = my_password
allow_insecure_connections = false
tls_cacert_file = /my/cacert/path/if/any
```

Besides the ones described above, two other sections need to be edited to
contain your Openstack credentials, which are the [keystone_authtoken] and
[nova] sections. Configure these sections in the same way it's configured on
ironic.conf and nova.conf.

Now, with these options configured, go to the *sync-service* directory and run:

```
bash sync-service.sh
```

The service should now be up and running, synchronizing Ironic's inventory
with the events from OneView, which includes creating, removing and putting
nodes in maintenance mode if in use by other OneView users.

[1]: http://www8.hp.com/us/en/business-solutions/converged-systems/oneview.html

[2]: http://docs.openstack.org/developer/ironic/dev/architecture.html#drivers

[3]: http://h17007.www1.hp.com/docs/enterprise/servers/oneviewhelp/oneviewRESTAPI/content/images/api/index.html

[4]: http://en.wikipedia.org/wiki/Preboot_Execution_Environment

[5]: http://pt.wikipedia.org/wiki/Trivial_File_Transfer_Protocol

[6]: http://docs.openstack.org/developer/ironic/dev/dev-quickstart.html#deploying-ironic-with-devstack

[7]: http://docs.openstack.org/developer/ironic/deploy/install-guide.html#configure-neutron-to-communicate-with-the-bare-metal-server

[8]: https://github.com/openstack/diskimage-builder

[9]: http://cloudinit.readthedocs.org/en/latest/topics/examples.html

[10]: https://www.rabbitmq.com/

[11]: http://docs.openstack.org/developer/ironic/deploy/install-guide.html

[12]: https://help.ubuntu.com/community/UFW
