from pathlib import Path

from app.main import app


REQUIRED_ROUTES = {
    "/",
    "/auth/register",
    "/auth/login",
    "/auth/me",
    "/plans",
    "/plans/activate",
    "/billing/invoices",
    "/billing/invoices/{invoice_id}",
    "/billing/generate",
}

REQUIRED_FILES = [
    "app/web/index.html",
    "app/web/styles.css",
    "app/web/app.js",
    "Dockerfile",
    "docker-compose.yml",
    "Makefile",
    "README.md",
    "AI_USAGE.md",
    "SECURITY_ANALYSIS.md",
    "COMPARISON.md",
    "main.tex",
]


def main() -> None:
    route_paths = {route.path for route in app.routes}
    missing_routes = REQUIRED_ROUTES - route_paths
    if missing_routes:
        raise SystemExit(f"Missing routes: {sorted(missing_routes)}")

    missing_files = [path for path in REQUIRED_FILES if not Path(path).exists()]
    if missing_files:
        raise SystemExit(f"Missing files: {missing_files}")

    html = Path("app/web/index.html").read_text(encoding="utf-8")
    if "/web/styles.css" not in html or "/web/app.js" not in html:
        raise SystemExit("Frontend assets are not linked from index.html")

    report = Path("main.tex").read_text(encoding="utf-8")
    required_report_phrases = [
        "AI-assisted",
        "OWASP Top 10",
        "Сравнительный анализ",
        "Prompt",
        "Повторное тестирование",
    ]
    for phrase in required_report_phrases:
        if phrase not in report:
            raise SystemExit(f"Report does not mention: {phrase}")

    print("AI-assisted version smoke check passed")


if __name__ == "__main__":
    main()
