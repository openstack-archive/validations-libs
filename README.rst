================
validations-libs
================

A collection of python libraries for the Validation Framework

Development Environment Setup
=============================

Vagrantfiles for CentOS and Ubuntu have been provided for convenience; simply
copy one into your desired location and rename to ``Vagrantfile``, then run::

     vagrant up

Once complete you will have a clean development environment
ready to go for working with Validation Framework.

Docker Quickstart
=================

A Dockerfile is provided at the root of the Validations Library project in
order to quickly set and hack the Validation Framework, on a equivalent of a single machine.
Build the container from the Dockerfile by running::

    docker build -t "vf:dockerfile" .

From the validations-libs repo directory.

.. note::
    More complex images are available in the dockerfiles directory
    and require explicit specification of both build context and the Dockerfile.

Then you can run the container and start to run some builtin Validations::

    docker run -ti vf:dockerfile /bin/bash

Then run validations::

    validation.py run --validation check-ftype,512e --inventory /etc/ansible/hosts
