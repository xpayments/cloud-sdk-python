from requests import post
from requests.exceptions import RequestException, HTTPError
from json import JSONDecodeError, dumps as json_dumps
from base64 import b64encode
from hmac import new as hmac_new
from hashlib import sha256
from exceptions import IllegalArgumentError, JSONProcessingError, UnicodeProcessingError
from request_params import PaymentRequestParams
from dotenv import dotenv_values

config = dotenv_values(".env")


class Request:

    XP_DOMAIN = "xpayments.com"
    TEST_SERVER_HOST: str
    API_VERSION = "4.8"
    CONNECTION_TIMEOUT = 120
    account: str
    api_key: str
    secret_key: str

    def __init__(self, account: str, api_key: str, secret_key: str) -> None:
        """
        Request constructor
        """
        if not all([len(str(v)) > 0 for v in locals().values() if type(v) is not Request]):
            raise IllegalArgumentError
        self.account = str(account)
        self.api_key = str(api_key)
        self.secret_key = str(secret_key)
        self.TEST_SERVER_HOST = config.get('TEST_SERVER_HOST', '')

    def send(self, controller: str, action: str, request_data: dict) -> str:
        """
        Send API request to X-Payments Cloud
        """
        request = json_dumps(request_data)
        url = self.get_api_endpoint(action=action, controller=controller)
        headers = {
            "Authorization": f"Basic {self.get_authorization_header()}",
            "X-Payments-Signature": self.get_signature_header(action=action, data=request),
            "Content-Type": "application/json",
        }
        try:
            response = post(url=url, data=request, headers=headers, timeout=self.CONNECTION_TIMEOUT)
        except RequestException:
            raise HTTPError
        response.raise_for_status()
        try:
            # print(response.json())
            return response.json()
        except JSONDecodeError as ex:
            raise JSONProcessingError(ex.msg)

    def get_authorization_header(self) -> str:
        """
        Get Basic HTTP Authorization header
        """
        try:
            data = f"{self.account}:{self.api_key}".encode()
            return b64encode(data).decode()
        except UnicodeEncodeError | UnicodeDecodeError:
            raise UnicodeProcessingError

    def get_signature_header(self, action: str, data: str) -> str:
        """
        Get signature header
        """
        try:
            message = f"{action}{data}".encode()
            return hmac_new(key=self.secret_key.encode(), msg=message, digestmod=sha256).hexdigest()
        except UnicodeEncodeError:
            raise UnicodeProcessingError

    def get_server_host(self) -> str:
        """
        Get X-Payments server host
        """
        return self.TEST_SERVER_HOST if len(self.TEST_SERVER_HOST) > 0 \
            else f"{self.account}.{self.XP_DOMAIN}"

    def get_api_endpoint(self, action: str, controller: str) -> str:
        """
        Get API endpoint
        """
        return f"https://{self.get_server_host()}/api/{self.API_VERSION}/{controller}/{action}"


class Client:

    account: str
    api_key: str
    secret_key: str
    request: Request

    def __init__(self, account: str, api_key: str, secret_key: str) -> None:
        """
        Client constructor
        """
        if not all([len(str(v)) > 0 for v in locals().values() if type(v) is not Client]):
            raise IllegalArgumentError
        self.account = str(account)
        self.api_key = str(api_key)
        self.secret_key = str(secret_key)
        self.request = Request(account=self.account, api_key=self.api_key, secret_key=self.secret_key)

    def do_pay(self, params: PaymentRequestParams) -> str:
        """
        Process payment
        """
        return self.request.send(controller='payment', action='pay', request_data=params.to_dict())

    def do_tokenize_card(self, params: PaymentRequestParams) -> str:
        """
        Tokenize card
        """
        return self.request.send(controller='payment', action='tokenize_card', request_data=params.to_dict())

    def do_rebill(self, xpid: str, ref_id: str, customer_id: str, cart: list, callback_url: str) -> str:
        """
        Rebill payment (process payment using the saved card)
        """
        params = {
            "xpid": xpid,
            "refId": ref_id,
            "customerId": customer_id,
            "cart": cart,
            "callbackUrl": callback_url
        }
        return self.request.send(controller='payment', action='rebill', request_data=params)

    def do_action(self, action: str, xpid: str, amount: int | None = None) -> str:
        """
        Execute secondary payment action
        """
        params = {"xpid": xpid}
        if amount is not None and amount > 0:
            params.amount = amount
        return self.request.send(controller='payment', action=action, request_data=params)

    def do_capture(self, xpid: str, amount: int) -> str:
        """
        Capture payment
        """
        return self.do_action(action='capture', xpid=xpid, amount=amount)

    def do_void(self, xpid: str, amount: int) -> str:
        """
        Void payment
        """
        return self.do_action(action='void', xpid=xpid, amount=amount)

    def do_refund(self, xpid: str, amount: int) -> str:
        """
        Refund payment
        """
        return self.do_action(action='refund', xpid=xpid, amount=amount)

    def do_continue(self, xpid: str) -> str:
        """
        Continue payment
        """
        return self.do_action(action='continue', xpid=xpid)

    def do_accept(self, xpid: str) -> str:
        """
        Accept payment
        """
        return self.do_action(action='accept', xpid=xpid)

    def do_decline(self, xpid: str) -> str:
        """
        Decline payment
        """
        return self.do_action(action='decline', xpid=xpid)

    def do_get_info(self, xpid: str) -> str:
        """
        Get detailed payment information
        """
        return self.do_action(action='get_info', xpid=xpid)

    def do_get_customer_cards(self, customer_id: str, status: str = 'any') -> str:
        """
        Get customer's cards
        """
        params = {
            "customerId": customer_id,
            "status": status
        }
        return self.request.send(controller='customer', action='get_cards', request_data=params)

    def do_add_bulk_operation(self, operation: str, xpids: list[str]) -> str:
        """
        Add bulk operation
        """
        params = {
            "operation": operation,
            "payments": [{'xpid': xpid} for xpid in xpids],
        }
        return self.request.send(controller='bulk_operation', action='add', request_data=params)

    def do_start_bulk_operation(self, batch_id: str) -> str:
        """
        Start bulk operation
        """
        params = {"batch_id": batch_id}
        return self.request.send(controller='bulk_operation', action='start', request_data=params)

    def do_stop_bulk_operation(self, batch_id: str) -> str:
        """
        Stop bulk operation
        """
        params = {"batch_id": batch_id}
        return self.request.send(controller='bulk_operation', action='stop', request_data=params)

    def do_get_bulk_operation(self, batch_id: str) -> str:
        """
        Get bulk operation
        """
        params = {"batch_id": batch_id}
        return self.request.send(controller='bulk_operation', action='get', request_data=params)

    def do_delete_bulk_operation(self, batch_id: str) -> str:
        """
        Delete bulk operation
        """
        params = {"batch_id": batch_id}
        return self.request.send(controller='bulk_operation', action='delete', request_data=params)

    def get_xpayments_web_location(self) -> str:
        """
        Get web location of the X-Payments Cloud instance
        """
        return f"https://{self.request.get_server_host()}/"

    def get_admin_url(self) -> str:
        """
        Get admin backend URL of the X-Payments Cloud instance
        """
        return f"{self.get_xpayments_web_location()}admin.php"

    def get_payment_url(self) -> str:
        """
        Get payment URL of the X-Payments Cloud instance
        """
        return f"{self.get_xpayments_web_location()}payment.php"
