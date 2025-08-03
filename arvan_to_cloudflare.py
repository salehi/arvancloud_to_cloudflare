#!/usr/bin/env python3
"""
Arvan Cloud DNS Records Backup Script
Uses Arvan's native export API to get BIND9 compatible format
"""

import os
import sys
import requests
from datetime import datetime


class ArvanDNSBackup:
    def __init__(self):
        self.api_key = os.getenv('ARVAN_API_KEY')
        if not self.api_key:
            print("Error: ARVAN_API_KEY environment variable not set")
            sys.exit(1)

        self.base_url = "https://napi.arvancloud.ir/cdn/4.0"
        self.headers = {
            'Authorization': f'Apikey {self.api_key}',
            'Content-Type': 'application/json'
        }

    def get_domains(self):
        """Get list of all domains"""
        try:
            response = requests.get(f"{self.base_url}/domains", headers=self.headers)
            response.raise_for_status()
            return response.json()['data']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching domains: {e}")
            return []

    def export_dns_records(self, domain):
        """Export DNS records using Arvan's native export API"""
        try:
            url = f"{self.base_url}/domains/{domain}/dns-records"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error exporting DNS records for {domain}: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return None

    def json_to_cloudflare_import(self, records_data, domain):
        """Convert Arvan JSON response to Cloudflare import format"""
        if not records_data or 'data' not in records_data:
            return ""

        lines = []
        lines.append(f"; DNS records for {domain}")
        lines.append(f"; Exported from Arvan Cloud on {datetime.now().isoformat()}")
        lines.append(f"; Format: Cloudflare import compatible")
        lines.append("")

        for record in records_data['data']:
            record_type = record['type'].upper()
            if record_type == 'NS':
                continue
            name = record['name']
            ttl = record.get('ttl', 300)

            # Handle root domain
            if name == '@' or name == domain:
                name = domain
            elif not name.endswith(f'.{domain}'):
                name = f"{name}.{domain}" if name else domain

            # Handle different record types
            if record_type == 'A' or record_type == 'AAAA':
                # Extract IP from value array
                for value_item in record.get('value', []):
                    ip = value_item.get('ip', '')
                    if ip:
                        lines.append(f"{name}\t{ttl}\tIN\t{record_type}\t{ip}")
            elif record_type in ['ANAME']:
                # These have dict values
                value = record.get('value', {})
                if isinstance(value, dict) and value:
                    value = value['location'] if value['host_header'] == 'source' else value['host_header']
                if value and not value.endswith('.'):
                    value += '.'
                lines.append(f"{name}\t{ttl}\tIN\t{record_type}\t{value}")
            elif record_type in ['CNAME']:
                # These have dict values
                value = record.get('value', {})
                if isinstance(value, dict) and value:
                    value = value['host'] if value['host_header'] == 'source' else value['host_header']
                if value and not value.endswith('.'):
                    value += '.'
                lines.append(f"{name}\t{ttl}\tIN\t{record_type}\t{value}")

            elif record_type == 'MX':
                # MX records have priority and exchange
                value = record.get('value', '')
                if isinstance(value, list) and value:
                    mx_data = value[0]
                    priority = mx_data.get('priority', 10)
                    exchange = mx_data.get('value', mx_data.get('exchange', ''))
                    if exchange and not exchange.endswith('.'):
                        exchange += '.'
                    lines.append(f"{name}\t{ttl}\tIN\t{record_type}\t{priority}\t{exchange}")
                elif isinstance(value, str):
                    # Assume format like "10 mail.example.com"
                    lines.append(f"{name}\t{ttl}\tIN\t{record_type}\t{value}")

            elif record_type == 'TXT':
                # TXT records
                value = record.get('value')['text']
                # Ensure TXT is quoted
                if value and not (value.startswith('"') and value.endswith('"')):
                    value = f'"{value}"'
                lines.append(f"{name}\t{ttl}\tIN\t{record_type}\t{value}")

            elif record_type == 'SRV':
                # SRV records have priority, weight, port, target
                value = record.get('value', '')
                if isinstance(value, list) and value:
                    srv_data = value[0]
                    priority = srv_data.get('priority', 0)
                    weight = srv_data.get('weight', 0)
                    port = srv_data.get('port', 0)
                    target = srv_data.get('target', srv_data.get('value', ''))
                    if target and not target.endswith('.'):
                        target += '.'
                    lines.append(f"{name}\t{ttl}\tIN\t{record_type}\t{priority}\t{weight}\t{port}\t{target}")
                elif isinstance(value, str):
                    lines.append(f"{name}\t{ttl}\tIN\t{record_type}\t{value}")

            else:
                # Generic handling for other record types
                value = record.get('value', '')
                if isinstance(value, list) and value:
                    value = value[0] if isinstance(value[0], str) else str(value[0])
                lines.append(f"{name}\t{ttl}\tIN\t{record_type}\t{value}")

        return '\n'.join(lines)

    def backup_domain(self, domain):
        """Backup DNS records for a domain using JSON API"""
        print(f"Exporting DNS records for: {domain}")

        records_data = self.export_dns_records(domain)
        if not records_data:
            print(f"Failed to export records for {domain}")
            return None

        # Convert JSON to Cloudflare import format
        zone_content = self.json_to_cloudflare_import(records_data, domain)
        if not zone_content:
            print(f"No records found for {domain}")
            return None

        # Create backup file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{domain}_dns_backup_cloudflare_{timestamp}.txt"

        with open(filename, 'w') as f:
            f.write(zone_content)

        print(f"Backup saved to: {filename}")
        record_count = len(records_data.get('data', []))
        print(f"Exported {record_count} DNS records")
        return filename

    def backup_all_domains(self):
        """Backup all domains in the account"""
        domains = self.get_domains()
        if not domains:
            print("No domains found in your Arvan Cloud account")
            return

        print(f"Found {len(domains)} domain(s)")
        backup_files = []

        for domain_info in domains:
            domain = domain_info['domain']
            filename = self.backup_domain(domain)
            if filename:
                backup_files.append(filename)
            print("-" * 50)

        print(f"\nBackup complete! Created {len(backup_files)} zone files:")
        for filename in backup_files:
            print(f"  - {filename}")


def main():
    if len(sys.argv) > 1:
        # Backup specific domain
        domain = sys.argv[1]
        backup = ArvanDNSBackup()
        backup.backup_domain(domain)
    else:
        # Backup all domains
        backup = ArvanDNSBackup()
        backup.backup_all_domains()


if __name__ == "__main__":
    main()
