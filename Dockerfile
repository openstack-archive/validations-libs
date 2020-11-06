FROM centos:latest

RUN dnf install -y git python3-pip gcc python3-devel

RUN git clone https://opendev.org/openstack/validations-libs /root/validations-libs
RUN git clone https://opendev.org/openstack/validations-common /root/validations-common

RUN cd /root/validations-libs && \
    pip3 install -r requirements.txt && \
    python3 setup.py install

RUN cd /root/validations-common && \
    pip3 install -r requirements.txt && \
    python3 setup.py install

RUN ln -s /usr/local/share/ansible  /usr/share/ansible

RUN mkdir -p /var/log/validations
