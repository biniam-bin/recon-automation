import os
import re
from config import TEMP_DIR

def ensure_temp_dir():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def clean_domain(domain):
    """Remove http://, https://, and paths from domain"""
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'/.*$', '', domain)
    return domain.lower()

def get_domain_id(domain):
    db = ReconDatabase()
    with db.conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM domains WHERE domain = %s",
            (domain,)
        )
        result = cur.fetchone()
        return result[0] if result else None