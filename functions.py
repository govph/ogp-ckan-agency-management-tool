import os
import json
import uuid
import hmac
import base64
import urllib
import string
import base64
import hashlib
import logging
import random
import datetime
from cookie import *


def hp(email, password):
    """
        Creates a hashed password.
    """
    pepper = "gbvPzkyK177wjSpuJgESD10ZpultupddSOsegroWNqo6iff1AaeS0aDXpBgcAUEOs3FTU9L5lOKQ9OGQu9Hxb0Y5S4HW6GNldhY5orVkS0H1n4VQ8yM3j3KgW0Ai5UIZ"
    i = email + password + pepper
    return base64.b64encode(hashlib.sha1(i).digest())
    # return hashlib.sha1(i).digest()


def generate_token():
    """
        Generates a random token.
    """
    token = ""
    for x in range(128):
        random_str = string.ascii_uppercase + string.digits
        random_str += string.lowercase
        token += random.choice(random_str)

    return token


def random_string(n):
    """
        Generates a random string.
    """
    random_str = ""
    for x in range(n):
        rand = string.ascii_letters + string.digits
        random_str += random.choice(rand)

    return random_str


def get_login_url(url, error=None):
    """
        Creates the login url with redirect.
    """
    login_url = "/login"
    if url:
        login_url = login_url + "?redirect=" + urllib.quote(url.strip())

    if error:
        if url:
            login_url = login_url + "&error=" + urllib.quote(error)
        else:
            login_url = login_url + "?error=" + urllib.quote(error)

    return login_url


def error_message(self, message):
    """
        Creates a success message.
    """
    error = base64.b64encode(message)
    set_cookie(self, name="_erm_", value=error)


def success_message(self, message):
    """
        Creates an error message.
    """
    success = base64.b64encode(message)
    set_cookie(self, name="_scm_", value=success)


def wrap_response(res, response):
    if "code" in response:
        try:
            response_code = int(response['code'])
            if response_code >= 400 and response_code <= 499:
                if response_code == 404:
                    res.response.set_status(404, response["response"])
                else:
                    res.response.set_status(400, response["response"])

            elif response_code >= 500 and response_code <= 599:
                res.response.set_status(500, response["response"])
            else:
                res.response.set_status(response_code, response["response"])
        except:
            logging.exception("Cannot set Status Code Header")

    res.response.headers['Content-Type'] = "application/json"
    response_text = json.dumps(response, False, False)
    res.response.out.write(response_text)
    logging.debug("RESPONSE:")
    logging.debug(response_text)
    return


def create_indexed_tag(key, value):
    """
        Creates a tag for the api.
    """
    key = key.upper()
    key = key.replace("INDEXED_", "")
    key = key.replace("UNINDEXED_", "")
    return "->".join([key, value]).upper()


def uniquify(seq, idfun=None):
    """
        Removes duplicate items in the list.
    """
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


def to_date_format_only(date, format):
    """
        Converts date to a desired format.
    """
    date = datetime.datetime.strptime(date, "%b %d, %Y %I:%M:%S %p")
    return date.strftime(format)


def create_tags(title):
    """
        Creates a tags used for search.
    """
    title = title.strip().upper()
    title_list = title.split()
    tags = []

    title_length = len(title_list) + 1

    for x in range(0, title_length):
        for i in range(0, title_length):
            tags.append(" ".join(title_list[x:i]))

    return uniquify(tags)


def hexto62(x):
    x = int(x, 16)
    base = 62
    digs = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if x < 0:
        sign = -1
    elif x == 0:
        return '0'
    else:
        sign = 1
    x *= sign
    digits = []
    while x:
        digits.append(digs[x % base])
        x /= base
    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)


def generate_uuid():
    uu_id = str(uuid.uuid4()).replace("-", "")
    uu_id += str(uuid.uuid4()).replace("-", "")
    return hexto62(uu_id)


def generate_signature(secret_key, data):
    try:
        signature = hmac.new(secret_key, msg=data, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(signature).decode()
        return signature
    except Exception, e:
        logging.exception(e)
        raise CannotGenerateSignature()
