# Stage 1: Build Go tools
FROM golang:1.21 as gobuilder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install tools with individual error handling
# 1. Subfinder (with explicit version)
RUN git clone https://github.com/projectdiscovery/subfinder.git \
    && cd subfinder/v2/cmd/subfinder \
    && go build -o /go/bin/subfinder . \
    && cd / && rm -rf /go/pkg/mod /go/src

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

# 7. Amass (built from source)
RUN git clone https://github.com/OWASP/Amass.git \
    && cd Amass \
    && go install ./...

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
