FROM nginx:1.19.10

RUN apt update && \
    apt install -y python3 procps neovim