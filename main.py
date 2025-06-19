import argparse
from subdomain_enumeration import enumerate_subdomains
from port_scanning import scan_ports_and_identify_live
from historical_content import discover_historical_content
from content_discovery import discover_content
from database import ReconDatabase
from slack_notifier import SlackNotifier

def main():
    parser = argparse.ArgumentParser(description='Recon Automation Tool')
    parser.add_argument('domain', help='Domain to perform recon on')
    args = parser.parse_args()
    
    domain = args.domain
    
    try:
        # Step 1: Subdomain enumeration
        subdomains = enumerate_subdomains(domain)
        
        db = ReconDatabase()
        domain_id = db.get_domain_id(domain)
        subdomains_with_ids = db.get_subdomains(domain_id)
        
        # Step 2: Port scanning and live sub identification
        scan_ports_and_identify_live(domain_id, subdomains_with_ids)
        
        # Step 3: Historical content discovery
        discover_historical_content(domain_id, domain)
        
        # Step 4: Content discovery by spidering
        discover_content(domain_id, domain)
        
        # Final summary
        summary = db.get_scan_summary(domain_id)
        summary_message = (
            f"Recon complete for {domain}!\n"
            f"• Subdomains found: {summary['subdomains']}\n"
            f"• Open ports found: {summary['open_ports']}\n"
            f"• Historical URLs: {summary['historical_urls']}\n"
            f"• Crawled URLs: {summary['crawled_urls']}"
        )
        
        SlackNotifier.send_message(summary_message, is_complete=True)
        db.close()
        
    except Exception as e:
        SlackNotifier.send_message(f":exclamation: Critical error during recon for {domain}: {str(e)}")
        raise

if __name__ == "__main__":
    main()