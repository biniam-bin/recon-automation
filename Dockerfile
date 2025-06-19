FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nmap \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Go (required for some tools)
ENV GO_VERSION=1.20.4
RUN apt-get update && apt-get install -y wget && \
    wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz && \
    rm go${GO_VERSION}.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin

# Install recon tools
RUN go install github.com/OWASP/Amass/v3/...@latest && \
    go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install github.com/tomnomnom/assetfinder@latest && \
    go install github.com/Findomain/Findomain@latest && \
    go install github.com/lc/gau/v2/cmd/gau@latest && \
    go install github.com/tomnomnom/waybackurls@latest && \
    go install github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install github.com/jaeles-project/gospider@latest

# Install Python requirements
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

CMD ["python", "main.py"]