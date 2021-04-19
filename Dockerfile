FROM nginx:1.19.10

RUN apt update && \
    apt install -y python3 python3-pip procps neovim less

COPY requirements.txt /app/

RUN pip3 install -r /app/requirements.txt

VOLUME /ngm2

ENV ACME_MOCK=True

ENTRYPOINT ["/bin/bash"]