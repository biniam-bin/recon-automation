FROM python:3.9-slim

# Install system dependencies with clean up
RUN apt-get update && apt-get install -y \
    nmap \
    git \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Go with proper environment setup
ENV GO_VERSION=1.21.0
RUN wget -q https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz -P /tmp && \
    tar -C /usr/local -xzf /tmp/go${GO_VERSION}.linux-amd64.tar.gz && \
    rm /tmp/go${GO_VERSION}.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin
ENV GOPATH=/go
ENV PATH=$PATH:$GOPATH/bin

# Create directory structure for Go
RUN mkdir -p $GOPATH/src $GOPATH/bin $GOPATH/pkg && \
    chmod -R 777 $GOPATH

# Install Go tools one by one with error handling
RUN go install github.com/OWASP/Amass/v3/...@latest && \
    go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install github.com/tomnomnom/assetfinder@latest && \
    go install github.com/Findomain/Findomain@latest && \
    go install github.com/lc/gau/v2/cmd/gau@latest && \
    go install github.com/tomnomnom/waybackurls@latest && \
    go install github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install github.com/jaeles-project/gospider@latest && \
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest

# Verify installations
RUN subfinder -version && \
    amass -version && \
    httpx -version

# Install Python requirements
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

CMD ["python", "main.py"]
