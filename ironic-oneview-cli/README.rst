==================
Ironic-OneView CLI
==================

Overview
========

Ironic-OneView CLI is a command line interface tool for easing the use of the
OneView Drivers for Ironic. It allows the user to easily create and configure
Ironic nodes compatible with OneView ``Server Hardware`` objects and create
Nova flavors to match available Ironic nodes that use OneView drivers. It also
offers the option to migrate Ironic nodes using pre-allocation model to the
dynamic allocation model.

This tool creates Ironic nodes based on the Ironic OneView drivers' dynamic
allocation model [1]_ [2]_.

.. note::
   If you still want to use the deprecated pre-allocation model instead, use
   version 0.0.2 of this tool.
.. note::
   This tool works with OpenStack Identity API v2.0 and v3.
.. note::
   This tool works with OpenStack Ironic API microversion '1.22'.

----

For more information on *HPE OneView* entities, see [3]_.

Installation
============

To install Ironic-OneView CLI from PyPI, use the following command::

    $ pip install ironic-oneview-cli


Configuration
=============

Ironic-Oneview CLI uses credentials loaded into environment variables by
the OpenStack RC **and** by the Ironic-OneView CLI RC files. You can download
the OpenStack RC file from your cloud controller. An Ironic-OneView CLI RC
sample file can be generated using the ``genrc`` subcommand::

    $ ironic-oneview genrc > ironic-oneviewrc.sh

Since you have the ``ironic-oneviewrc.sh`` sample file, you can set the OneView
credentials using your editor and load its environment variables by running::

    $ source ironic-oneviewrc.sh

You can also set credentials by passing them as command line parameters.
To see which parameters to use for setting credentials, use the command::

    $ ironic-oneview help

For more information how to obtain and load the *OpenStack RC* file, see [4]_.


Usage
=====

Once the necessary environment variables and command line parameters are
set, Ironic-OneView CLI is ready to be used.

In the current version of Ironic-OneView CLI, the available subcommands are:

+--------------------+---------------------------------------------------------------+
|     node-create    | Creates nodes based on available HPE OneView Server Hardware. |
+--------------------+---------------------------------------------------------------+
|    flavor-create   | Creates flavors based on available Ironic nodes.              |
+--------------------+---------------------------------------------------------------+
| migrate-to-dynamic | Migrate Ironic nodes to dynamic allocation model.             |
+--------------------+---------------------------------------------------------------+
|        genrc       | Generates a sample Ironic-OneView CLI RC file.                |
+--------------------+---------------------------------------------------------------+
|        help        | Displays help about this program or one of its subcommands.   |
+--------------------+---------------------------------------------------------------+

The ironic-oneview-cli can be run in debugging mode with the --debug parameter, as in::

    $ ironic-oneview --debug node-create


Features
========

Node creation
^^^^^^^^^^^^^

To create Ironic nodes based on available HPE OneView ``Server Hardware`` objects,
use the following command::

    $ ironic-oneview node-create

The tool will ask you to choose a valid ``Server Profile Template`` from those
retrieved from HPE OneView appliance.::

    Retrieving Server Profile Templates from OneView...
    +----+------------------------+----------------------+---------------------------+
    | Id | Name                   | Enclosure Group Name | Server Hardware Type Name |
    +----+------------------------+----------------------+---------------------------+
    | 1  | template-dcs-virt-enc3 | virt-enclosure-group | BL460c Gen8 3             |
    | 2  | template-dcs-virt-enc4 | virt-enclosure-group | BL660c Gen9 1             |
    +----+------------------------+----------------------+---------------------------+

Once you have chosen a valid ``Server Profile Template``, the tool lists the
available ``Server Hardware`` that match the chosen ``Server Profile Template``.
Choose a ``Server Hardware`` to be used as base to the Ironic node you are creating.::

    Listing compatible Server Hardware objects...
    +----+-----------------+------+-----------+----------+----------------------+---------------------------+
    | Id | Name            | CPUs | Memory MB | Local GB | Enclosure Group Name | Server Hardware Type Name |
    +----+-----------------+------+-----------+----------+----------------------+---------------------------+
    | 1  | VIRT-enl, bay 5 | 8    | 32768     | 120      | virt-enclosure-group | BL460c Gen8 3             |
    | 2  | VIRT-enl, bay 8 | 8    | 32768     | 120      | virt-enclosure-group | BL460c Gen8 3             |
    +----+-----------------+------+-----------+----------+----------------------+---------------------------+

Notice that you can create multiple Ironic nodes at once. For that, type
multiple ``Server Hardware`` IDs separated by blank spaces. The created Ironic
nodes will be in the *enroll* provisioning state.

.. note::
   If you have the parameter os_inspection_enabled = True, the created node
   will not have the hardware properties (cpus, memory_mb, local_gb, cpu_arch)
   set in the node properties. This will be discovered during the Ironic
   Hardware Inspection.

----

Alternatively, you can set a ``Server Profile Template`` through command
line and the tool prompt the list of ``Server Hardware`` to be used.
For that, use the following command::

    $ ironic-oneview node-create --server-profile-template-name <spt_name>

Or set the number of nodes you want to create and the tool will show
the list of ``Server Profile Template`` to be chosen. For that, use
the following command::

    $ ironic-oneview node-create --number <number>

.. note::
   You can use both arguments at once.

If you have the Networking OneView ML2 Driver enabled, use the following
command to add this information in the node driver_info::

    $ ironic-oneview node-create --use-oneview-ml2-driver

For more information on *Networking OneView ML2 Driver*, see [5]_.

----

To list all nodes in Ironic, use the command::

    $ ironic node-list

For more information about the created Ironic node, use the command::

    $ ironic node-show <node_uuid>


Flavor creation
^^^^^^^^^^^^^^^

To create Nova flavors compatible with available Ironic nodes, use the
following command::

    $ ironic-oneview flavor-create

The tool will now prompt you to choose a valid flavor configuration, according
to available Ironic nodes.::

    +----+------+---------+-----------+-------------------------------------+----------------------+-------------------------+
    | Id | CPUs | Disk GB | Memory MB | Server Profile Template             | Server Hardware Type | Enclosure Group Name    |
    +----+------+---------+-----------+-------------------------------------+----------------------+-------------------------+
    | 1  | 8    | 120     | 8192      | second-virt-server-profile-template | BL460c Gen9 1        | virtual-enclosure-group |
    +----+------+---------+-----------+-------------------------------------+----------------------+-------------------------+

After choosing a valid configuration ID, you'll be prompted to name the new
flavor. If you leave the field blank, a default name will be used.

----

To list all flavors in Nova, use the command::

    $ nova flavor-list

For more information about the created Nova flavor, use the command::

    $ nova flavor-show <flavor>


Node migration
^^^^^^^^^^^^^^

To migrate pre-allocation Ironic nodes to the Ironic OneView drivers' dynamic
allocation model, use the following command::

    $ ironic-oneview migrate-to-dynamic

The tool will prompt you to choose the available pre-allocation nodes to
migrate, those retrieved from Ironic.::

    Retrieving pre-allocation Nodes from Ironic...
    +----+--------------------------------------+----------------------+---------------------------+--------------------+
    | Id | Node UUID                            | Server Hardware Name | Server Hardware Type Name | Enclose Group Name |
    +----+--------------------------------------+----------------------+---------------------------+--------------------+
    | 1  | 607e269f-155e-443e-83af-d3a553c8b535 | Encl1, bay 6         | BL460c Gen8 1             | VirtualEnclosure   |
    | 2  | 3ca132c0-0769-48d1-a2af-9a67f363345e | Encl1, bay 7         | BL460c Gen8 1             | VirtualEnclosure   |
    | 3  | e9eb685d-cb46-4645-9980-f27b44e472f9 | Encl1, bay 8         | BL460c Gen8 1             | VirtualEnclosure   |
    +----+--------------------------------------+----------------------+---------------------------+--------------------+

Once you have chosen a valid pre-allocation node ID, the tool will migrate the
node to dynamic allocation model. Notice that you can migrate multiple nodes at
once. For that, type multiple nodes ``Id`` separated by blank spaces or type
``all`` to migrate all nodes shown at once.

----

To migrate one or more specific pre-allocation node(s), without showing the
table of pre-allocation nodes available, use the command::

    $ ironic-oneview migrate-to-dynamic --nodes <node_uuid> [<node_uuid> ...]

To migrate all available pre-allocation nodes at once, without showing the
table of pre-allocation nodes available, use the command::

    $ ironic-oneview migrate-to-dynamic --all

Node delete
^^^^^^^^^^^

The tool also offers the option to delete a specific number of Ironic nodes.
For that use the following command::

    $ ironic-oneview node-delete --number <number>

To delete all Ironic nodes, use the command::

    $ ironic-oneview node-delete --all

References
==========
.. [1] Dynamic allocation spec - https://review.openstack.org/#/c/275726/
.. [2] Driver documentation - http://docs.openstack.org/developer/ironic/drivers/oneview.html
.. [3] HPE OneView - https://www.hpe.com/us/en/integrated-systems/software.html
.. [4] OpenStack RC - http://docs.openstack.org/user-guide/common/cli_set_environment_variables_using_openstack_rc.html
.. [5] Networking OneView ML2 Driver - https://github.com/HewlettPackard/ironic-driver-oneview/tree/master/networking-oneview
