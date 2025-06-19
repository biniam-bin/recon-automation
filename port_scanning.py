import subprocess
import re
import json
from database import ReconDatabase
from slack_notifier import SlackNotifier
from utils import ensure_temp_dir

def run_nmap(subdomain, output_file):
    # Fast scan with service detection
    cmd = f"nmap -T4 -Pn -sS -sV --top-ports 1000 -oN {output_file} {subdomain}"
    subprocess.run(cmd, shell=True, check=True)

def parse_nmap_output(output_file):
    ports = []
    with open(output_file, 'r') as f:
        content = f.read()
        
        # Find all port lines
        port_lines = re.findall(r'^(\d+)/(tcp|udp)\s+open\s+(\S+)(?:\s+(.*))?', content, re.MULTILINE)
        
        for port, protocol, service, version in port_lines:
            ports.append({
                'port': int(port),
                'protocol': protocol,
                'service': service,
                'version': version if version else None
            })
    
    return ports

def run_httpx(subdomains_file, output_file):
    cmd = f"httpx -l {subdomains_file} -status-code -title -tech-detect -json -o {output_file}"
    subprocess.run(cmd, shell=True, check=True)

def parse_httpx_output(output_file):
    live_subdomains = []
    with open(output_file, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                live_subdomains.append(data['url'])
            except json.JSONDecodeError:
                continue
    return live_subdomains

def scan_ports_and_identify_live(domain_id, subdomains):
    ensure_temp_dir()
    db = ReconDatabase()
    
    # First, identify live subdomains with httpx
    subdomains_file = f"/tmp/recon/{domain_id}_subdomains.txt"
    with open(subdomains_file, 'w') as f:
        f.write('\n'.join([sub[1] for sub in subdomains]))
    
    httpx_output = f"/tmp/recon/{domain_id}_httpx.json"
    try:
        run_httpx(subdomains_file, httpx_output)
        live_subdomains = parse_httpx_output(httpx_output)
        
        SlackNotifier.send_message(
            f"HTTPX scan for domain ID {domain_id} found {len(live_subdomains)} live subdomains"
        )
    except Exception as e:
        print(f"Error running httpx: {e}")
        SlackNotifier.send_message(
            f":warning: Failed to run httpx for domain ID {domain_id}: {str(e)}"
        )
        live_subdomains = []
    
    # Then scan ports for each subdomain
    total_ports = 0
    
    for subdomain_id, subdomain in subdomains:
        if not any(subdomain in live_sub for live_sub in live_subdomains):
            continue
        
        nmap_output = f"/tmp/recon/{domain_id}_{subdomain_id}_nmap.txt"
        try:
            run_nmap(subdomain, nmap_output)
            ports = parse_nmap_output(nmap_output)
            db.add_ports(subdomain_id, ports)
            total_ports += len(ports)
            
            SlackNotifier.send_message(
                f"Nmap scan for {subdomain} found {len(ports)} open ports"
            )
        except Exception as e:
            print(f"Error running nmap for {subdomain}: {e}")
            SlackNotifier.send_message(
                f":warning: Failed to run nmap for {subdomain}: {str(e)}"
            )
    
    SlackNotifier.send_message(
        f"Port scanning for domain ID {domain_id} is done. Found {total_ports} open ports across all subdomains"
    )
    
    db.close()
    return total_ports