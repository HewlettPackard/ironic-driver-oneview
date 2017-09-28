# HPE OneView drivers and tools for OpenStack

While virtualization is the use case for the average end user, it does not apply for all types of workloads. Some applications cannot be executed in virtual machines due to performance constraints (e.g. database hosting), hardware constraints (i.e. depending on hardware that cannot be virtualized), also due to security and isolation reasons, or even deploying cloud nodes for provisioning virtual machines or containers (new use case being adopted). In order to bring bare metal to Cloud with HPE OneView, we have developed integrations with OpenStack Ironic and Neutron. With our solution, we can provision HPE OneView bare metal servers using end user tenant networks in OpenStack in the same way as virtual machines.

OneView’s Server Hardware are enrolled as OpenStack Ironic nodes, based on a given Server Profile Template previously created. Thus, the OneView drivers, unlike others, can help cloud administrators manage firmware/driver dependencies between the hardware they provision and the operating system images they make use of. The drivers work in a shared allocation fashion with other HPE OneView users, which means nodes enrolled to OpenStack Ironic are not statically allocated at OneView. OneView drivers’ periodic tasks take care of marking nodes claimed by OneView users as unavailable to OpenStack users and vice versa.

# Projects

## Bare metal Drivers

The HPE OneView drivers for OpenStack Ironic, already incorporated in the OpenStack mainstream codebase, allow cloud providers to use their OneView managed hardware as bare metal instances. Please refer to [OpenStack Ironic documentation for OneView drivers]( https://docs.openstack.org/ironic/latest/admin/drivers/oneview.html)

## Ironic OneView CLI

Tool with custom interactive commands, that interfaces with OpenStack CLI, helping administrators create Ironic nodes, exposing their HPE OneView compute nodes to the bare metal service, and Nova flavors, mapping different Server Hardware configuration (memory, disk and vcpus to match the bare metal instance), taking into consideration not only hardware configuration but also Server Hardware Type and Enclosure Group. Moreover, it provides commands to create Ironic Ports mapping Server Hardware NICs.. Please refer to [ironic-oneview-cli](ironic-oneview-cli).

## Ironic OneView Daemon

Tool that helps administrators to manage their compute nodes, automating the process of Server Hardware enrollment - the transition of states according to OpenStack ironic state machine, and also making the nodes available for deployment. Please refer to [ironic-oneviewd](ironic-oneviewd).

## Network ML2 Driver

The HPE OneView ML2 driver allows cloud providers to manage their networking hardware reflecting networking operations performed on OpenStack Neutron to OneView, being responsible for automatically creating and deleting networks, configuring Logical Interconnect Groups, and its associated Logical Interconnects and UpLink sets; and updating connections on Server Profile applied to a given Server Hardware. We have been preparing the HPE OneView Mechanism Driver to be moved from GitHub to OpenStack codebase, meanwhile refer to [networking-oneview](networking-oneview).

# Contributing

You know the drill. Fork it, branch it, change it, commit it, and pull-request it. We are passionate about improving this project, and glad to accept help to make it better.

# Feature Requests 

If you have a need not being met by the current implementation, please let us know (via a new issue). This feedback is crucial for us to deliver a useful product. Do not assume that we have already thought of everything, because we assure you that is not the case.

# License

All projects are licensed under the Apache License 2.0 license.
