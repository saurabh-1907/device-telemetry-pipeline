from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class ReconciliationRow:
    transaction_id: str
    authorization_amount: Decimal | None
    clearing_amount: Decimal | None
    status: str

def reconcile(authorizations, clearings):
    by_id = {c.transaction_id: c for c in clearings}
    rows = []
    seen = set()
    for a in authorizations:
        c = by_id.get(a.transaction_id)
        if c is None: status = 'missing_clearing'
        elif c.amount != a.amount or c.currency != a.currency: status = 'amount_mismatch'
        else: status = 'matched'
        rows.append(ReconciliationRow(a.transaction_id, a.amount, c.amount if c else None, status))
        seen.add(a.transaction_id)
    for c in clearings:
        if c.transaction_id not in seen: rows.append(ReconciliationRow(c.transaction_id, None, c.amount, 'orphan_clearing'))
    return rows
