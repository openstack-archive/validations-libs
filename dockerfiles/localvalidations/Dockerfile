FROM centos:latest

LABEL name="VF develoment dockerfile"
LABEL version="0.3"
LABEL description="Provides environment for development of new validations."

RUN dnf install -y git python3-pip gcc python3-devel jq

#We copy contents of the local validations-libs repo with all of our changes
COPY . /root/validations-libs
#validations-common repo is cloned
RUN git clone https://opendev.org/openstack/validations-common /root/validations-common

RUN python3 -m pip install cryptography==3.3

RUN cd /root/validations-libs && \
    python3 -m pip install . && \
    python3 -m pip install -r test-requirements.txt

RUN cd /root/validations-common && \
    python3 -m pip install . && \
    python3 -m pip install -r test-requirements.txt

#Setting up the default directory structure for both ansible,
#and the VF
RUN ln -s /usr/local/share/ansible  /usr/share/ansible && \
    mkdir -p /var/log/validations
#Simplified ansible inventory is created, containing only localhost,
#and defining the connection as local.
RUN mkdir -p /etc/ansible && \
    echo "localhost ansible_connection=local" > /etc/ansible/hosts
