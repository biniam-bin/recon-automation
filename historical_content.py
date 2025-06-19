import subprocess
import json
from database import ReconDatabase
from slack_notifier import SlackNotifier
from utils import ensure_temp_dir

def run_wayback(domain, output_file):
    cmd = f"waybackurls {domain} > {output_file}"
    subprocess.run(cmd, shell=True, check=True)

def run_gau(domain, output_file):
    cmd = f"gau {domain} > {output_file}"
    subprocess.run(cmd, shell=True, check=True)

def run_waymore(domain, output_file):
    # Note: waymore is a Python tool, might need different installation
    cmd = f"waymore -i {domain} -mode U -o {output_file}"
    subprocess.run(cmd, shell=True, check=True)

def discover_historical_content(domain_id, domain):
    ensure_temp_dir()
    db = ReconDatabase()
    
    tools = {
        'wayback': run_wayback,
        'gau': run_gau,
        'waymore': run_waymore
    }
    
    all_urls = set()
    
    for tool_name, tool_func in tools.items():
        try:
            output_file = f"/tmp/recon/{domain_id}_{tool_name}_urls.txt"
            tool_func(domain, output_file)
            
            with open(output_file, 'r') as f:
                urls = set(line.strip() for line in f if line.strip())
                all_urls.update(urls)
                db.add_historical_urls(domain_id, urls, tool_name)
            
            SlackNotifier.send_message(
                f"{tool_name.capitalize()} found {len(urls)} historical URLs for {domain}"
            )
        except Exception as e:
            print(f"Error running {tool_name}: {e}")
            SlackNotifier.send_message(
                f":warning: Failed to run {tool_name} for {domain}: {str(e)}"
            )
    
    SlackNotifier.send_message(
        f"Historical content discovery for {domain} is done. Found {len(all_urls)} unique URLs"
    )
    
    db.close()
    return list(all_urls)