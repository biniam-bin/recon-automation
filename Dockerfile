FROM kalilinux/kali-rolling

RUN apt update && apt install -y golang git curl python3-pip

RUN go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest

ENV PATH=$PATH:/root/go/bin

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["bash", "recon.sh"]
