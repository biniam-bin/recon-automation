# Stage 1: Build Go tools
FROM golang:1.21 as gobuilder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install tools using pre-built binaries where needed
# 1. Subfinder (using pre-built binary)
RUN wget https://github.com/projectdiscovery/subfinder/releases/download/v2.6.3/subfinder_2.6.3_linux_amd64.zip \
    && unzip subfinder_2.6.3_linux_amd64.zip \
    && mv subfinder /go/bin/ \
    && rm subfinder_2.6.3_linux_amd64.zip

# 2. Assetfinder
RUN go install github.com/tomnomnom/assetfinder@latest

# 3. GAU
RUN go install github.com/lc/gau/v2/cmd/gau@latest

# 4. Waybackurls
RUN go install github.com/tomnomnom/waybackurls@latest

# 5. Katana
RUN go install github.com/projectdiscovery/katana/cmd/katana@latest

# 6. Gospider
RUN go install github.com/jaeles-project/gospider@latest

# 7. Amass (using pre-built binary)
RUN wget https://github.com/OWASP/Amass/releases/download/v4.2.0/amass_linux_amd64.zip \
    && unzip amass_linux_amd64.zip \
    && mv amass_linux_amd64/amass /go/bin/ \
    && rm -rf amass_linux_amd64*

# Stage 2: Build Findomain (Rust tool)
FROM rust:1.70 as findomainbuilder
RUN cargo install --git https://github.com/Findomain/Findomain.git

# Final stage
FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    nmap \
    && rm -rf /var/lib/apt/lists/*

# Copy Go tools from builder
COPY --from=gobuilder /go/bin /usr/local/bin

# Copy Findomain from Rust builder
COPY --from=findomainbuilder /usr/local/cargo/bin/findomain /usr/local/bin/

# Install Python requirements
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

CMD ["python", "main.py"]
