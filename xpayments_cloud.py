#!/usr/bin/env python3
# coding: utf-8
import inspect
import requests
import hmac
import hashlib
import binascii
import base64
import json
import os

XPAYMENTS_SDK_DEBUG_SERVER_HOST = ""

class Request:

    XP_DOMAIN = "xpayments.com"
    API_VERSION = "4.8"
    connection_timeout = 120
    account = ""
    api_key = ""
    secret_key = ""

    def __init__(self, account, api_key, secret_key):
        """
        Request constructor

        Parameters
        ----------
        account: str
        api_key: str
        secret_key: str                    
        """
        self.account = account
        self.api_key = api_key
        self.secret_key = secret_key

    def send(self, controller, action, request_data):
        """
        Send API request to X-Payments Cloud

        Parameters
        ----------
        controller: str
        action: str
        request_data: list

        Returns
        -------
        str
        """

        request_data = json.dumps(request_data)

        url = self.get_api_endpoint(action, controller)

        headers = {
            "Authorization": "Basic " + self.get_authorization_header(),
            "X-Payments-Signature": self.get_signature_header(action, request_data),
            "Content-Type": "application/json",
        }

        response = requests.post(url, data=request_data, headers=headers, timeout=self.connection_timeout)

        response.raise_for_status()

        print(response.json())

    def get_authorization_header(self):
        """
        Get Basic HTTP Authorization header

        Returns
        -------
        str
        """

        data = "%s:%s" % (self.account, self.api_key)
        return base64.b64encode(data.encode()).decode()

    def get_signature_header(self, action, data):
        """
        Get signature header

        Parameters
        ----------
        action: str
        data: str

        Returns
        -------
        str
        """

        message = action + data

        return hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()

    def get_server_host(self):
        """
        Get X-Payments server host

        Returns
        -------
        str
        """
        if XPAYMENTS_SDK_DEBUG_SERVER_HOST:
            return XPAYMENTS_SDK_DEBUG_SERVER_HOST
        else:
            return self.account + "." + self.XP_DOMAIN

    def get_api_endpoint(self, action, controller):
        """
        Get API endpoint

        Parameters
        ----------
        action: str
        controller: str

        Returns
        -------
        str
        """
        return "https://" + self.get_server_host() + "/api/" + self.API_VERSION + "/" + controller + "/" + action

class Client:
    account = ""
    api_key = ""
    secret_key = ""

    def __init__(self, account, api_key, secret_key):
        """
        Client constructor

        Parameters
        ----------
        account: str
        api_key: str
        secret_key: str                    
        """
        self.account = account
        self.api_key = api_key
        self.secret_key = secret_key

    def do_pay(self, token, ref_id, customer_id, cart, return_url, callback_url, force_save_card=None, force_transaction_type=None, force_conf_id=0):
        """
        Processs payment

        Parameters
        ----------
        token: str
        ref_id: str
        customer_id: str
        cart: list
        return_url: str
        callback_url: str
        force_save_card: str, optional
        force_transaction_type: str, optional
        force_conf_id: str, optional

        Returns
        -------
        list
        """

        params = {
            "token": token,
            "refId": ref_id,
            "customerId": customer_id,
            "cart": cart,
            "returnUrl": return_url,
            "callbackUrl": callback_url
        }

        if force_save_card:
            params["force_save_card"] = "Y"
        else:
            params["force_save_card"] = "N"

        if force_transaction_type:
            params["force_transaction_type"] = force_transaction_type

        if force_conf_id:
            params["confId"] = force_conf_id

        request = Request(self.account, self.api_key, self.secret_key)

        return request.send('payment', 'pay', params)

    def do_tokenize_card(self, token, ref_id, customer_id, cart, return_url, callback_url, force_conf_id=0):
        """
        Tokenize card

        Parameters
        ----------
        token: str
        ref_id: str
        customer_id: str
        cart: list
        return_url: str
        callback_url: str
        force_conf_id: str, optional

        Returns
        -------
        list
        """

        params = {
            "token": token,
            "refId": ref_id,
            "customerId": customer_id,
            "cart": cart,
            "returnUrl": return_url,
            "callbackUrl": callback_url
        }

        if force_conf_id:
            params["confId"] = force_conf_id

        request = Request(self.account, self.api_key, self.secret_key)

        return request.send('payment', 'tokenize_card', params)

    def do_rebill(self, xpid, ref_id, customer_id, cart, callback_url):
        """
        Rebill payment (process payment using the saved card)

        Parameters
        ----------
        xpid: str
        ref_id: str
        customer_id: str
        cart: list
        callback_url: str

        Returns
        -------
        list
        """

        params = {
            "xpid": xpid,
            "refId": ref_id,
            "customerId": customer_id,
            "cart": cart,
            "callbackUrl": callback_url
        }

        request = Request(self.account, self.api_key, self.secret_key)

        return request.send('payment', 'rebill', params)

    def do_action(self, action, xpid, amount=0):
        """
        Execute secondary payment action

        Parameters
        ----------
        action: str
            Payment action
        xpid: str
            X-Payments payment ID
        amount: str, optional
            Amount to capture

        Returns
        -------
        list
        """

        params = {"xpid": xpid}
        if 0 < amount:
            params.amount = amount

        request = Request(self.account, self.api_key, self.secret_key)

        return request.send('payment', action, params)

    def do_capture(self, xpid, amount=0):
        """
        Capture payment

        Parameters
        ----------
        xpid: str
            X-Payments payment ID
        amount: str, optional
            Amount to capture

        Returns
        -------
        list
        """

        return self.do_action("capture", xpid, amount)

    def do_void(self, xpid, amount=0):
        """
        Void payment

        Parameters
        ----------
        xpid: str
            X-Payments payment ID
        amount: str, optional
            Amount to void

        Returns
        -------
        list
        """

        return self.do_action("void", xpid, amount)

    def do_refund(self, xpid, amount=0):
        """
        Refund payment

        Parameters
        ----------
        xpid: str
            X-Payments payment ID
        amount: str, optional
            Amount to refund

        Returns
        -------
        list
        """

        return self.do_action("refund", xpid, amount)

    def do_continue(self, xpid):
        """
        Continue payment

        Parameters
        ----------
        xpid: str
            X-Payments payment ID

        Returns
        -------
        list
        """

        return self.do_action("continue", xpid)

    def do_accept(self, xpid):
        """
        Accept payment

        Parameters
        ----------
        xpid: str
            X-Payments payment ID

        Returns
        -------
        list
        """

        return self.do_action("accept", xpid)

    def do_decline(self, xpid):
        """
        Decline payment

        Parameters
        ----------
        xpid: str
            X-Payments payment ID

        Returns
        -------
        list
        """

        return self.do_action("decline", xpid)

    def do_get_info(self, xpid):
        """
        Get detailed payment information

        Parameters
        ----------
        xpid: str
            X-Payments payment ID

        Returns
        -------
        list
        """

        return self.do_action("get_info", xpid)

    def do_get_customer_cards(self, customer_id, status="any"):
        """
        Get customer's cards

        Parameters
        ----------
        customer_id: str
            X-Payments customer ID
        status: str
            Status of the cards, "any" or "active"

        Returns
        -------
        list
        """

        params = {
            "customerId": customer_id,
            "status": status
        }

        request = Request(self.account, self.api_key, self.secret_key)

        return request.send('customer', 'get_cards', params)

    def do_add_bulk_operation(self, operation, xpids):
        """
        Add bulk operation

        Parameters
        ----------
        operation: str
            Bulk operation type
        xpids: dict
            List of X-Payments payments ID's

        Returns
        -------
        list
        """

        params = {
            'operation': operation,
            'payments': [],
        }

        for xpid in xpids:
            params['payments'].append({'xpid': xpid})

        request = Request(self.account, self.api_key, self.secret_key)

        return request.send('bulk_operation', 'add', params)

    def do_start_bulk_operation(self, batch_id):
        """
        Start bulk operation

        Parameters
        ----------
        batch_id: str
            Bulk operation ID

        Returns
        -------
        list
        """

        params = {'batch_id': batch_id}

        request = Request(self.account, self.api_key, self.secret_key)

        return request.send('bulk_operation', 'start', params)

    def do_stop_bulk_operation(self, batch_id):
        """
        Stop bulk operation

        Parameters
        ----------
        batch_id: str
            Bulk operation ID

        Returns
        -------
        list
        """

        params = {'batch_id': batch_id}

        request = Request(self.account, self.api_key, self.secret_key)

        return request.send('bulk_operation', 'stop', params)

    def do_get_bulk_operation(self, batch_id):
        """
        Get bulk operation

        Parameters
        ----------
        batch_id: str
            Bulk operation ID

        Returns
        -------
        list
        """

        params = {'batch_id': batch_id}

        request = Request(self.account, self.api_key, self.secret_key)

        return request.send('bulk_operation', 'get', params)

    def do_delete_bulk_operation(self, batch_id):
        """
        Delete bulk operation

        Parameters
        ----------
        batch_id: str
            Bulk operation ID

        Returns
        -------
        list
        """

        params = {'batch_id': batch_id}

        request = Request(self.account, self.api_key, self.secret_key)

        return request.send('bulk_operation', 'delete', params)

    def get_xpayments_web_location(self):
        """
        Get web location of the X-Payments Cloud instance

        Returns
        -------
        str
        """
        if XPAYMENTS_SDK_DEBUG_SERVER_HOST:
            host = XPAYMENTS_SDK_DEBUG_SERVER_HOST
        else:
            host = self.account + "." + self.XP_DOMAIN
        return "https://" + host + "/"

    def get_admin_url(self):
        """
        Get admin backend URL of the X-Payments Cloud instance

        Returns
        -------
        str
        """

        return self.get_xpayments_web_location() + "admin.php"

    def get_payment_url(self):
        """
        Get payment URL of the X-Payments Cloud instance

        Returns
        -------
        str
        """

        return self.get_xpayments_web_location() + "payment.php"
