# HPE OneView drivers for Ironic

## OpenStack Ironic integration

HPE OneView is a single integrated platform that implements a software-defined
approach to manage physical infrastructure environments. Besides all that, HPE
OneView also exposes a RESTful API that allows operators and developers to
build custom workloads to best fit their needs.

Due special requirements e.g. high performance needs, cloud providers may want
to provide bare metal servers to their customers instead of virtual machines.
In the OpenStack ecosystem, the component responsible for provisioning bare
metal machines is named Ironic. In the most basic scenario, Ironic achieves
this goal communicating with other three main OpenStack components: i) `Nova`
compute service; ii) `Glance` image service; and iii) `Neutron` networking
service.

The integration of management systems, such as HPE OneView, is made possible in
Ironic through the implementation of drivers. This way, OneView drivers
implements well defined interfaces in Ironic and uses OneView RESTful API to
execute actions that will be performed in the physical machines. For example,
the drivers use OneView RESTful API when powering machine on/off and rebooting;
changing boot device; and when creating and removing a *Server Profile*.

Currently HPE has two drivers that allows cloud providers to deploy bare metal
instances using OneView, the `agent_pxe_oneview` and `iscsi_pxe_oneview`. Both
drivers use Preboot eXecution Environment (PXE) technology for boot and differs
only in the technology used for deploying the instance as detailed in this
documentation.

### Agent PXE OneView driver

The deployment process can be broken down into three phases as explained below.

Firstly, the `Server Hardware` will be allocated to Ironic. Once the operator
configures the bare metal node to use `agent_pxe_oneview` driver and Ironic
gets a request to deploy an image on it, the driver checks if the node is free
for use by Ironic and applies a `Server Profile` created based on a given
`Server Profile Template` at OneView.

The next step is to download the deploy images with `Ironic Python Agent (IPA)`
embedded. The driver then sets the bare metal node to boot from `PXE`,
configures network options for this node at Neutron and power on the node,
triggering `PXE` boot. Then the node downloads the deploy images through
`Trivial File Transfer Protocol (TFTP)` according to the configuration provided
by the `Dynamic Host Configuration Protocol (DHCP)` server.

Finally, once the node is powered on, the IPA at the node downloads the user
images from Ironic via `HTTP` and writes it to disk. After this operation is
finished, Ironic sets the bare metal node to boot from `disk`, change the
network configuration at Neutron if needed and reboot it, finishing the
instance deployment.

### iSCSI PXE OneView driver

The deployment process using `iscsi_pxe_oneview` driver can be described in the
same way the `agent_pxe_oneview` driver was above.

Firstly, the `Server Hardware` will be allocated to Ironic. Once the operator
configures the bare metal node to use `iscsi_pxe_oneview` driver and Ironic
gets a request to deploy an image on it, the driver checks if the node is free
for use by Ironic and applies a `Server Profile` created based on a given
`Server Profile Template` at OneView.

The next step is to download the deploy images containing `IPA`. The driver
then sets the bare metal node to boot from `PXE`, configures `DHCP` options
for this node at Neutron and power on the node, triggering the download of the
deploy images through `TFTP` according to the configuration provided by the
`DHCP` server.

Once the node is powered on, the `IPA` informs Ironic to continue the
deployment. Ironic then wipes out the disk of the node and writes the user
image. After this operation is finished, Ironic configures the node boot loader
partition, sets the bare metal node to boot from `disk`, reboot it and change
the network configuration at Neutron if needed, finishing the instance
deployment.

### Requirements
* HPE OneView
  * HPE OneView 2.0
  * HPE OneView 3.0

* HPE Blade Lines:
  * BL 460c Gen 8 (Tested)
  * BL 460c Gen 9  (Tested)
  * BL 465c Gen 8 (Tested)
  * BL 660c Gen 8
  * BL 660c Gen 9


* HPE Density Lines (requires iLO 4 with Redfish):
  * DL 360 Gen 9 (Tested)
  * DL 360e Gen 8
  * DL 360e Gen 9
  * DL 360p Gen 8
  * DL 360p Gen 9

## OpenStack Ansible

Teams of operators spend so much time and effort to setup, tuning and
maintaining OpenStack cloud environments and automating that workflow became a
hot topic in the OpenStack community. Automation engines like TripleO, Salt,
Chef, Puppet and Ansible started to be used and well adopted by the community
to automate the OpenStack deployment workflow.

For this documentation the OpenStack Ansible, also known as OSA, was chosen and
the process of OpenStack deployment is fully described below.

### Install

Copy your SSH key to the server where the OpenStack will be deployed.

```bash
ssh-copy-id USER@SERVER_IP
```

Then, access the server:

```bash
ssh USER@SERVER_IP
```

Update package lists from the repositories:

```bash
apt-get update
```

Install dependencies:

```bash
apt-get install -y git build-essential openssh-server \
  python-dev python-virtualenv virtualenv openvswitch-switch
```

Clone OpenStack Ansible project:
```bash
git clone https://github.com/openstack/openstack-ansible.git \
    /opt/openstack-ansible
```

Install Ansible:

```bash
source /opt/openstack-ansible/scripts/bootstrap-ansible.sh
```

Edit Ansible Bootstrap file /opt/openstack-ansible/tests/bootstrap-aio.yml:

```yaml
- name: Bootstrap the All-In-One (AIO)
  hosts: localhost
  user: root
  roles:
    - role: "sshd"
    - role: "pip_install"
    - role: "bootstrap-host"
      openstack_confd_entries: "{{ confd_overrides[scenario] }}"
      scenario: "{{ lookup('env','SCENARIO') | default('aio', true) }}"
      confd_overrides:
        aio:
          - name: glance.yml.aio
          - name: horizon.yml.aio
          - name: keystone.yml.aio
          - name: ironic.yml.aio
          - name: neutron.yml.aio
          - name: nova.yml.aio
          - name: swift.yml.aio
```

Run the pre-installation script:

```
source /opt/openstack-ansible/scripts/bootstrap-aio.sh
```

Modify the default passwords in `/etc/openstack_deploy/user_secrets.yml`.

Deploy the OpenStack cloud environment:

```bash
source /opt/openstack-ansible/scripts/run-playbooks.sh
```

> Note: The deployment will take about 90 minutes.


## Configuration


### Neutron configuration

Once the OpenStack deployment is fully complete the next step is to configure
the network. OSA creates by default four bridges. The management bridge is
responsible for connecting all containers in the installation and also makes
possible ironic nodes to reach DHCP and then TFTP services running in the
neutron and ironic conductor respectively.

Turn the deploy interface up:

```bash
ip link set $CONTROLLER_DEPLOY_INTERFACE up
```

Add the deploy interface to the management bridge:

```bash
brctl addif br-mgmt $CONTROLLER_DEPLOY_INTERFACE
```

Find the `br-mgmt` bridge gateway:

```bash
ifconfig br-mgmt
```

Create an environment variable to store the `br-mgmt` bridge gateway:

```bash
GATEWAY_IP = $MANAGEMENT_BRIDGE_IP
```

Find an available IPs interval to be allocated to the nodes requesting DHCP:

```bash
lxc-ls -f
```
> Note: look at the IPs used by all containers and find an available IP
interval.

Store the start and end interval:

```bash
START_POOL_IP = $START_IP
END_POOL_IP = $END_IP
```

Attach to the container:

```bash
lxc-attach -n aio1_utility_container
```

Load the credentials:

```bash
source /root/openrc
```

Create the `flat` network:

```bash
openstack network create \
  --provider-physical-network flat \
  --provider-network-type flat \
  $FLAT_NETWORK_NAME
```

Create the subnet:

```bash
openstack subnet create \
  --network $FLAT_NETWORK_NAME_OR_UUID \
  --allocation-pool start=$START_POOL_IP,end=$END_POOL_IP \
  --gateway $GATEWAY_IP \
  --subnet-range $MANAGEMENT_MASK_IN_CIDR_FORMAT \
  $SUBNET_NAME
```

### Ironic configuration

Attach to the container:

```bash
lxc-attach -n aio1_utility_container
```

List and copy the network uuid:

```bash
openstack network list
```

Attach to the ironic conductor container:

```bash
lxc-attach -n aio1_ironic_conductor_container
```

In the section `[DEFAULT]` edit enabled drivers like this:

```
enabled_drivers = agent_pxe_oneview,iscsi_pxe_oneview

```

In the section` [conductor]` edit automated clean like this:

```
automated_clean = True
```

In the section `[neutron]` edit cleaning network pasting the network `uuid`:

```
cleaning_network = $NETWORK_NAME_OR_UUID
```

In the section `[oneview]` edit the variables like this:

```
manager_url = $ONEVIEW_MANAGER_URL
username = $ONEVIEW_USERNAME
password = $ONEVIEW_PASSWORD
allow_insecure_connections = $ALLOW_INSECURE_CONNECTIONS
tls_cacert_file = $TLS_CACERT_FILE
max_polling_attempts = $MAX_POLLING_ATTEMPTS
```

Load the ironic-conductor virtual environment:

```bash
source /openstack/venvs/ironic-master/bin/activate
```

Install the python-oneviewclient in the virtual environment:

```bash
pip install python-oneviewclient
```

Restart the ironic conductor service:

```bash
service ironic-conductor restart
```

> Note: Write zeros in the whole disk sometimes is undesired time consuming
task. If want to disable this behavior edit the erase device priority variables
in section `[deploy]` as: `erase_device_priority = 0`

## Launching an instance

Since there is a node in `available` state in ironic, an instance can be
requested to nova compute service. It can be done through `horizon` web
interface or via OpenStack command line interface:

```bash
openstack server create \
  --image $USER_IMAGE_NAME_OR_UUID \
  --flavor $FLAVOR_NAME_OR_UUID \
  --nic net-id=$FLAT_NETWORK_NAME_OR_UUID \
  $SERVER_NAME
```

## Optional tools

There are two tools to assist the creation and management of nodes using HPE
OneView drivers, the ironic-oneview-cli and ironic-oneviewd.

Install the operating system dependencies:

```bash
apt-get install -y python-pip build-essential python-dev

```
Install the pip dependencies:

```bash
pip install setuptools wheel
```

> Note: If the `pip.conf` file in the machine has some customizations,
installing packages through pip may not work. If so, remove or rename the file
to ensure pip can reach the PyPi index.

### Ironic OneView CLI

Ironic-OneView CLI is a command line interface tool for easing the use of the
OneView Drivers for Ironic. It allows the user to easily create and configure
Ironic nodes compatible with OneView Server Hardware objects and create Nova
flavors to match Ironic nodes that use OneView drivers.

#### Install

Attach to the container:

```bash
lxc-attach -n aio1_utility_container
```

Install the Ironic OneView CLI:

```bash
pip install ironic-oneview-cli
```

#### Configuring credentials

Some initial configuration are needed before to use the tool and the first step
to achieve that is create and initialization file.

To create the initialization file do:

```bash
ironic-oneview genrc > ironic-oneviewrc.sh
```

Open the `ironic-oneviewrc.sh` file and edit the needed fields.

Load the file to export the environment variables:

```bash
source ironic-oneviewrc.sh
```

Load OpenStack `openrc` credential file:

```bash
source /root/openrc
```

#### Node creation

The process of creating a node is interactive. Firstly, ironic-oneview-cli show
the list of available `Server Profile Templates` to the user to be chosen. Once
it does, the tool will show a list of nodes that match the
`Server Profile Template` chosen in the previous step. It is possible to choose
multiple nodes to be enrolled at once.

Attach to the container:

```bash
lxc-attach -n aio1_utility_container
```

Create the node:

```bash
ironic-oneview node-create
```

> Note: The tool has an `--insecure` option to skip SSL certificate validation.

The created nodes can be seen doing:

```bash
openstack baremetal node list
```

#### Flavor creation

The process of creating a flavor is also interactive. The user will be prompted
with a list of `Server Profile Template` for the nodes registered in Ironic.
Different of creating a node, where a list of all the
`Server Profile Templates` in OneView are shown, the `Server Profile Template`
shown when creating a flavor are the ones that match the nodes already created.

The information about disk, memory, cpus and processor architecture within the
template are used to create the flavor. The user will only be asked to choose
the `Server Profile Template` and a name for the flavor. To start the process
of creating a flavor, run:

Attach to the container:

```bash
lxc-attach -n aio1_utility_container
```

Create the flavor:
```
ironic-oneview flavor-create
```

The created flavor can be seen doing:

```bash
openstack flavor list
```

### Ironic OneView Daemon

The ironic-oneviewd is a python daemon of the OneView Driver for Ironic. It
handles nodes in `enroll` and `manageable` provision states in ironic,
preparing them to become `available`. In order to be moved from `enroll` to
`available`, a `Server Profile` must be applied to the `Server Hardware`
represented by a node according to its `Server Profile Template`. This daemon
monitors ironic nodes and applies a `Server Profile` to such `Server Hardware`.

#### Install

Attach to the container:

```bash
lxc-attach -n aio1_ironic_conductor_container
```

Install the Ironic OneView Daemon:

```bash
pip install ironic-oneviewd
```

#### Configuring credentials

Some initial configuration are needed before to use the tool and the first step
to achieve that is to edit the configuration file.

Edit the `/etc/ironic-oneviewd/ironic-oneviewd.conf.sample` accordingly.

Rename the file to `ironic-oneviewd.conf`:

```bash
mv /etc/ironic-oneviewd/ironic-oneviewd.conf.sample \
  /etc/ironic-oneviewd/ironic-oneviewd.conf
```

#### Starting the daemon

Start the daemon:

```bash
ironic-oneviewd
```

## OneView ML2 Mechanism driver for Ironic-Neutron integration

Ironic can be used together with Neutron to allow Layer 2 networking isolation
between the physical machines when running OpenStack instances. To use OneView
as the means to configure the networking in this context, please refer to the
OneView ML2 Mechanism Driver for Neutron and its documentation that can be
found in the `networking-oneview` directory of this repository.

## Glossary

* Blade Line (BL): HPE ProLiant enclosure-based server models.

* Density Line (DL): HPE ProLiant rack-based server models.

* Dynamic Host Configuration Protocol (DHCP): stands for, a protocol to provide
network configuration such as IP, subnet mask and default gateway, in a
client/server fashion.

* Hypertext Transfer Protocol (HTTP): application protocol for World Wide Web.

* Integrated Lights-Out (iLO): proprietary embedded server management
technology by HPE which provides out-of-band management facilities
(e.g. power on/off, reset, mount image).

* Ironic Python Agent (IPA): An agent for controlling and deploying Ironic
controlled baremetal nodes.

* Pre eXecution Environment (PXE): is a standardized environment that runs a
assembly software that permits boot by NIC.

* Server Profile (SP): Server Hardware configuration entity including firmware
baseline, BIOS settings, network connectivity, boot configuration, Integrated
Lights-Out (iLO) settings, and unique IDs.

* Server Profile Template (SPT): Template for creation of Server Profiles.

* Trivial File Transfer Protocol (TFTP): is a utility to transfer files using
FTP generally in early stages of boot when user authentication is not required.

* OpenStack Ansible (OSA): is an official OpenStack project which aims to
deploy production environments from source in a way that makes it scalable
while also being simple to operate, upgrade, and grow.

* Secure Shell (SSH): is a cryptographic network protocol for operating network
services securely over an unsecured network. The best known example application
is for remote login to computer systems by users.

* Secure Sockets Layer (SSL): is a cryptographic protocol that provide
communications security over a computer network.
