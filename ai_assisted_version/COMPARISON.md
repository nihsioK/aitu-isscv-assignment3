# Comparison: Assignment 1 vs Assignment 2

| Criterion | Assignment 1 manual version | Assignment 2 AI-assisted version | Security conclusion |
|---|---|---|---|
| Development approach | Manual iterative development | AI-assisted generation and review | AI speeds up work but requires review. |
| Backend stack | FastAPI and SQLAlchemy | FastAPI and SQLAlchemy | Equivalent security baseline. |
| UI structure | Static frontend separated from backend route | Static frontend separated from backend route | Both are maintainable enough for MVP. |
| Data model | users, tariffs, invoices | customers, plans, invoices | Same business coverage with independent naming. |
| Authentication | JWT and bcrypt | JWT and bcrypt | Equivalent core control. |
| Authorization | Client/admin, object-level invoice checks | Client/admin, object-level invoice checks | Equivalent access-control goal. |
| Internal operation protection | Internal API key | Internal billing key | AI version preserved defense-in-depth. |
| Input validation | Pydantic schemas | Pydantic schemas | Equivalent validation strategy. |
| Billing integrity | Backend-calculated invoice amount | Backend-calculated invoice amount | Both prevent client-controlled amount. |
| Duplicate prevention | Service check | Unique constraint and service check | AI version adds DB-level integrity. |
| Login abuse control | Redis failed-login limit | Redis failed-login limit | Equivalent brute-force mitigation. |
| Documentation | README and report | README, AI_USAGE, SECURITY_ANALYSIS, COMPARISON, main.tex | AI version documents AI influence more explicitly. |
| Risk of AI errors | Not applicable | Possible hallucinated code or incomplete controls | Human verification remains necessary. |

## Conclusion

AI-assisted development improved speed and documentation breadth, but it did not remove the need for human security review. The main security benefit is faster checklist-based OWASP coverage. The main risk is accepting generated code without validating authorization, secret handling and data integrity.
