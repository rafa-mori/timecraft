# Security Policy

## Supported Versions

We actively support the following versions of TimeCraft AI with security updates:

| Version | Supported          | End of Support |
| ------- | ------------------ | -------------- |
| 1.1.x   | :white_check_mark: | TBD            |
| 1.0.x   | :white_check_mark: | 2025-12-31     |
| < 1.0   | :x:                | Ended          |

## Security Considerations

TimeCraft handles sensitive data including:

- Database connection credentials
- Webhook URLs and authentication tokens
- Time series data that may contain business-critical information
- Configuration files with sensitive settings

### Best Practices

When using TimeCraft, please follow these security best practices:

1. **Credential Management**
   - Never commit credentials to version control
   - Use environment variables for sensitive configuration
   - Regularly rotate database passwords and API keys
   - Use secure credential storage solutions

2. **Network Security**
   - Use encrypted connections (HTTPS/TLS) for webhooks
   - Implement proper firewall rules for database access
   - Consider using VPNs for sensitive database connections

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Use secure protocols for data transmission
   - Implement proper access controls
   - Regular security audits of your deployment

4. **Configuration Security**
   - Secure configuration files with appropriate permissions
   - Use configuration validation to prevent injection attacks
   - Implement proper logging without exposing sensitive data

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in TimeCraft AI, please follow these steps:

### How to Report

1. **Do NOT create a public GitHub issue** for security vulnerabilities
2. **Email us directly** at [faelmori@gmail.com](mailto:faelmori@gmail.com) with the subject line: "TimeCraft AI Security Vulnerability"
3. **Include the following information**:
   - A clear description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Any suggested fixes or mitigations
   - Your contact information for follow-up

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Updates**: We will keep you informed of our progress every 7 days
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days
- **Credit**: We will acknowledge your contribution in the security advisory (if desired)

### Response Timeline

| Severity | Initial Response | Target Resolution |
|----------|------------------|-------------------|
| Critical | 24 hours         | 7 days            |
| High     | 48 hours         | 14 days           |
| Medium   | 5 days           | 30 days           |
| Low      | 7 days           | 60 days           |

## Security Update Process

When we release security updates:

1. We will create a security advisory on GitHub
2. We will release a patched version following semantic versioning
3. We will notify users through:
   - GitHub releases
   - Security advisory notifications
   - Project documentation updates

## Vulnerability Disclosure Policy

We follow responsible disclosure practices:

1. **Private Disclosure**: Vulnerabilities are initially disclosed privately to maintainers
2. **Coordinated Disclosure**: We work with reporters to develop and test fixes
3. **Public Disclosure**: Details are made public only after fixes are available
4. **Timeline**: We aim for public disclosure within 90 days of initial report

## Security Contact

- **Primary Contact**: Rafael Mori ([faelmori@gmail.com](mailto:faelmori@gmail.com))
- **GitHub**: [@rafa-mori](https://github.com/rafa-mori)
- **Response Time**: Within 48 hours during business days

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Guide](https://python-security.readthedocs.io/)
- [Database Security Best Practices](https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure)

---

Thank you for helping keep TimeCraft and its users safe!
