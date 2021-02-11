FROM centos:latest

LABEL name="VF develoment dockerfile"
LABEL version="0.2"
LABEL description="Provides environment for development of new validations."

RUN dnf install -y git python3-pip gcc python3-devel jq

COPY . /root/validations-libs
RUN git clone https://opendev.org/openstack/validations-common /root/validations-common

RUN python3 -m pip install cryptography==3.3

RUN cd /root/validations-libs && \
    python3 -m pip install . && \
    python3 -m pip install -r test-requirements.txt

RUN cd /root/validations-common && \
    python3 -m pip install . && \
    python3 -m pip install -r test-requirements.txt

RUN ln -s /usr/local/share/ansible  /usr/share/ansible
RUN mkdir /etc/ansible && \
    echo "localhost ansible_connection=local" > /etc/ansible/hosts
RUN mkdir -p /var/log/validations
