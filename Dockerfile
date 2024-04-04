FROM gradle:8.7.0-jdk21 as base

ARG DEBIAN_FRONTEND=noninteractive
ARG USERNAME=otel
ARG USER_UID=1001
ARG USER_GID=$USER_UID

RUN apt-get -qq update && apt-get -qq upgrade

RUN apt-get -qq install \
    sudo \
    bash \
    git \
    python3 \
    python3-pip \
    docker \
    docker-compose

RUN pip3 install \
    requests \
    flask \
    Faker \
    opentelemetry-api \
    opentelemetry-sdk

WORKDIR /workspace

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

RUN usermod -aG docker $USERNAME

USER $USERNAME

EXPOSE 5000

ENTRYPOINT ["/bin/bash"]