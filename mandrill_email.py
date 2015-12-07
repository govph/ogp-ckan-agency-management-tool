import os
import json
import jinja2
import logging
import datetime
from request import global_vars
from settings import MANDRILL_API_KEY, MANDRILL_SENDER
from settings import CURRENT_URL, MANDRILL_API_BASE_ENDPOINT
from google.appengine.api import urlfetch

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True)


def send_email(receiver_name=False, receiver_email=False, subject=False,
               content={}, email_type=False, many_receiver=False):

    if not subject or not email_type:
        return False

    data = {}
    data['type'] = email_type
    data['current_url'] = CURRENT_URL
    data['email_content'] = content
    data['receiver_name'] = receiver_name
    data['receiver_email'] = receiver_email
    data["footer_year"] = global_vars.datetime_now_adjusted.strftime("%Y")
    template = jinja_environment.get_template('frontend/email-template.html')
    content['date'] = datetime.datetime.utcnow().strftime('%B %d, %Y %H:%M:%S')

    if receiver_name and receiver_email:
        receiver = [{"email": receiver_email, "name": receiver_name}]
    else:
        receiver = []

    if many_receiver:
        for r in many_receiver:
            data['receiver_name'] = r['name']
            send_via_mandrill(
                receiver=[{"email": r['email'], "name": r['name']}],
                subject=subject, html=template.render(data),
                plain_text=None, email_type=email_type)

        return True

    send_via_mandrill(
        receiver=receiver, subject=subject,
        html=template.render(data), plain_text=None, email_type=email_type)

    return True


def send_via_mandrill(receiver, subject, html=None,
                      plain_text=None, email_type=None):
    data = {
        "key": MANDRILL_API_KEY,
        "message": {
            "html": html,
            "subject": subject,
            "from_email": MANDRILL_SENDER,
            "from_name": "Open Data Network",
            "to": receiver,
            "headers": {
                "Reply-To": MANDRILL_SENDER
            },
            "tags": [
                "notifications",
                email_type
            ],
            "important": True,
            "track_opens": True,
            "track_clicks": True,
            "auto_text": True
        },
        "async": False
    }

    response = urlfetch.fetch(
        url=MANDRILL_API_BASE_ENDPOINT + "messages/send.json",
        method=urlfetch.POST, payload=json.dumps(data), deadline=30)

    logging.debug(response.content)
