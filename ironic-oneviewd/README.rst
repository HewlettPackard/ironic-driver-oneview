===============
Ironic-OneViewd
===============

Overview
========

The ironic-oneviewd is a ``python daemon`` of the OneView Driver for Ironic.
It handles nodes in *enroll* and *manageable* provision states, preparing them
to become *available*. In order to be moved from *enroll* to *available*, a
``Server Profile`` must be applied to the ``Server Hardware`` represented by a
node according to its ``Server Profile Template``.

This daemon monitors Ironic nodes and applies a ``Server Profile`` to such
``Server Hardware``. The node then goes from an *enroll* to a *manageable*
state, and right after to an *available* state.

.. note::
   This tool works with OpenStack Identity API v2.0 and v3.

For more information on OneView entities, see [1]_.

Tested platforms
================

The OneView appliance used for testing was the OneView 2.0.

The Enclosure used for testing was the ``BladeSystem c7000 Enclosure G2``.

The daemon should work on HP Proliant Gen8 and Gen9 Servers supported by
OneView 2.0 and above, or any hardware whose network can be managed by
OneView's ServerProfile. It has been tested with the following servers:

  - Proliant BL460c Gen8
  - Proliant BL465c Gen8
  - Proliant DL360 Gen9 (starting with python-oneviewclient 2.1.0)

Notice here that to the daemon work correctly with Gen8 and Gen9 DL servers
in general, the hardware also needs to run version 4.2.3 of iLO, with Redfish.

Installation
============

To install the ironic-oneviewd service, use the following command::

    pip install ironic-oneviewd

Configuring the service
=======================

The ironic-oneviewd uses a configuration file to get Ironic and OneView
credentials and addresses. By default, ironic-oneviewd tries to use the
configuration file::

    /etc/ironic-oneviewd/ironic-oneviewd.conf

A sample configuration file is found within the same directory and may be used
as base for the configuration file. In order to do so, the sample file needs to
be renamed to ``ironic-oneviewd.conf``. The sample configuration file is found
as::

    /etc/ironic-oneviewd/ironic-oneviewd.conf.sample

Usage
=====

If your configuration file is in the default directory */etc/ironic-oneviewd/ironic-oneviewd.conf*,
the service will automatically use this conf. In this case, to run
ironic-oneviewd, do::

    ironic-oneviewd

If you chose to place this file in a different location, you should pass it
when starting the service::

    ironic-oneviewd --config-file <path to your configuration file>

or::

    ironic-oneviewd -c <path to your configuration file>

Note that, in order to run this daemon, you only have to pass the
configuration file previously created containing the required credentials
and addresses.

When ironic-oneviewd is executed, the default output is the standard output.
Otherwise, if the --log-file parameter is passed at the execution, the logs
will be appended to the logfile path and not shown on the standard output. You
should pass it when starting the service::

  ironic-oneviewd --log-file <path to your logging file>

References
==========
.. [1] HP OneView - http://www8.hp.com/us/en/business-solutions/converged-systems/oneview.html
