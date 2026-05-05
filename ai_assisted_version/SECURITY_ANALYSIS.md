# OWASP Top 10 Security Analysis

| OWASP category | Location | Finding | Impact | Severity | Mitigation |
|---|---|---|---|---|---|
| Broken Access Control | `/billing/invoices/{invoice_id}` | A client could try to enumerate invoice IDs. | Disclosure of financial metadata. | High | Foreign invoices return 404 unless requester is admin. |
| Security Misconfiguration | `.env.example`, `app/config.py` | Example secrets could be accidentally reused. | JWT signing or billing operation compromise. | High | Startup validation rejects empty, short and example-like secrets. |
| Software Supply Chain Failures | `pyproject.toml` | Dependencies may contain vulnerable versions. | Vulnerable package execution. | Medium | `pip-audit` target is included in Makefile. |
| Cryptographic Failures | `app/security.py` | Plain passwords would be unsafe. | Credential compromise. | High | bcrypt hashing and password verification are used. |
| Injection | SQLAlchemy queries | Dynamic user input reaches database queries. | SQL injection risk if raw SQL is used. | Medium | ORM query API is used; no string-concatenated SQL. |
| Insecure Design | `/billing/generate` | Client-controlled invoice amount would break billing integrity. | Fraudulent or incorrect invoices. | High | Amount is calculated on backend from active plan. |
| Authentication Failures | `/auth/login` | Brute force login attempts are possible. | Account compromise. | Medium | Redis failed-login limit and generic invalid credentials response. |
| Software or Data Integrity Failures | invoice generation | Duplicate invoices could be created for one month. | Double charging. | Medium | Unique constraint and service-level duplicate check. |
| Security Logging and Alerting Failures | auth/billing events | Sensitive data could leak into logs. | Exposure of tokens or personal data. | Medium | Logs use event names and technical IDs only. |
| Mishandling of Exceptional Conditions | generic exception handler | Tracebacks could leak implementation details. | Information disclosure. | Medium | Generic 500 response hides internal exception details. |

## Retesting

Planned retesting commands:

```bash
uv run python -m compileall app
uv run ruff check app scripts
uv run mypy app
uv run bandit -r app
uv run python scripts/smoke_check.py
uv run pip-audit
```

Manual retesting scenarios:

- register returns 201;
- login returns JWT;
- weak password is rejected;
- public plans are visible without token;
- plan activation requires JWT;
- invoice generation requires admin JWT and `X-Internal-Billing-Key`;
- duplicate invoice returns 409;
- foreign invoice returns 404 for a client;
- oversized request body returns 413.
