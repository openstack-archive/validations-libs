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

.. _Apache_license: http://www.apache.org/licenses/LICENSE-2.0
