from dataclasses import dataclass, fields
from typing import Any


@dataclass
class PaymentRequestParams:
    token: str
    refId: str
    customerId: str
    returnUrl: str
    callbackUrl: str
    cart: list
    forceSaveCard: bool | None = None
    forceTransactionType: str | None = None
    confId: int | None = None

    def __get(self, field: str) -> Any:
        val = getattr(self, field)
        if type(val) is bool:
            return "Y" if val is True else "N"
        return val

    def to_dict(self) -> dict:
        """
        Converts this dataclass to a dict.
        'None' params are excluded. Boolean values are replaced: True->Y / False->N
        """
        return dict((field.name, self.__get(field.name))
                    for field in fields(self) if getattr(self, field.name) is not None)


@dataclass(frozen=True)
class TransactionType:
    """
    TransactionType.A - Authorize only
    TransactionType.S - Sale (Auth & Capture)
    """
    A = "A"
    S = "S"
