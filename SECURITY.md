# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

To report a security vulnerability, please email **praneeth@tuskira.ai** with:

- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested mitigations

You can expect an acknowledgement within **48 hours** and a status update within **7 days**.

**Please do not open a public GitHub issue for security vulnerabilities.**

## Security Considerations

- **Transport:** The server defaults to HTTP on `0.0.0.0:8000`. In production, run behind a reverse proxy (nginx, Caddy) with TLS.
- **Rate limiting:** Built-in `RateLimitingMiddleware` guards all MCP tool endpoints.
- **Data sources:** All upstream API calls (Jolpica, OpenF1) use HTTPS.
- **No authentication:** This server is designed to run in a trusted environment (localhost or private network). Do not expose port 8000 directly to the internet without adding authentication.
