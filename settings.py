import os
from google.appengine.api import app_identity


USER_REGISTER = False
APP_IS_LOCAL = False
FB_APP_ID = ""
CURRENT_URL = str(os.environ.get('wsgi.url_scheme'))
CURRENT_URL += "://"+str(os.environ.get('HTTP_HOST'))+"/"

if 'staging' in app_identity.get_application_id() \
   or "localhost" in CURRENT_URL:
    APP_IS_STAGING = True
else:
    APP_IS_STAGING = False

if 'localhost' in CURRENT_URL:
    APP_IS_LOCAL = True
    COOKIE_PARENT_DOMAIN = 'localhost'
elif APP_IS_STAGING:
    COOKIE_PARENT_DOMAIN = '.appspot.com'
else:
    COOKIE_PARENT_DOMAIN = '.appspot.com'

LOGIN_KEY = "nzqvu1PvpN3iBsPrKM9Pe07DAto3GpUfWDa12Z80g12vs3iwsc4pEAnvN9lILhTBOQbwYYJtwrOK0A639Glj9agL0tBAhKGllY9sO4CrGsj6m0D6bzidk7VKe9eHv6Oz"
MANDRILL_API_KEY = ""
MANDRILL_API_BASE_ENDPOINT = "https://mandrillapp.com/api/1.0/"
MANDRILL_SENDER = "email@example.com"

DEPARTMENTS = [
    {"name": "Department 1", "code": "D1"},
    {"name": "Department 2", "code": "D2"},
    {"name": "Department 3", "code": "D3"},
    {"name": "Department 4", "code": "D4"},
    {"name": "Department 5", "code": "D5"},
    {"name": "Department 6", "code": "D6"},
    {"name": "Department 7", "code": "D7"},
    {"name": "Department 8", "code": "D8"},
    {"name": "Department 9", "code": "D9"},
    {"name": "Department 10", "code": "D10"},
    {"name": "Department 11", "code": "D11"},
    {"name": "Department 12", "code": "D12"},
    {"name": "Department 13", "code": "D13"},
    {"name": "Department 14", "code": "D14"},
    {"name": "Department 15", "code": "D15"},
    {"name": "Department 16", "code": "D16"},
    {"name": "Department 17", "code": "D17"},
    {"name": "Department 18", "code": "D18"},
    {"name": "Department 19", "code": "D19"},
    {"name": "Department 20", "code": "D20"},


]

LICENSE = [
    {"code": "cc-by", "name": "Creative Commons Attribution"},
    {"code": "cc-by-sa", "name": "Creative Commons Attribution Share-Alike"},
    {"code": "cc-zero", "name": "Creative Commons CCZero"},
    {"code": "cc-nc", "name": "Creative Commons Non-Commercial (Any)"},
    {"code": "gfdl", "name": "GNU Free Documentation License"},
    {"code": "notspecified", "name": "License not specified"},
    {"code": "odc-by", "name": "Open Data Commons Attribution License"},
    {"code": "odc-odbl", "name": "Open Data Commons Open Database License (ODbL)"},
    {"code": "odc-pddl", "name": "Open Data Commons Public Domain Dedication and License (PDDL)"},
    {"code": "other-at", "name": "Other (Attribution)"},
    {"code": "other-nc", "name": "Other (Non-Commercial)"},
    {"code": "other-closed", "name": "Other (Not Open)"},
    {"code": "other-open", "name": "Other (Open)"},
    {"code": "other-pd", "name": "Other (Public Domain)"},
    {"code": "uk-ogl", "name": "Open Government Licence (OGL)"}
]

RESPONSE = {
    "response": "UNKNOWN",
    "description": "",
    "code": 200,
}

CKAN_API_KEY = ""
