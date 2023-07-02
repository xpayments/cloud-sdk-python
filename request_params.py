from dataclasses import dataclass, fields


@dataclass
class RequestParams:
    token: str
    refId: str
    customerId: str
    returnUrl: str
    callbackUrl: str
    cart: list
    force_save_card: str | None = None
    force_transaction_type: str | None = None
    confId: int | None = None

    def to_dict(self) -> dict:
        return dict((field.name, getattr(self, field.name))
                    for field in fields(self) if getattr(self, field.name) is not None)
