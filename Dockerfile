# Stage 1: Build Go tools
FROM golang:1.21 as gobuilder

# Install basic dependencies for Go tools
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install each tool separately with error handling
RUN go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
RUN go install github.com/tomnomnom/assetfinder@latest
RUN go install github.com/lc/gau/v2/cmd/gau@latest
RUN go install github.com/tomnomnom/waybackurls@latest
RUN go install github.com/projectdiscovery/katana/cmd/katana@latest
RUN go install github.com/jaeles-project/gospider@latest

# Special handling for Amass (which often causes issues)
RUN git clone https://github.com/OWASP/Amass.git \
    && cd Amass \
    && go install ./...

# Special handling for Findomain (Rust tool)
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
