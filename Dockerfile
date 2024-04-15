FROM gradle:8-jdk21 as base

ARG DEBIAN_FRONTEND=noninteractive
ARG USERNAME=otel
ARG USER_UID=1001
ARG USER_GID=$USER_UID
ARG DOCKER_REPOSITORY_VERSION=bookworm

RUN apt-get -qq update && apt-get -qq upgrade

RUN apt-get -qq install ca-certificates curl sudo bash git
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
RUN chmod a+r /etc/apt/keyrings/docker.asc

RUN echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo ${DOCKER_REPOSITORY_VERSION}) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

RUN apt-get -qq update

RUN apt-get -qq install \
    python3 \
    python3-pip \
    python-is-python3 \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

RUN pip3 install \
    requests \
    flask \
    Faker \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-exporter-prometheus \
    opentelemetry-exporter-otlp \
    psutil

WORKDIR /workspace

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

RUN usermod -aG docker $USERNAME

USER $USERNAME

EXPOSE 5000

ENTRYPOINT ["/bin/bash"]