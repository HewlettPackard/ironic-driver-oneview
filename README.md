# HPE OneView drivers and tools for OpenStack

While virtualization is the use case for the average end user, it does not apply for all types of workloads. Some applications cannot be executed in virtual machines due to performance constraints (e.g. database hosting), hardware constraints (i.e. depending on hardware that cannot be virtualized). This can also occur due to security and isolation reasons, or even deploying cloud nodes for provisioning virtual machines or containers (new use case being adopted).

HPE OneView is an infrastructure management tool that allows IT teams to deploy, monitor, and manage their HPE data center infrastructure. It is also the foundation of the HPE drive to Composable Infrastructure. HPE OneView is built with software intelligence, and provides a unified API that allows automation of the infrastructure deployment and updates, and managing facilities. For more information about HPE OneView, see [here](https://www.hpe.com/us/en/integrated-systems/software.html).

In order to bring bare metal to Cloud with HPE OneView, we have developed integrations with OpenStack Ironic and Neutron. With our solution, we can provision HPE OneView bare metal servers using end user tenant networks in OpenStack in the same way as virtual machines.

In the OpenStack ecosystem, the component responsible for provisioning bare metal machines is named Ironic. In the most basic scenario, Ironic achieves this goal by communicating with the other three main OpenStack components:
* "Nova" - compute service
* "Glance" - image service
* "Neutron" - networking service

The integration of management systems, such as HPE OneView, is made possible in Ironic through the implementation of drivers. This way, OneView drivers implement well defined interfaces in Ironic, and uses OneView RESTful API to execute actions that will be performed in the physical machines. For example,  powering machine on/off and rebooting; changing boot device; and when creating and removing a *Server Profile*.

# Projects

## Bare metal Drivers

The HPE OneView drivers for OpenStack Ironic, already incorporated in the OpenStack mainstream codebase, allow cloud providers to use their OneView managed hardware as bare metal instances. For more information, please refer to [OpenStack Ironic documentation for OneView drivers]( https://docs.openstack.org/ironic/latest/admin/drivers/oneview.html).

The OneView Server Hardware is enrolled as OpenStack Ironic nodes, based on a given Server Profile Template previously created. The OneView drivers, unlike others, can help cloud administrators manage firmware/driver dependencies between the hardware they provision, and the operating system images they use. The drivers work in a shared allocation fashion with other HPE OneView users, which means nodes enrolled to OpenStack Ironic are not statically allocated at OneView. The OneView drivers’ periodic tasks take care of marking nodes claimed by OneView users as unavailable to OpenStack users and vice versa.

## Ironic OneView CLI

A tool with custom interactive commands that interfaces with OpenStack CLI. Ironic OneView CLI, helps administrators create Ironic nodes, exposing HPE OneView compute nodes to the bare metal service, and Nova flavors. Enables mapping different Server Hardware configuration (memory, disk, and vcpus to match the bare metal instance), also taking takes into consideration the Server Hardware Type and Enclosure Group. Moreover, it provides commands to create Ironic Ports mapping for Server Hardware NICs. Please refer to ironic-oneview-cli. For more information, Please refer to [ironic-oneview-cli](https://github.com/HewlettPackard/ironic-oneview-cli).

## Ironic OneView Daemon

A tool that helps administrators manage their compute nodes. Automating the process of Server Hardware enrollment, the transition of states according to the OpenStack ironic state machine, and making the nodes available for deployment. For more information, please refer to [ironic-oneviewd](https://github.com/HewlettPackard/ironic-oneviewd).

## Network ML2 Driver

The HPE OneView ML2 driver allows cloud providers to manage their networking hardware. Reflecting networking operations performed on OpenStack Neutron to OneView being responsible for automatically creating and deleting networks, configuring Logical Interconnect Groups, its associated Logical Interconnects and UpLink sets, and updating connections on the Server Profile applied to Server Hardware. We have been preparing the HPE OneView Mechanism Driver to be moved from GitHub to OpenStack codebase, meanwhile refer to [networking-oneview](networking-oneview).

# Contributing

You know the drill. Fork it, branch it, change it, commit it, and pull-request it. We are passionate about improving this project, and glad to accept help to make it better.

# Feature Requests

If you have a need that is not being met by the current implementation, please let us know (via a new issue). Feedback is crucial for us to deliver a useful product. Do not assume that we have already thought of everything, because we assure you, that is not the case.

# License

All projects are licensed under the Apache License 2.0 license.
