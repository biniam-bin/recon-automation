import subprocess
import json
from database import ReconDatabase
from slack_notifier import SlackNotifier
from utils import ensure_temp_dir

def run_katana(domain, output_file):
    cmd = f"katana -u {domain} -jc -kf -d 3 -c 10 -o {output_file}"
    subprocess.run(cmd, shell=True, check=True)

def run_gospider(domain, output_file):
    cmd = f"gospider -s https://{domain} -o /tmp/recon/gospider_output -c 10 -d 3 --json"
    subprocess.run(cmd, shell=True, check=True)
    
    # Parse gospider's JSON output
    urls = set()
    with open('/tmp/recon/gospider_output', 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                if 'output' in data:
                    for url in data['output']:
                        urls.add(url['url'])
            except json.JSONDecodeError:
                continue
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(urls))

def discover_content(domain_id, domain):
    ensure_temp_dir()
    db = ReconDatabase()
    
    tools = {
        'katana': run_katana,
        'gospider': run_gospider
    }
    
    all_urls = set()
    
    for tool_name, tool_func in tools.items():
        try:
            output_file = f"/tmp/recon/{domain_id}_{tool_name}_crawled.txt"
            tool_func(domain, output_file)
            
            with open(output_file, 'r') as f:
                urls = set(line.strip() for line in f if line.strip())
                all_urls.update(urls)
                db.add_crawled_urls(domain_id, urls, tool_name)
            
            SlackNotifier.send_message(
                f"{tool_name.capitalize()} crawled {len(urls)} URLs for {domain}"
            )
        except Exception as e:
            print(f"Error running {tool_name}: {e}")
            SlackNotifier.send_message(
                f":warning: Failed to run {tool_name} for {domain}: {str(e)}"
            )
    
    SlackNotifier.send_message(
        f"Content discovery for {domain} is done. Found {len(all_urls)} unique URLs"
    )
    
    db.close()
    return list(all_urls)