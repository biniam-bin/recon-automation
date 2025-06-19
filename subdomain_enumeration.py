import os
import subprocess
from database import ReconDatabase
from slack_notifier import SlackNotifier
from utils import ensure_temp_dir, clean_domain

def run_amass(domain, output_file):
    cmd = f"amass enum -passive -d {domain} -o {output_file}"
    subprocess.run(cmd, shell=True, check=True)

def run_subfinder(domain, output_file):
    cmd = f"subfinder -d {domain} -o {output_file}"
    subprocess.run(cmd, shell=True, check=True)

def run_assetfinder(domain, output_file):
    cmd = f"assetfinder -subs-only {domain} > {output_file}"
    subprocess.run(cmd, shell=True, check=True)

def run_findomain(domain, output_file):
    cmd = f"findomain -t {domain} -u {output_file}"
    subprocess.run(cmd, shell=True, check=True)

def run_crtsh(domain, output_file):
    import requests
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        subdomains = set()
        for item in data:
            name = item['name_value'].lower()
            if name.startswith('*.'):
                name = name[2:]
            if domain in name:
                subdomains.add(name)
        with open(output_file, 'w') as f:
            f.write('\n'.join(subdomains))

def enumerate_subdomains(domain):
    ensure_temp_dir()
    domain = clean_domain(domain)
    db = ReconDatabase()
    domain_id = db.add_domain(domain)
    
    tools = {
        'amass': run_amass,
        'subfinder': run_subfinder,
        'assetfinder': run_assetfinder,
        'findomain': run_findomain,
        'crtsh': run_crtsh
    }
    
    all_subdomains = set()
    
    for tool_name, tool_func in tools.items():
        try:
            output_file = f"/tmp/recon/{domain}_{tool_name}_subdomains.txt"
            tool_func(domain, output_file)
            
            with open(output_file, 'r') as f:
                subdomains = set(line.strip() for line in f if line.strip())
                all_subdomains.update(subdomains)
                db.add_subdomains(domain_id, subdomains, tool_name)
            
            SlackNotifier.send_message(
                f"{tool_name.capitalize()} subdomain enumeration for {domain} found {len(subdomains)} subdomains"
            )
        except Exception as e:
            print(f"Error running {tool_name}: {e}")
            SlackNotifier.send_message(
                f":warning: Failed to run {tool_name} for {domain}: {str(e)}"
            )
    
    # Store all unique subdomains
    db.add_subdomains(domain_id, all_subdomains, 'combined')
    
    SlackNotifier.send_message(
        f"Subdomain enumeration for {domain} is done and found {len(all_subdomains)} subdomains"
    )
    
    db.close()
    return list(all_subdomains)