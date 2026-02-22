import logging
from functools import wraps

import httpx
from flask import jsonify, make_response

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def jsonify_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = make_response(jsonify(func(*args, **kwargs)))
        response.headers["Content-Type"] = "application/json"
        return response

    return wrapper


def get_address_ip():
    try:
        url = "https://api64.ipify.org?format=json"
        with httpx.Client() as client:
            response_data = client.get(url).json()

        ip = response_data.get("ip")
        logger.info(f"IP address: {ip})")
        if not ip or not isinstance(ip, str):
            raise ValueError("Invalid IP address")
        return ip
    except (httpx.RequestError, ValueError) as error:
        logger.debug(f"Unable to obtain IP address: {error})")
        return None


def get_country_code():
    try:
        ip_address = get_address_ip()
        if not ip_address:
            return None
        url = f"https://ipapi.co/{ip_address}/json/"
        with httpx.Client() as client:
            response_data = client.get(url).json()
            logger.info(f"Data : {response_data})")

        country_code = response_data.get("country_code")
        if not country_code or not isinstance(country_code, str):
            raise ValueError("Invalid country code")
        return country_code
    except (httpx.RequestError, ValueError) as error:
        logger.debug(f"Unable to obtain the country code: {error})")
        return None


def formatted_number(obj):
    number = "{:,.0f}".format(obj)
    return number.replace(",", " ")
