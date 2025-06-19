import psycopg2
from psycopg2 import sql
from config import DB_CONFIG

class ReconDatabase:
    def __init__(self):
        self.conn = None
        self.connect()
        self.initialize_db()

    def connect(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
    
    def initialize_db(self):
        with self.conn.cursor() as cur:
            # Create tables if they don't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS domains (
                    id SERIAL PRIMARY KEY,
                    domain VARCHAR(255) NOT NULL,
                    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS subdomains (
                    id SERIAL PRIMARY KEY,
                    domain_id INTEGER REFERENCES domains(id),
                    subdomain VARCHAR(255) NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    UNIQUE(domain_id, subdomain)
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ports (
                    id SERIAL PRIMARY KEY,
                    subdomain_id INTEGER REFERENCES subdomains(id),
                    port INTEGER NOT NULL,
                    service VARCHAR(100),
                    protocol VARCHAR(10),
                    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(subdomain_id, port)
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS historical_urls (
                    id SERIAL PRIMARY KEY,
                    domain_id INTEGER REFERENCES domains(id),
                    url TEXT NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS crawled_urls (
                    id SERIAL PRIMARY KEY,
                    domain_id INTEGER REFERENCES domains(id),
                    url TEXT NOT NULL,
                    method VARCHAR(10) NOT NULL,
                    status_code INTEGER,
                    source VARCHAR(50) NOT NULL,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
    
    def add_domain(self, domain):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO domains (domain) VALUES (%s) RETURNING id",
                (domain,)
            )
            domain_id = cur.fetchone()[0]
            self.conn.commit()
            return domain_id
    
    def add_subdomains(self, domain_id, subdomains, source):
        with self.conn.cursor() as cur:
            for subdomain in subdomains:
                try:
                    cur.execute(
                        """
                        INSERT INTO subdomains (domain_id, subdomain, source)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (domain_id, subdomain) DO NOTHING
                        """,
                        (domain_id, subdomain, source)
                    )
                except Exception as e:
                    print(f"Error adding subdomain {subdomain}: {e}")
                    self.conn.rollback()
                    continue
            self.conn.commit()
    
    def add_ports(self, subdomain_id, ports):
        with self.conn.cursor() as cur:
            for port_info in ports:
                try:
                    cur.execute(
                        """
                        INSERT INTO ports (subdomain_id, port, service, protocol)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (subdomain_id, port) DO NOTHING
                        """,
                        (subdomain_id, port_info['port'], port_info['service'], port_info['protocol'])
                    )
                except Exception as e:
                    print(f"Error adding port {port_info}: {e}")
                    self.conn.rollback()
                    continue
            self.conn.commit()
    
    def add_historical_urls(self, domain_id, urls, source):
        with self.conn.cursor() as cur:
            for url in urls:
                try:
                    cur.execute(
                        """
                        INSERT INTO historical_urls (domain_id, url, source)
                        VALUES (%s, %s, %s)
                        """,
                        (domain_id, url, source)
                    )
                except Exception as e:
                    print(f"Error adding historical URL {url}: {e}")
                    self.conn.rollback()
                    continue
            self.conn.commit()
    
    def add_crawled_urls(self, domain_id, urls, source, method="GET", status_code=None):
        with self.conn.cursor() as cur:
            for url in urls:
                try:
                    cur.execute(
                        """
                        INSERT INTO crawled_urls (domain_id, url, method, status_code, source)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (domain_id, url, method, status_code, source)
                    )
                except Exception as e:
                    print(f"Error adding crawled URL {url}: {e}")
                    self.conn.rollback()
                    continue
            self.conn.commit()
    
    def get_subdomains(self, domain_id):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, subdomain FROM subdomains WHERE domain_id = %s",
                (domain_id,)
            )
            return cur.fetchall()
    
    def get_scan_summary(self, domain_id):
        with self.conn.cursor() as cur:
            # Subdomains count
            cur.execute(
                "SELECT COUNT(*) FROM subdomains WHERE domain_id = %s",
                (domain_id,)
            )
            subdomains_count = cur.fetchone()[0]
            
            # Open ports count
            cur.execute(
                """
                SELECT COUNT(*) FROM ports p
                JOIN subdomains s ON p.subdomain_id = s.id
                WHERE s.domain_id = %s
                """,
                (domain_id,)
            )
            ports_count = cur.fetchone()[0]
            
            # Historical URLs count
            cur.execute(
                "SELECT COUNT(*) FROM historical_urls WHERE domain_id = %s",
                (domain_id,)
            )
            historical_urls_count = cur.fetchone()[0]
            
            # Crawled URLs count
            cur.execute(
                "SELECT COUNT(*) FROM crawled_urls WHERE domain_id = %s",
                (domain_id,)
            )
            crawled_urls_count = cur.fetchone()[0]
            
            return {
                'subdomains': subdomains_count,
                'open_ports': ports_count,
                'historical_urls': historical_urls_count,
                'crawled_urls': crawled_urls_count
            }
    
    def close(self):
        if self.conn:
            self.conn.close()