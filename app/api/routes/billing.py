from fastapi import APIRouter

router = APIRouter()

# POST /billing/generate-invoice       — ADMIN only, implemented in Phase 4
# GET  /billing/my-invoices            — CLIENT only, implemented in Phase 4
# GET  /billing/invoices/{invoice_id}  — object-level auth, implemented in Phase 4
