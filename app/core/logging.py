import logging

# Logging configuration — PII-safe handlers added in Phase 9
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("telecom")
