# Arvan to Cloudflare DNS Migration Tool

A tool to backup DNS records from Arvan Cloud and convert them to Cloudflare-compatible import format. Available as a **Python CLI** and as a **zero-install web page**.

## 🌐 Use it in your browser (no install)

A static web version runs the whole conversion client-side — no Python, no backend:

👉 **https://salehi.github.io/arvancloud_to_cloudflare/**

1. Paste your Arvan Cloud API key
2. Pick a domain
3. Download the Cloudflare-ready import file

**Your API key never leaves your browser.** GitHub Pages serves only static files; requests go directly from your browser to Arvan Cloud's API (which sends `Access-Control-Allow-Origin: *`, so no proxy is involved). Nothing is logged or sent to any third party. The page source lives in [`www/index.html`](www/index.html).

> Prefer automation, cron jobs, or exporting *all* domains at once? Use the Python CLI below.

## Features

- ✅ Exports all DNS records from Arvan Cloud using their native API
- ✅ Converts records to Cloudflare import-compatible BIND9 format
- ✅ Supports all major record types (A, AAAA, CNAME, MX, TXT, SRV, ANAME)
- ✅ Handles both single domain and bulk domain exports
- ✅ Automatic timestamping of backup files
- ✅ Comprehensive error handling and logging

## Prerequisites

- Python 3.6 or higher
- `requests` library
- Valid Arvan Cloud API key

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/arvan-to-cloudflare
cd arvan-to-cloudflare
```

2. Install required dependencies:
```bash
pip install requests
```

3. Set up your Arvan Cloud API key as an environment variable:
```bash
export ARVAN_API_KEY="your_arvan_api_key_here"
```

## Getting Your Arvan API Key

1. Log in to your [Arvan Cloud Dashboard](https://panel.arvancloud.ir/)
2. Navigate to **Profile** > **API Keys**
3. Generate a new API key with DNS management permissions
4. Copy the API key for use with this script

## Usage

### Backup All Domains

To export DNS records for all domains in your Arvan Cloud account:

```bash
python3 arvan_to_cloudflare.py
```

### Backup Specific Domain

To export DNS records for a specific domain:

```bash
python3 arvan_to_cloudflare.py example.com
```

## Output Format

The script generates timestamped backup files in Cloudflare-compatible format:

```
example.com_dns_backup_cloudflare_20250803_143022.txt
```

Each file contains:
- Header with export timestamp and domain information
- DNS records in BIND9 format compatible with Cloudflare import
- Proper handling of TTL values and record formatting

### Example Output

```
; DNS records for example.com
; Exported from Arvan Cloud on 2025-08-03T14:30:22
; Format: Cloudflare import compatible

example.com	300	IN	A	192.168.1.1
www.example.com	300	IN	CNAME	example.com.
mail.example.com	300	IN	MX	10	mail.provider.com.
example.com	300	IN	TXT	"v=spf1 include:_spf.provider.com ~all"
```

## Importing to Cloudflare

1. Log in to your Cloudflare dashboard
2. Add your domain to Cloudflare (if not already added)
3. Go to **DNS** > **Records**
4. Click **Import DNS records**
5. Upload the generated `.txt` file
6. Review and confirm the import

## Supported Record Types

| Record Type | Support Status | Notes |
|-------------|----------------|-------|
| A           | ✅ Full        | IPv4 addresses |
| AAAA        | ✅ Full        | IPv6 addresses |
| CNAME       | ✅ Full        | Canonical names |
| MX          | ✅ Full        | Mail exchange |
| TXT         | ✅ Full        | Text records |
| SRV         | ✅ Full        | Service records |
| ANAME       | ✅ Full        | Alias records |
| NS          | ⚠️ Skipped     | Handled by Cloudflare |

## Error Handling

The script includes comprehensive error handling for:
- Invalid API keys
- Network connectivity issues
- API rate limiting
- Malformed DNS records
- File I/O operations

## Security Notes

- Store your API key securely using environment variables
- Never commit API keys to version control
- Consider using `.env` files for local development
- The API key requires DNS read permissions only

## Troubleshooting

### Common Issues

**"ARVAN_API_KEY environment variable not set"**
- Ensure you've exported your API key: `export ARVAN_API_KEY="your_key"`

**"Error fetching domains"**
- Verify your API key has correct permissions
- Check your internet connection
- Ensure the API key is valid and not expired

**"No records found"**
- The domain may not have any DNS records configured
- Verify the domain exists in your Arvan Cloud account

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is not officially affiliated with Arvan Cloud or Cloudflare. Use at your own risk and always verify exported records before importing to production environments.

## Support

If you encounter issues or have questions:
- Check the [Issues](https://github.com/yourusername/arvan-to-cloudflare/issues) page
- Create a new issue with detailed error information
- Include relevant log output and your Python version

---

**⚠️ Important**: Always test imports in a staging environment before applying to production domains.