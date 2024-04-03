FROM python:3-slim

# update
RUN apt-get update \
    && pip install --upgrade pip


RUN apt install -y git

# network tools
RUN apt install -y curl

# text editors
RUN apt install -y vim

# non-root user
ARG USERNAME=app
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME
USER $USERNAME

WORKDIR /home/$USERNAME

# .dotfiles
COPY .config/.bashrc /home/$USERNAME/.bashrc

# setup
COPY requirements.txt .
RUN pip install -r ./requirements.txt

ENTRYPOINT ["/bin/bash"]