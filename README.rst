================
validations-libs
================

.. image:: https://governance.openstack.org/tc/badges/validations-libs.svg
    :target: https://governance.openstack.org/tc/reference/tags/index.html

A collection of python libraries for the Validation Framework

The validations will help detect issues early in the deployment process and
prevent field engineers from wasting time on misconfiguration or hardware
issues in their environments.

* Free software: Apache_license_
* Documentation: https://docs.openstack.org/validations-libs/latest/
* Source: https://opendev.org/openstack/validations-libs
* Bugs - Upstream: https://bugs.launchpad.net/tripleo/+bugs?field.tag=validations
* Bugs - Downstream: https://bugzilla.redhat.com/buglist.cgi?component=validations-libs&product=Red%20Hat%20OpenStack

.. * Release notes: https://docs.openstack.org/releasenotes/validations-libs/  We don't have any yet.


Development Environment Setup
=============================

Vagrantfiles for CentOS and Ubuntu have been provided for convenience; simply
copy one into your desired location and rename to ``Vagrantfile``, then run::

     vagrant up

Once complete you will have a clean development environment
ready to go for working with Validation Framework.

podman Quickstart
=================

A Dockerfile is provided at the root of the Validations Library project in
order to quickly set and hack the Validation Framework, on a equivalent of a single machine.
Build the container from the Dockerfile by running::

    podman build -t "vf:dockerfile" .

From the validations-libs repo directory.

.. note::
    More complex images are available in the dockerfiles directory
    and require explicit specification of both build context and the Dockerfile.

Since the podman build uses code sourced from the buildah project to build container images.
It is also possible to build an image using::

    buildah bud -t "vf:dockerfile" .

Then you can run the container and start to run some builtin Validations::

    podman run -ti vf:dockerfile /bin/bash

Then run validations::

    validation.py run --validation check-ftype,512e --inventory /etc/ansible/hosts


Skip list
=========

You can provide a file with a list of Validations to skip via the run command::

    validation.py run --validation check-ftype,512e --inventory /etc/ansible/hosts --skiplist my-skip-list.yaml

This file should be formed as::

    validation-name:
      hosts: targeted_hostname
      reason: reason to ignore the file
      lp: bug number

The framework will skip the validation against the ``hosts`` key.
In order to skip the validation on every hosts, you can set ``all`` value such
as::

    hosts: all

If no hosts key is provided for a given validation, it will be considered as ``hosts: all``.

.. note::
    The ``reason`` and ``lp`` key are for tracking and documentation purposes,
    the framework won't use those keys.

Community Validations
=====================

Community Validations enable a sysadmin to create and execute validations unique
to their environment through the ``validation`` CLI.

The Community Validations will be created and stored in an unique, standardized
and known place, called ``'community-validations/'``, in the home directory of the
non-root user which is running the CLI.

.. note::
   The Community Validations are enabled by default. If you want to disable
   them, please set ``[DEFAULT].enable_community_validations`` to ``False`` in the
   validation configuration file located by default in ``/etc/validation.cfg``

The first level of the mandatory structure will be the following (assuming the
operator uses the ``pennywise`` user):

.. code-block:: console

    /home/pennywise/community-validations
    ├── library
    ├── lookup_plugins
    ├── playbooks
    └── roles

.. note::
   The ``community-validations`` directory and its sub directories will be
   created at the first CLI use and will be checked everytime a new community
   validation will be created through the CLI.

How To Create A New Community Validation
----------------------------------------

.. code-block:: console

   [pennywise@localhost]$ validation init my-new-validation
   Validation config file found: /etc/validation.cfg
   New role created successfully in /home/pennywise/community-validations/roles/my_new_validation
   New playbook created successfully in /home/pennywise/community-validations/playbooks/my-new-validation.yaml

The ``community-validations/`` directory should have been created in the home
directory of the ``pennywise`` user.

.. code-block:: console

    [pennywise@localhost ~]$ cd && tree community-validations/
    community-validations/
    ├── library
    ├── lookup_plugins
    ├── playbooks
    │   └── my-new-validation.yaml
    └── roles
        └── my_new_validation
            ├── defaults
            │   └── main.yml
            ├── files
            ├── handlers
            │   └── main.yml
            ├── meta
            │   └── main.yml
            ├── README.md
            ├── tasks
            │   └── main.yml
            ├── templates
            ├── tests
            │   ├── inventory
            │   └── test.yml
            └── vars
                └── main.yml

    13 directories, 9 files

Your new community validation should also be available when listing all the
validations available on your system.

.. code-block:: console

    [pennywise@localhost ~]$ validation list
    Validation config file found: /etc/validation.cfg
    +-------------------------------+--------------------------------+--------------------------------+-----------------------------------+---------------+
    | ID                            | Name                           | Groups                         | Categories                        | Products      |
    +-------------------------------+--------------------------------+--------------------------------+-----------------------------------+---------------+
    | 512e                          | Advanced Format 512e Support   | ['prep', 'pre-deployment']     | ['storage', 'disk', 'system']     | ['common']    |
    | check-cpu                     | Verify if the server fits the  | ['prep', 'backup-and-restore', | ['system', 'cpu', 'core', 'os']   | ['common']    |
    |                               | CPU core requirements          | 'pre-introspection']           |                                   |               |
    | check-disk-space-pre-upgrade  | Verify server fits the disk    | ['pre-upgrade']                | ['system', 'disk', 'upgrade']     | ['common']    |
    |                               | space requirements to perform  |                                |                                   |               |
    |                               | an upgrade                     |                                |                                   |               |
    | check-disk-space              | Verify server fits the disk    | ['prep', 'pre-introspection']  | ['system', 'disk', 'upgrade']     | ['common']    |
    |                               | space requirements             |                                |                                   |               |
    | check-ftype                   | XFS ftype check                | ['pre-upgrade']                | ['storage', 'xfs', 'disk']        | ['common']    |
    | check-latest-packages-version | Check if latest version of     | ['pre-upgrade']                | ['packages', 'rpm', 'upgrade']    | ['common']    |
    |                               | packages is installed          |                                |                                   |               |
    | check-ram                     | Verify the server fits the RAM | ['prep', 'pre-introspection',  | ['system', 'ram', 'memory', 'os'] | ['common']    |
    |                               | requirements                   | 'pre-upgrade']                 |                                   |               |
    | check-selinux-mode            | SELinux Enforcing Mode Check   | ['prep', 'pre-introspection']  | ['security', 'selinux']           | ['common']    |
    | dns                           | Verify DNS                     | ['pre-deployment']             | ['networking', 'dns']             | ['common']    |
    | no-op                         | NO-OP validation               | ['no-op']                      | ['noop', 'dummy', 'test']         | ['common']    |
    | ntp                           | Verify all deployed servers    | ['post-deployment']            | ['networking', 'time', 'os']      | ['common']    |
    |                               | have their clock synchronised  |                                |                                   |               |
    | service-status                | Ensure services state          | ['prep', 'backup-and-restore', | ['systemd', 'container',          | ['common']    |
    |                               |                                | 'pre-deployment', 'pre-        | 'docker', 'podman']               |               |
    |                               |                                | upgrade', 'post-deployment',   |                                   |               |
    |                               |                                | 'post-upgrade']                |                                   |               |
    | validate-selinux              | validate-selinux               | ['backup-and-restore', 'pre-   | ['security', 'selinux', 'audit']  | ['common']    |
    |                               |                                | deployment', 'post-            |                                   |               |
    |                               |                                | deployment', 'pre-upgrade',    |                                   |               |
    |                               |                                | 'post-upgrade']                |                                   |               |
    | my-new-validation             | Brief and general description  | ['prep', 'pre-deployment']     | ['networking', 'security', 'os',  | ['community'] |
    |                               | of the validation              |                                | 'system']                         |               |
    +-------------------------------+--------------------------------+--------------------------------+-----------------------------------+---------------+

To get only the list of your community validations, you can filter by products:

.. code-block:: console

   [pennywise@localhost]$ validation list --product community
   Validation config file found: /etc/validation.cfg
   +-------------------+------------------------------------------+----------------------------+------------------------------------------+---------------+
   | ID                | Name                                     | Groups                     | Categories                               | Products      |
   +-------------------+------------------------------------------+----------------------------+------------------------------------------+---------------+
   | my-new-validation | Brief and general description of the     | ['prep', 'pre-deployment'] | ['networking', 'security', 'os',         | ['community'] |
   |                   | validation                               |                            | 'system']                                |               |
   +-------------------+------------------------------------------+----------------------------+------------------------------------------+---------------+

How To Develop Your New Community Validation
--------------------------------------------

As you can see above, the ``validation init`` CLI sub command has generated a
new Ansible role by using `ansible-galaxy
<https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html>`_
and a new Ansible playbook in the ``community-validations/`` directory.

.. warning::
   The community validations won't be supported at all. We won't be responsible
   as well for potential use of malignant code in their validations.  Only the
   creation of a community validation structure through the new Validation CLI sub
   command will be supported.

You are now able to implement your own validation by editing the generated
playbook and adding your ansible tasks in the associated role.

For people not familiar with how to write a validation, get started with this
`documentation <https://docs.openstack.org/tripleo-validations/latest/contributing/developer_guide.html#writing-validations>`_.

.. _Apache_license: http://www.apache.org/licenses/LICENSE-2.0
