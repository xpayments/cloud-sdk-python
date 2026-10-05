# X-Payments Cloud SDK for Python

**Work in progress.** For production integrations, the [PHP SDK](https://github.com/xpayments/cloud-sdk-php) is the reference implementation.

When processing online credit card payments, X-Payments works as an intermediary between a shopping cart application or any other API-friendly system on one side and payment gateways and 3D-Secure systems on the other side, implementing the PCI compliant secure layer that works with credit card data and keeps your applications and systems out of the PCI scope.

This SDK targets the [X-Payments Cloud server-side API](https://xpayments.stoplight.io/docs/server-side-api/spsxnj22ewcd7-x-payments-cloud-api-overview) version 4.8.

### Requirements

- Python 3.10+
- `requests` and `python-dotenv` (`pip install -r requirements.txt`)

### Usage

The modules are plain files, not a package: put them on your import path and import `xpayments_cloud`.

```python
from xpayments_cloud import Client
from request_params import PaymentRequestParams

client = Client(account, api_key, secret_key)

response = client.do_pay(PaymentRequestParams(
    token=token,                  # one-time token from the X-Payments Cloud payment widget
    refId="1001",
    customerId="",
    returnUrl="https://shop.example.com/checkout/xpayments-return",
    callbackUrl="https://shop.example.com/xpayments-callback",
    cart=cart,                    # same structure as in the PHP SDK README
))
```

Methods return the decoded JSON response as a `dict` and raise `requests.HTTPError` on HTTP errors.

Covered API calls:

- payment: `do_pay`, `do_tokenize_card`, `do_continue`, `do_capture`, `do_void`, `do_refund`, `do_accept`, `do_decline`, `do_get_info`, `do_refresh`, `do_rebill`
- customer: `do_get_customer_cards`
- bulk operations: `do_add_bulk_operation`, `do_start_bulk_operation`, `do_stop_bulk_operation`, `do_get_bulk_operation`, `do_delete_bulk_operation`
- connection check: `do_test_connection`

Unlike the PHP SDK, this SDK does not yet verify the `X-Payments-Signature` of responses or parse callbacks. Keep card details in the X-Payments Cloud payment widget and the API keys on the server only.

### Supported payment gateways
X-Payments Cloud supports more than 60 payment gateway integrations: ANZ eGate, American Express Web-Services API Integration, Authorize.Net, Bambora (Beanstream), Beanstream (legacy API), Bendigo Bank, BillriantPay, BluePay, BlueSnap Payment API (XML), Braintree, BluePay Canada (Caledon), Cardinal Commerce Centinel, Chase Paymentech, CommWeb - Commonwealth Bank, BAC Credomatic, CyberSource - SOAP Toolkit API, X-Payments Demo Pay, X-Payments Demo Pay 3-D Secure, DIBS, DirectOne - Direct Interface, eProcessing Network - Transparent Database Engine, SecurePay Australia, Moneris eSELECTplus, Elavon (Realex API), ePDQ MPI XML (Phased out), eWAY Rapid - Direct Connection, eWay Realtime Payments XML, Sparrow (5th Dimension Gateway), First Data Payeezy Gateway (ex- Global Gateway e4), Global Iris, Global Payments, GoEmerchant - XML Gateway API, HeidelPay, Innovative Gateway, iTransact XML, Payment XP (Meritus) Web Host, NAB - National Australia Bank, NMI (Network Merchants Inc.), Netbilling - Direct Mode, Netevia, Ingenico ePayments (Ogone e-Commerce), PayGate South Africa, Payflow Pro, PayPal REST API, PayPal Payments Pro (PayPal API), PayPal Payments Pro (Payflow API), PSiGate XML API, QuantumGateway - XML Requester, Intuit QuickBooks Payments, QuickPay, Worldpay Corporate Gateway - Direct Model, Global Payments (ex. Realex), Opayo Direct (ex. Sage Pay Go - Direct Interface), Paya (ex. Sage Payments US), Simplify Commerce by MasterCard, SkipJack, Suncorp, TranSafe, powered by Monetra, 2Checkout, USA ePay - Transaction Gateway API, Elavon Converge (ex VirtualMerchant), WebXpress, Worldpay Total US, Worldpay US (Lynk Systems).

### Supported fraud-screening services
 - Kount
 - NoFraud
 - Signifyd

### License

MIT. See [LICENSE](LICENSE).

Copyright (c) 2023-present X-Cart Holdings LLC.

### Support
If you have any questions, please [contact us](https://www.x-payments.com/contact-us).
