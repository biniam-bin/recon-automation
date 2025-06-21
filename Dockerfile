FROM golang:1.21 as gobuilder

# Install Go tools one by one with proper error handling
RUN set -eux; \
    go install github.com/OWASP/Amass/v3/...@latest; \
    go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest; \
    go install github.com/tomnomnom/assetfinder@latest; \
    go install github.com/Findomain/Findomain@latest; \
    go install github.com/lc/gau/v2/cmd/gau@latest; \
    go install github.com/tomnomnom/waybackurls@latest; \
    go install github.com/projectdiscovery/katana/cmd/katana@latest; \
    go install github.com/jaeles-project/gospider@latest

FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nmap \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy Go tools from builder
COPY --from=gobuilder /go/bin /usr/local/bin

# Install Python requirements
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

CMD ["python", "main.py"]
