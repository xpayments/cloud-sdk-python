from dataclasses import dataclass, fields
from typing import Any


@dataclass(frozen=True)
class TransactionType:
    """
    TransactionType.Auth - Authorize only
    TransactionType.Sale - Auth & Capture
    """
    Auth = "A"
    Sale = "S"


@dataclass(frozen=True)
class DurationUnit:
    Day = "D"
    Week = "W"
    Month = "M"
    Year = "Y"


@dataclass(frozen=True)
class ScheduleType:
    """
    ScheduleType.Each - Each specific day
    ScheduleType.Every - Every X days
    """
    Each = "E"
    Every = "D"


@dataclass
class BaseParamsClass:
    def _get(self, field: str) -> Any:
        return getattr(self, field)

    def to_dict(self) -> dict:
        """
        Converts this dataclass to a dict.
        Optional 'None' params are excluded.
        """
        return dict((field.name, self._get(field.name))
                    for field in fields(self) if getattr(self, field.name) is not None)


@dataclass
class Address(BaseParamsClass):
    firstname: str
    address: str
    city: str
    state: str
    zipcode: str
    country: str
    lastname: str | None = None
    zip4: str | None = None
    company: str | None = None
    phone: str | None = None
    fax: str | None = None


@dataclass
class SubscriptionSchedule(BaseParamsClass):
    type: ScheduleType | None = None
    number: int | None = None
    reverse: bool | None = None
    period: DurationUnit | None = None
    periods: int | None = None


@dataclass
class SubscriptionPlan(BaseParamsClass):
    subscriptionSchedule: SubscriptionSchedule | None = None
    callbackUrl: str | None = None
    recurringAmount: float | None = None
    description: str | None = None
    uniqueOrderItemId: str | None = None
    trialDuration: int | None = None
    trialDurationUnit: DurationUnit | None = None


@dataclass
class CartItem(BaseParamsClass):
    sku: str
    name: str
    price: float
    quantity: int | None = None
    isSubscription: bool | None = None
    subscriptionPlan: SubscriptionPlan | None = None


@dataclass
class Cart(BaseParamsClass):
    billingAddress: Address
    merchantEmail: str
    currency: str
    items: list[CartItem]
    totalCost: float
    shippingAddress: Address | None = None
    login: str | None = None
    shippingCost: float | None = None
    taxCost: float | None = None
    discount: float | None = None
    description: str | None = None


@dataclass
class PaymentRequestParams(BaseParamsClass):
    token: str
    refId: str
    returnUrl: str
    cart: Cart
    callbackUrl: str | None = None
    customerId: str | None = None
    forceSaveCard: bool | None = None
    forceTransactionType: TransactionType | None = None
    confId: int | None = None

    def _get(self, field: str) -> Any:
        """
        Boolean values are replaced: True->Y / False->N
        """
        val = getattr(self, field)
        if type(val) is bool:
            return "Y" if val is True else "N"
        return val


