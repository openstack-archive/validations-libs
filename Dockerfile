FROM redhat/ubi9:latest

LABEL name="VF development container file"
LABEL version="1.1"
LABEL description="Provides environment for development of new validations."

RUN dnf install -y git python3-pip gcc python3-devel jq

# Copy contents of the local validations-libs repo with all of our changes
COPY . /root/validations-libs
# validations-common repo is cloned
RUN git clone https://opendev.org/openstack/validations-common /root/validations-common

# Install wheel, validations-libs, validations-common, pytest and all dependencies
RUN python3 -m pip install wheel &&\
    python3 -m pip install /root/validations-libs &&\
    python3 -m pip install -r /root/validations-libs/test-requirements.txt &&\
    python3 -m pip install pytest &&\
    python3 -m pip install /root/validations-common

# Setting up the default directory structure for both ansible,
# and the VF
RUN ln -s /usr/local/share/ansible  /usr/share/ansible &&\
    mkdir -p /var/log/validations
# Simplified ansible inventory is created, containing only localhost,
# and defining the connection as local.
RUN mkdir -p /etc/ansible && \
    echo "localhost ansible_connection=local" > /etc/ansible/hosts
