from dataclasses import dataclass
from decimal import Decimal

class MessageError(ValueError):
    pass

AUTH_REQUEST_MTI = "0100"
AUTH_RESPONSE_MTI = "0110"
CLEARING_MTI = "0220"
FIELD_MAP = {2: "transaction_id", 4: "amount", 49: "currency", 41: "device_id", 39: "response_code"}

@dataclass(frozen=True)
class Authorization:
    transaction_id: str
    amount: Decimal
    currency: str
    device_id: str
    response_code: str | None = None

@dataclass(frozen=True)
class ClearingRecord:
    transaction_id: str
    amount: Decimal
    currency: str
    device_id: str

def serialize(mti, fields):
    if len(mti) != 4 or not mti.isdigit(): raise MessageError("MTI must be four digits")
    return "|".join([mti] + [f"{n:02d}={fields[n]}" for n in sorted(fields) if n in FIELD_MAP])

def parse(message):
    parts = message.split("|")
    if not parts or len(parts[0]) != 4 or not parts[0].isdigit(): raise MessageError("invalid MTI")
    out = {}
    for token in parts[1:]:
        try: n, v = token.split("=", 1); n = int(n)
        except ValueError as e: raise MessageError(f"invalid field token: {token}") from e
        if n not in FIELD_MAP or n in out: raise MessageError(f"invalid or duplicate field {n}")
        out[n] = v
    return parts[0], out

def auth_request(a): return serialize(AUTH_REQUEST_MTI, {2:a.transaction_id,4:a.amount,49:a.currency,41:a.device_id})
def auth_response(a):
    if a.response_code is None: raise MessageError("response_code is required")
    return serialize(AUTH_RESPONSE_MTI, {2:a.transaction_id,4:a.amount,49:a.currency,41:a.device_id,39:a.response_code})
def clearing(c): return serialize(CLEARING_MTI, {2:c.transaction_id,4:c.amount,49:c.currency,41:c.device_id})
