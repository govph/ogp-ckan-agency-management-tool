#!/usr/bin/env python
import os
import time
import base64
import jinja2
import urllib
import urllib2
import webapp2
import logging
import datetime
import threading
import cloudstorage as gcs
from mandrill_email import *
from webapp2_extras import routes
from request import global_vars
from models import *
from cookie import *
from settings import *
from decorators import *
# from decorator import *
from functions import *
# from transactional import *
from sessions import SessionHandler, force_logout
from google.appengine.api import images, urlfetch
from google.appengine.ext import blobstore
from google.appengine.datastore.datastore_query import Cursor

this_thread = threading.local()
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True)
jinja_environment.filters['to_date_format_only'] = to_date_format_only


class BaseHandler(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        self.initialize(request, response)
        self.tv = {}
        self.tv["user"] = None
        self.tv["local"] = APP_IS_LOCAL
        self.tv["show_breadcrumb"] = True
        self.tv["show_add_dataset"] = True

        self.user = None
        self.GET = self.request.get
        self.POST = self.request.POST.get

        try:
            self.user = SessionHandler().owner
        except Exception, e:
            self.user = None

        if self.user:
            self.tv["user"] = self.user.to_object()

        if get_cookie(self, name="_erm_"):
            self.tv["error"] = base64.b64decode(get_cookie(self, name="_erm_"))
            clear_cookie(self, name="_erm_")

        if get_cookie(self, name="_scm_"):
            success = base64.b64decode(get_cookie(self, name="_scm_"))
            self.tv["success"] = success
            clear_cookie(self, name="_scm_")

        # self.response.write('Hello world!')

    def render(self, template_path=None, force=False):
        self.tv["current_timestamp"] = time.mktime(
            datetime.datetime.now().timetuple())
        current_time = global_vars.datetime_now_adjusted
        self.tv["current_time"] = current_time
        self.tv["footer_year"] = current_time.strftime("%Y")

        if self.request.get('json') or not template_path:
            self.response.out.write(simplejson.dumps(self.tv))
            return

        template = jinja_environment.get_template(template_path)
        self.response.out.write(template.render(self.tv))


class MainHandler(BaseHandler):
    def get(self):
        """
            Handles the / endpoint.
            Shows the landing page.
        """
        self.redirect("/login")
        # self.render("frontend/main.html")


class LoginHandler(BaseHandler):
    def get(self):
        """
            Handles the /login endpoint
        """
        self.tv["FB_APP_ID"] = FB_APP_ID
        if self.user:
            self.redirect("/dashboard")
        else:
            if self.GET("redirect"):
                self.tv["redirect"] = self.GET("redirect")

            self.render("frontend/login.html")

    def post(self):
        """
            Handles the /login endpoint.
            Logs in users.
        """
        if self.POST("email") and self.POST("password"):
            url = "/login"
            redirect = None
            email = self.POST("email").strip().lower()
            query = User.query()
            query = query.filter(User.current_email == email)
            user = query.get()

            if self.POST("redirect"):
                redirect = urllib.quote(self.POST("redirect"))

            if not user:
                error = "Invalid email or password."
                error_message(self, error)
                if redirect:
                    url += "?redirect=" + str(redirect)

                self.redirect(url)
                return

            password = hp(email=email, password=self.POST("password"))
            if user.password != password:
                error = "Invalid email or password."
                error_message(self, error)
                if redirect:
                    url += "?redirect=" + str(redirect)

                self.redirect(url)
                return

            if user.status == "PENDING":
                error = "Your account has not been verified. "
                error += "Please verify your account by opening the "
                error += "verification email we sent you. "
                error_message(self, error)
                if redirect:
                    url += "?redirect=" + str(redirect)

                self.redirect(url)
                return

            if user.role == "AGENCYADMIN":
                if user.status == "VERIFIED":
                    error = "Your account is still pending approval. "
                    error += "Once your account is approved, you will be able "
                    error += "to login. You will receive an email once your "
                    error += "account is approved."
                    error_message(self, error)
                    self.redirect(url)
                    return

                if user.status == "DISAPPROVED":
                    error = "Your account has been disapproved. "
                    error += "Please contact the Open Data Team."
                    error_message(self, error)
                    self.redirect(url)
                    return

            session = SessionHandler(user)
            session.login()
            if self.POST("redirect"):
                self.redirect(str(self.POST("redirect")))
            else:
                self.redirect("/dashboard")
            return

        error = "Please enter your email and password."
        error_message(self, error)
        self.redirect("/login")


class LoginOauthHandler(BaseHandler):
    def get(self):
        self.tv["FB_APP_ID"] = FB_APP_ID
        if self.user:
            if self.GET("r"):
                self.redirect(str(urllib.unquote(self.GET("r"))))
            else:
                self.redirect(self.request.referer)
            return
        else:
            if self.GET("r"):
                self.tv["redirect"] = self.GET("r")
            else:
                self.tv["redirect"] = self.request.referer

            self.render("frontend/login.html")

    def post(self):
        """
            Handles the /login endpoint.
            Logs in users.
        """
        url = "/login/authorize"
        if self.POST("email") and self.POST("password"):
            redirect = None
            email = self.POST("email").strip().lower()
            query = User.query()
            query = query.filter(User.current_email == email)
            user = query.get()

            if self.POST("redirect"):
                redirect = urllib.quote(self.POST("redirect"))

            if not user:
                error = "Invalid email or password."
                error_message(self, error)
                if redirect:
                    url += "?r=" + str(redirect)

                self.redirect(url)
                return

            password = hp(email=email, password=self.POST("password"))
            if user.password != password:
                error = "Invalid email or password."
                error_message(self, error)
                if redirect:
                    url += "?r=" + str(redirect)

                self.redirect(url)
                return

            if user.status == "PENDING":
                error = "Your account has not been verified. "
                error += "Please verify your account by opening the "
                error += "verification email we sent you. "
                error_message(self, error)
                if redirect:
                    url += "?r=" + str(redirect)

                self.redirect(url)
                return

            if user.role == "AGENCYADMIN":
                if user.status == "VERIFIED":
                    error = "Your account is still pending approval. "
                    error += "Once your account is approved, you will be able "
                    error += "to login. You will receive an email once your "
                    error += "account is approved."
                    error_message(self, error)
                    self.redirect(url)
                    return

                if user.status == "DISAPPROVED":
                    error = "Your account has been disapproved. "
                    error += "Please contact the Open Data Team."
                    error_message(self, error)
                    self.redirect(url)
                    return

            session = SessionHandler(user)
            session.login()
            code = session.generate_login_code()

            if self.POST("redirect"):
                url = str(urllib.unquote(self.POST("redirect")))
            else:
                url = self.request.referer

            url += "?code=" + code
            self.redirect(url)
            return

        error = "Please enter your email and password."
        error_message(self, error)
        self.redirect(url)

class VerifyLoginCode(BaseHandler):
    def post(self, code=None):
        response = RESPONSE.copy()
        if not code:
            response["response"] = "MissingParameters"
            response["description"] = "There is/are missing parameters in the request."
            response["code"] = 463

        if "X-Signature" in self.request.headers:
            c_sig = self.request.headers['X-Signature']
            s_data = "POST&" + str(urllib.quote(self.request.uri)) + "&" + str(urllib.quote(self.request.body))
            s_sig = generate_signature(LOGIN_KEY, s_data)
            logging.info("v: " + s_sig)
            if c_sig == s_sig:
                try:
                    body = json.loads(self.request.body)
                except:
                    response["response"] = "InvalidJSONFormat"
                    response["description"] = "The body seems to be not in JSON format."
                    response["code"] = 406
                else:
                    if "nonce" in body and "timestamp" in body:
                        new = False
                        nn = Nonce.get_by_id(body["nonce"])
                        if nn:
                            if (((int(time.mktime(self.datenow.timetuple())) - int(nn.timestamp))/60)/60) <= 10:
                                new = True
                            else:
                                response["response"] = "RequestExpired"
                                response["description"] = "This request seems to be expired already"
                                response["code"] = 464
                        else:
                            n = Nonce(id=body["nonce"])
                            n.nonce = body["nonce"]
                            n.timestamp = int(body["timestamp"])
                            n.put()
                            new = True

                        if new:
                            logincode = LoginCode.get_by_id(str(code))
                            if logincode:
                                s = logincode.session.get()
                                if s.expires >= datetime.datetime.now():
                                    user = s.owner.get()
                                    if user:
                                        t_id = generate_uuid() + generate_uuid()
                                        token = Token(id=t_id)
                                        token.token = t_id
                                        token.session = s.key
                                        token.token_type = "api"
                                        token.put()
                                        response = user.to_object(token=t_id)
                                        response["response"] = "Successful"
                                        response["expires"] = time.mktime(s.expires.timetuple())
                                        response["code"] = 200
                                    else:
                                        s.status = False
                                        s.put()
                                        response["response"] = "UserUnavailable"
                                        response["description"] = "This user seems to be unavailble"
                                        response["code"] = 404
                                else:
                                    response["response"] = "SessionExpired"
                                    response["description"] = "This session seems to be expired already"
                                    response["code"] = 465
                            else:
                                response["response"] = "LoginCodeDoesNotExist"
                                response["description"] = "This login code does not exist."
                                response["code"] = 404
                    else:
                        response["response"] = "MissingParameters"
                        response["description"] = "There is/are missing parameters in the request."
                        response["code"] = 463
            else:
                response["response"] = "InvalidSignature"
                response["description"] = "The request signature is invalid or has been tampered."
                response["code"] = 460
        else:
            response["response"] = "MissingParameters"
            response["description"] = "There is/are missing parameters in the request."
            response["code"] = 463

        wrap_response(self,response)

    def get(self, appid=None, code=None):
        response = RESPONSE.copy()
        response["response"] = "UnsupportedMethodError"
        response["description"] = "The GET method is not supported for this endpoint. Use POST instead."
        response["code"] = 405
        wrap_response(self,response)

    def put(self, appid=None, code=None):
        response = RESPONSE.copy()
        response["response"] = "UnsupportedMethodError"
        response["description"] = "The PUT method is not supported for this endpoint. Use POST instead."
        response["code"] = 405
        wrap_response(self,response)

    def delete(self, appid=None, code=None):
        response = RESPONSE.copy()
        response["response"] = "UnsupportedMethodError"
        response["description"] = "The DELETE method is not supported for this endpoint. Use POST instead."
        response["code"] = 405
        wrap_response(self,response)


class LogoutHandler(BaseHandler):
    @login_required
    def get(self):
        """
            Handles the /logout endpoint.
            Logs out users.
        """
        session = SessionHandler()
        session.logout()
        success = "You have logged out successfully!"
        success_message(self, success)
        self.redirect("/login")


class RegisterHandler(BaseHandler):
    def get(self):
        """
            Handles the /register endpoint.
            ODTF registration.
        """
        if self.user:
            self.redirect("/dashboard")
        else:
            if USER_REGISTER:
                self.render("frontend/register.html")
            else:
                self.redirect("/admin/register")

    def post(self):
        """
            Handles the /register endpoint.
            ODTF registration.
        """
        if self.POST("first_name") and self.POST("last_name") \
           and self.POST("email"):
            user_exist = User.check_user(email=self.POST("email"))
            if user_exist:
                message = "Sorry, it looks like "
                message += self.POST("email")
                message += " belongs to an existing account."
                error_message(self, message)
            else:
                user = User.create_new_user(
                    first_name=self.POST("first_name"),
                    middle_name=self.POST("middle_name"),
                    last_name=self.POST("last_name"),
                    password=self.POST("password"),
                    mobile=self.POST("mobile_number"),
                    email=self.POST("email"))

                success = "Thank you for your registration. "
                success += "We sent you a verification email, "
                success += "please open the email and verify your account "
                success += "to complete the registration."
                success_message(self, success)

        self.redirect("/register")


class AgencyAdminRegistrationHandler(BaseHandler):
    @allowed_users(["OPENDATAADMIN"])
    def get(self):
        """
            Handles the /admin/register endpoint.
            Agency Admin registration.
        """
        self.tv["breadcrumb"] = [
            {
                "name": "AGENCY ADMIN REGISTRATION",
                "link": "/agency/admins"
            }
        ]
        if self.GET("ajax"):
            n = 50
            if self.GET("n"):
                n = int(self.GET("n"))

            query = User.query()
            query = query.filter(User.role == "AGENCYADMIN")

            if self.GET("status"):
                query = query.filter(User.status == self.GET("status").upper())

            if self.GET("cursor"):
                curs = Cursor(urlsafe=self.GET("cursor"))
                users, cursor, more = query.fetch_page(n, start_cursor=curs)
            else:
                users, cursor, more = query.fetch_page(n)

            response = {}
            response["users"] = []

            if users:
                for user in users:
                    response["users"].append(user.to_approval_object())

            wrap_response(self, response)
        else:
            self.render("frontend/register-approve.html")

    @allowed_users(["OPENDATAADMIN"])
    def post(self):
        """
            Handles the /admin/register endpoint.
            Agency Admin registration.
        """
        if self.POST("agency_admin_id") and self.POST("action"):
            user = User.get_by_id(int(self.POST("agency_admin_id")))
            if user:
                if self.POST("action") == "approve":
                    user.approved_by_name = " ".join(
                        [self.user.first_name, self.user.last_name])
                    user.approved_by_key = self.user.key
                    user.approved_on = datetime.datetime.now()
                    user.status = "APPROVED"

                    send_email(
                        receiver_name=user.first_name,
                        receiver_email=user.current_email,
                        subject="Account Approved",
                        content={},
                        email_type="approve_account")
                elif self.POST("action") == "disapprove":
                    user.status = "DISAPPROVED"
                    user.disapproved_on = datetime.datetime.now()
                    user.disapproved_by_name = " ".join(
                        [self.user.first_name, self.user.last_name])
                    user.disapproved_by_key = self.user.key
                else:
                    wrap_response(self, {"status": "error"})
                    return

                user.put()
                wrap_response(self, {"status": "ok"})
                return

        wrap_response(self, {"status": "error"})


class AdminRegisterHandler(BaseHandler):
    def get(self):
        if self.user:
            self.redirect("/dashboard")
        else:
            self.render("frontend/register-admin.html")

    def post(self):
        if self.POST("salutation") and self.POST("first_name") \
           and self.POST("last_name") and self.POST("email") \
           and self.POST("email") and self.POST("department") \
           and self.POST("agency") and self.POST("region") \
           and self.POST("operating_unit") and self.POST("designation"):
            # user_exist = User.check_user(email=self.POST("email"))
            # if user_exist:
            #     if user_exist.role == "OPENDATAADMIN" \
            #        and user_exist.status == "INVITE":
            #         user = User.complete_opendata_admin_registration(
            #             user=user_exist.key,
            #             first_name=self.POST("first_name"),
            #             last_name=self.POST("last_name"),
            #             password=self.POST("password"),
            #             mobile=self.POST("mobile_number"))

            #         success = "Thank you for your registration. "
            #         success += "You can now login."
            #         success_message(self, success)
            #         self.redirect("/login")
            #         return
            #     else:
            #         message = "Sorry, it looks like "
            #         message += self.POST("email")
            #         message += " belongs to an existing account."
            #         error_message(self, message)
            # else:
            user = User.create_new_user(
                salutation=self.POST("salutation"),  # REQUIRED
                first_name=self.POST("first_name"),  # REQUIRED
                last_name=self.POST("last_name"),  # REQUIRED
                password=self.POST("password"),  # REQUIRED
                email=self.POST("email"),  # REQUIRED
                department=self.POST("department"),
                agency=self.POST("agency"),
                region=self.POST("region"),
                operating_unit=self.POST("operating_unit").split("->")[0],
                uacs=self.POST("operating_unit").split("->")[1],
                role="AGENCYADMIN",
                middle_name=self.POST("middle_name"),
                mobile=self.POST("mobile_number"),
                designation=self.POST("designation"))

            success = "Thank you for your registration. "
            success += "We sent you a verification email, "
            success += "please open the email and verify your account "
            success += "to complete the registration."
            success_message(self, success)
        elif self.POST("f_name") and self.POST("l_name") and self.POST("password") and self.POST("token") and self.POST("uid"):
            user = User.get_by_id(int(self.POST("uid")))
            if user:
                password = hp(user.original_email, self.POST("password"))
                user.first_name = self.POST("f_name").strip()
                user.last_name = self.POST("l_name").strip()
                user.name = " ".join([user.first_name, user.last_name])
                user.mobile_number = self.POST("mobile_number")
                user.previous_passwords.append(password)
                user.password = password
                user.status = "VERIFIED"
                user.put()

                session = SessionHandler(user)
                session.login()

                success = "Your account has been saved."
                success_message(self, success)
                self.redirect("/dashboard")
                return
            else:
                error = "Sorry, we could not process your request."
                error_message(self, error)
        else:
            error = "Please fill all required fields."
            success_message(self, error)

        self.redirect("/admin/register")


class LogsHandler(BaseHandler):
    @allowed_users(["OPENDATAADMIN", "AGENCYADMIN"])
    def get(self):
        """
            Handles the /logs endpoint.
            Logs the user activity.
        """
        response = {}
        response["logs"] = []

        query = Logs.query()
        query = query.order(-Logs.created_time)
        if self.user.role == "AGENCYADMIN":
            query = query.filter(Logs.uacs_id == self.user.uacs)

        if self.GET("dataset_id"):
            dataset_key = ndb.Key("APIData", int(self.GET("dataset_id")))
            query = query.filter(Logs.dataset == dataset_key)

        logs = query.fetch(20)
        if logs:
            for l in logs:
                try:
                    response["logs"].append(l.to_object())
                except Exception, e:
                    logging.exception(e)

        wrap_response(self, response)


class VerifyRegisterHandler(BaseHandler):
    def get(self):
        """
            Handles the /register/verify endpoint.
            Verifies user registration.
        """
        if self.user:
            self.redirect("/dashboard")
        else:
            if self.GET("token") and self.GET("uid"):
                user = User.get_by_id(int(self.GET("uid")))
                if user:
                    if user.status == "PENDING":
                        if user.confirmation_token == self.GET("token"):
                            user.status = "VERIFIED"
                            user.put()

                            if user.role == "AGENCYADMIN":
                                send_email(
                                    receiver_name=user.first_name,
                                    receiver_email=user.current_email,
                                    subject="Account Verified",
                                    content={},
                                    email_type="after_verify")

                            success = "Your account has been verified. "
                            success_message(self, success)
                            self.redirect("/login")
                        else:
                            self.redirect("/register")
                    elif user.status == "INVITE" and user.role == "OPENDATAADMIN":
                        self.tv["token"] = self.GET("token")
                        self.tv["uid"] = self.GET("uid")
                        self.tv["email"] = user.current_email
                        self.render("frontend/register-opendataadmin.html")
                    else:
                        error = "You may have clicked an expired link "
                        error += "or mistyped the address."
                        error_message(self, error)
                        self.redirect("/login")
                else:
                    error = "Sorry, we couldn't process your request. "
                    error += "Please try again."
                    error_message(self, error)
                    self.redirect("/register")
            else:
                self.redirect("/register")


class SendVerificationHandler(BaseHandler):
    def get(self):
        """
            Handles the /register/verify/send endpoint.
            Resends email verification.
        """
        self.render("frontend/send-verification.html")

    def post(self):
        """
            Handles the /register/verify/send endpoint.
            Resends email verification.
        """
        if self.POST("email"):
            email = self.POST("email").lower().strip()

            query = User.query()
            query = query.filter(User.current_email == email)
            user = query.get()

            if user:
                if user.status == "PENDING":
                    content = {
                        "token": user.confirmation_token,
                        "uid": str(user.key.id())
                    }

                    send_email(
                        receiver_name=user.first_name,
                        receiver_email=user.current_email,
                        subject="Email Verfication",
                        content=content,
                        email_type="verify")

                    success = "The verification email has been sent to "
                    success += self.POST("email") + ". Please open the "
                    success += "email and verify your account "
                    success += "to complete the registration."
                    success_message(self, success)
                    self.redirect("/register/verify/send")
                else:
                    error = "Account is already verified."
                    error_message(self, error)
                    self.redirect("/register/verify/send")
            else:
                error = "Sorry, " + self.POST("email")
                error += " does not belong to an existing account."
                error_message(self, error)
                self.redirect("/register/verify/send")
        else:
            error = "Email is required."
            error_message(self, error)
            self.redirect("/register/verify/send")


class DashboardHandler(BaseHandler):
    @login_required
    def get(self):
        """
            Handles the /dashboard endpoint.
            Dashboard page of the user.
        """
        if self.user.role in ["AGENCYADMIN", "MODERATOR"]:
            if self.GET("ajax") and self.GET("query"):
                search = self.GET("query").strip().upper()
                status = "STATUS->" + self.GET("status").strip().upper()
                query = APIData.query()
                # query = query.filter(APIData.indexed_data == status)
                query = query.filter(APIData.tags >= search)
                tag = create_indexed_tag("UACS_ID", self.user.uacs)
                query = query.filter(APIData.indexed_data == tag)

                logging.info(query)

                if self.GET("cursor"):
                    curs = Cursor(urlsafe=self.GET("cursor"))
                    datasets, cursor, more = query.fetch_page(50, start_cursor=curs)
                else:
                    datasets, cursor, more = query.fetch_page(50)

                dataset_dict = []

                if datasets:
                    for dataset in datasets:
                        dataset_dict.append(dataset.to_api_object())

                response = {}
                response["data"] = dataset_dict
                response["cursor"] = ""
                if more:
                    response["cursor"] = cursor.urlsafe()

                wrap_response(self, response)
            else:
                self.tv["breadcrumb"] = [{
                    "name": "AGENCY DASHBOARD",
                    "link": "/dashboard"
                }]
                self.render("/frontend/dashboard-agencyadmin.html")
        elif self.user.role == "OPENDATAADMIN":
            if self.GET("ajax") and self.GET("query"):
                search = self.GET("query").strip().upper()
                status = "STATUS->" + self.GET("status").strip().upper()
                query = APIData.query()
                # query = query.filter(APIData.indexed_data == status)
                query = query.filter(APIData.tags >= search)

                logging.info(query)

                if self.GET("cursor"):
                    curs = Cursor(urlsafe=self.GET("cursor"))
                    datasets, cursor, more = query.fetch_page(50, start_cursor=curs)
                else:
                    datasets, cursor, more = query.fetch_page(50)

                dataset_dict = []

                if datasets:
                    for dataset in datasets:
                        dataset_dict.append(dataset.to_api_object())

                response = {}
                response["data"] = dataset_dict
                response["cursor"] = ""
                if more:
                    response["cursor"] = cursor.urlsafe()

                wrap_response(self, response)
            else:
                self.tv["breadcrumb"] = [{
                    "name": "DATA-ADMIN DASHBOARD",
                    "link": "/dashboard"
                }]
                self.render("/frontend/dashboard-opendataadmin.html")
        elif self.user.role == "SUPERADMIN":
            self.tv["breadcrumb"] = [{
                "name": "SUPERADMIN DASHBOARD",
                "link": "/dashboard"
            }]
            self.render("/frontend/dashboard-superadmin.html")
        else:
            self.redirect("http://dgph.urls.ph/infographics/philgeps")

    @allowed_users(["SUPERADMIN", "OPENDATAADMIN"])
    def post(self):
        """
            Handles the /dashboard endpoint.
            Dashboard page of the user.
        """
        if self.POST("email"):
            email = self.POST("email").strip().lower()
            user = User.check_user(email)
            if user:
                error = "Sorry, it looks like "
                error += email + " belongs to an existing account."
                error_message(self, error)
                self.redirect("/opendata/admins")
                return

            user = User.invite_new_opendata_admin(
                email=email)

            success = "Your invitation has been sent to "
            success += email + "."
            success_message(self, success)
            self.redirect("/opendata/admins")
            return

        self.redirect("/dashboard")


class FeedbacksHandler(BaseHandler):
    @allowed_users(["AGENCYADMIN"])
    def get(self):
        self.tv["show_breadcrumb"] = False
        self.tv["show_add_dataset"] = False
        self.render('frontend/error404.html')
        return

        """
            Handles the /feedback endpoint.
            Shows the user feedbacks.
        """
        self.tv["breadcrumb"] = [{
            "name": "USER SUBMISSION",
            "link": "/feedback"
        }]
        self.tv["data"] = []

        query = APIData.query()
        tag = create_indexed_tag("type", "FEEDBACK")
        query = query.filter(APIData.indexed_data == tag)

        if self.GET("status"):
            tag = create_indexed_tag("status", self.GET("status"))
            query = query.filter(
                APIData.indexed_data == tag)

        if self.user.permissions \
           and self.user.role in ["AGENCYADMIN", "MODERATOR"]:
            for permission in self.user.permissions:
                query = query.filter(APIData.indexed_data == permission)

        logging.info(query)

        if self.GET("cursor"):
            pass
        else:
            data, cursor, more = query.fetch_page(50)

        if data:
            for d in data:
                self.tv["data"].append(d.to_object())

        if self.GET("ajax"):
            wrap_response(self, {"feedbacks": self.tv["data"]})
        else:
            self.render("frontend/feedbacks.html")

    def post(self):
        self.error(403)
        return
        """
            Handles the /feedback endpoint.
            Shows the user feedbacks.
        """
        if self.POST("feedback_id") and self.POST("action"):
            data = APIData.get_by_id(int(self.POST("feedback_id")))
            if data:
                if self.GET("status"):
                    tag = create_indexed_tag("status", self.GET("status"))
                    query = query.filter(
                        APIData.indexed_data == tag)
                if self.POST("action") == "approve":
                    tag = create_indexed_tag("status", "APPROVED")
                elif self.POST("action") == "disapprove":
                    tag = create_indexed_tag("status", "DISAPPROVED")

                try:
                    for d in data.indexed_data:
                        if d.startswith("STATUS"):
                            data.indexed_data.remove(d)

                    data.indexed_data.append(tag)
                except Exception, e:
                    logging.exception(e)

                data.put()

                wrap_response(self, {"status": "ok"})
            else:
                wrap_response(self, {"status": "error"})

            return


class PostSuccessHandler(BaseHandler):
    def get(self):
        self.tv["redirect_url"] = "/dashboard"
        if self.GET("redirect"):
            self.tv["redirect"] = urllib.unquote(self.GET("redirect"))

        self.tv["postsuccess"] = True
        self.render("frontend/thankyou.html")


class UACSAPIHandler(BaseHandler):
    def get(self):
        """
            Handles the /api/v1/uacs endpoint.
            Returns list of uacs.
        """
        response = {
            "code": 200,
            "type": "",
            "method": "GET",
            "response": "OK",
            "data": []
        }

        department = ""
        agency = ""
        region = ""
        operating_unit = ""

        if self.request.get('department'):
            department = self.request.get('department').upper().strip()

        if self.request.get('agency'):
            agency = self.request.get('agency').upper().strip()

        if self.request.get('region'):
            region = self.request.get('region').upper().strip()

        if self.request.get('operating_unit'):
            operating_unit = self.request.get('operating_unit').upper().strip()

        uacs_json_file = json.load(open('uacs.json'))
        response_json = []

        if department:
            if department in uacs_json_file:
                if agency:
                    if agency in uacs_json_file[department]:
                        if region:
                            if region in uacs_json_file[department][agency]:
                                response_json = uacs_json_file[department][agency][region]
                            else:
                                response["code"] = 404
                                response["response"] = "NOT FOUND"
                        else:
                            response_json = sorted(uacs_json_file[department][agency].keys())
                    else:
                        response["code"] = 404
                        response["response"] = "NOT FOUND"
                else:
                    response_json = sorted(uacs_json_file[department].keys())
            else:
                response["code"] = 404
                response["response"] = "NOT FOUND"

        else:
            response_json = sorted(uacs_json_file.keys())

        response['data'] = response_json

        if self.GET("callback"):
            callback = self.GET("callback")
            d = json.dumps(response)

            self.response.out.write(callback + "(" + d + ");")
        else:
            wrap_response(self, response)



class DataApiHandler(BaseHandler):
    def get(self):
        """
            Handles the /api/v1/data endpoint.
            Returns list of datasets.
        """
        response = {
            "code": 200,
            "type": "",
            "method": "GET",
            "response": "OK",
            "data": []
        }

        # Default number of entities to be retrieved is 50.
        n = 50
        if self.GET("n"):
            n = int(self.GET("n"))
            # if the number of entities to be retrieved given is
            # greater than 50. Switch back to default which is 50
            if n > 50:
                n = 50

        query = APIData.query()

        for arg in self.request.arguments():
            if arg.lower() == "callback" \
               or arg.lower() == "_" \
               or arg.lower() == "order" \
               or arg.lower() == "cursor" \
               or arg.lower() == "n":
                continue

            ad_value = self.GET(arg)
            tag = create_indexed_tag(arg, ad_value)
            query = query.filter(APIData.indexed_data == tag)

        if self.GET("order"):
            if self.GET("order").lower() in ["asc", "ascending"]:
                query = query.order(-APIData.updated_time)
            elif self.GET("order").lower() in ["desc", "descending"]:
                query = query.order(APIData.updated_time)
            elif self.GET("order").lower() == "created_asc":
                query = query.order(APIData.created_time)
            elif self.GET("order").lower() == "created_desc":
                query = query.order(-APIData.created_time)
            elif self.GET("order").lower() == "modified":
                query = query.order(-APIData.updated_time)
        else:
            query = query.order(-APIData.updated_time)

        logging.info(query)

        if self.GET("cursor"):
            curs = Cursor(urlsafe=self.GET("cursor"))
            data, cursor, more = query.fetch_page(n, start_cursor=curs)
        else:
            data, cursor, more = query.fetch_page(n)

        if data:
            response["cursor"] = ""

            for d in data:
                try:
                    response["data"].append(d.to_api_object())
                except Exception, e:
                    logging.exception(e)

            if more:
                response["cursor"] = cursor.urlsafe()

        if self.GET("callback"):
            callback = self.GET("callback")
            d = json.dumps(response)

            self.response.out.write(callback + "(" + d + ");")
        else:
            wrap_response(self, response)

    def post(self):
        """
            Handles the /api/v1/data endpoint.
            Creates a dataset.
        """
        response = {}
        if not self.request.arguments():
            desc = "There are missing parameters in your request."
            if self.POST("redirect"):
                url = str(self.POST("redirect"))
                if "?" in url:
                    url = url.split("?")[0]
                url += "?error=" + urllib.quote(desc)
                self.redirect(url)
                return
            else:
                response["response"] = "MissingParametersError"
                response["description"] = desc
                response["code"] = 400
                wrap_response(self, response)
                return

        data = APIData()
        data.additional_data = {}

        try:
            for arg in self.request.arguments():
                # if arg.startswith('list_'): # unindexed_
                #     try:
                #         data.additional_data[arg] = [a.strip() for a in self.request.get(arg).split(',')]
                #     except:
                #         logging.exception('error in extracting list')
                if arg.lower() == "unindexed_license_id":
                    for l in LICENSE:
                        if l["code"] == self.request.POST.get(arg).lower():
                            data.additional_data["license_title"] = l["name"]

                if arg.lower() == "indexed_type":
                    if self.request.POST.get(arg).upper() == "DATASET":
                        data.additional_data["private"] = False

                if arg.startswith('unindexed_'):  # unindexed_
                    ad_key = arg.replace("unindexed_", "")
                    ad_value = self.request.POST.get(arg)
                    data.additional_data[ad_key] = ad_value.strip()

                if arg.startswith('indexed_'):
                    ad_key = arg.replace("indexed_", "")
                    ad_value = self.request.POST.get(arg)
                    data.additional_data[ad_key] = ad_value

                    data.indexed_data.append(
                        create_indexed_tag(
                            arg, self.request.POST.get(arg)))

                if arg.startswith('file_'):
                    filename = "/amt-dgph.appspot.com/uploads/"
                    filename += random_string(20) + "/"
                    ad_key = arg.replace("file_", "")
                    data.additional_data[ad_key] = {}
                    try:
                        # try:
                        file_name = self.request.POST.get(arg).filename
                        filename += file_name

                        gcs_file = gcs.open(
                            filename, 'w',
                            options={'x-goog-acl': 'public-read'})
                        gcs_file.write(self.request.get(arg))
                        gcs_file.close()

                        full_url = "http://storage.googleapis.com" + filename
                        # data.additional_data["file"]["file_url"] = full_url

                        data.file_url = full_url
                        data.additional_data[ad_key]["file_url"] = full_url

                        try:
                            blob_key = blobstore.create_gs_key("/gs" + filename)
                            data.serving_url = images.get_serving_url(blob_key)
                            data.additional_data[ad_key]["serving_url"] = data.serving_url
                            data.gcs_key = blobstore.BlobKey(blob_key)
                            # data.additional_data[arg.lower().replace("file_", "")] = data.serving_url
                        except Exception, e:
                            logging.exception(e)
                            logging.error("not an image??")
                            data.additional_data[ad_key]["serving_url"] = full_url
                            # data.additional_data[arg.lower().replace("file_", "")] = full_url
                    except AttributeError, e:
                        logging.exception(e)
                        logging.exception("NO FILE ATTACHED")

            if self.user:
                data.username = self.user.name
                data.user = self.user.key

            data.put()
            # LOG
            if self.POST("indexed_type") == "DATASET":
                log = self.POST("indexed_department") + " added " + self.POST("indexed_dataset_title") + " dataset."
                Logs.add_log(
                    data={"action": log, "icon": "plus", "color": "primary" },
                    uacs_id=data.additional_data["uacs_id"],
                    user=self.user.key,
                    dataset=data.key)
        except Exception, e:
            logging.exception(e)
            desc = "A server error occured. Please try again later."
            if self.POST("redirect"):
                url = str(self.POST("redirect"))
                if "?" in url:
                    url = url.split("?")[0]
                url += "?error=" + urllib.quote(desc)
                self.redirect(url)
                return
            else:
                response["response"] = "ServerError"
                response["description"] = desc
                response["code"] = 500
                wrap_response(self, response)
                return

        if self.POST("redirect"):
            desc = "Data has been saved."
            url = str(self.POST("redirect"))
            if "?" in url:
                url = url.split("?")[0]

            url += "?success=" + urllib.quote(desc)
            self.redirect(url)
        else:
            data = data.to_api_object()
            wrap_response(self, data)


class OpenDataAdminManageHandler(BaseHandler):
    def get(self):
        """
            Handles the /opendata/admins endpoint.
            Invite a new ODTF member.
        """
        self.tv["breadcrumb"] = [{
            "name": "OPEND DATA ADMIN INVITE",
            "link": "/opendata/admins"
        }]
        self.render("frontend/opendata-admins.html")


class CreateDatasetStep1Handler(BaseHandler):
    @allowed_users(["AGENCYADMIN", "OPENDATAADMIN"])
    def get(self, dataset_id=None):
        """
            Handles the /dataset/new endpoint.
            Step 1 in creating a dataset.
        """
        if self.user.role == "AGENCYADMIN"\
           and self.user.status == "VERIFIED":
            self.redirect("/dashboard")
            return

        if dataset_id:
            dataset = APIData.get_by_id(int(dataset_id))
            if not dataset:
                error = "Sorry, we couldn't find the dataset."
                error_message(self, error)
                self.redirect("/dataset/new")
                return

            self.tv["edit"] = True
            self.tv["dataset"] = dataset.to_api_object()

            self.tv["breadcrumb"] = [
                {
                    "name": "DATASETS",
                    "link": "/dashboard"
                },
                {
                    "name": self.tv["dataset"]["dataset_title"],
                    "link": "/dataset/new/" + dataset_id + "/step1"
                },
                {
                    "name": "EDIT",
                    "link": "javascript:void(0);"
                }
            ]
        else:
            self.tv["breadcrumb"] = [
                {
                    "name": "DATASETS",
                    "link": "/dashboard"
                },
                {
                    "name": "CREATE DATASET",
                    "link": "/dataset/new"
                },
            ]

        self.render("frontend/dataset-create-step1.html")

    @allowed_users(["AGENCYADMIN", "OPENDATAADMIN"])
    def post(self, dataset_id=None):
        """
            Handles the /dataset/new endpoint.
            Step 1 in creating a dataset.
        """
        if dataset_id:
            dataset = APIData.get_by_id(int(dataset_id))
            if not dataset:
                error = "Sorry, we couldn't find the dataset."
                error_message(self, error)
                self.redirect("/dataset/new")
                return

            logging.debug(self.request.arguments())

            for arg in self.request.arguments():
                if arg.startswith('unindexed_'):  # unindexed_
                    ad_key = arg.replace("unindexed_", "")
                    ad_value = self.request.POST.get(arg)
                    dataset.additional_data[ad_key] = ad_value.strip()

                if arg.startswith('indexed_'):
                    ad_key = arg.replace("indexed_", "")
                    ad_value = self.request.POST.get(arg)
                    dataset.additional_data[ad_key] = ad_value

                    dataset.indexed_data.append(
                        create_indexed_tag(
                            arg, self.request.POST.get(arg)))
            dataset.indexed_data = uniquify(dataset.indexed_data)
            tags = dataset.tags
            tags += create_tags(self.POST("indexed_dataset_title"))
            tags += create_tags(self.POST("indexed_department"))
            dataset.tags = uniquify(tags)
            dataset.put()

            success = "Dataset has been saved."
            success_message(self, success)
            self.redirect("/dataset/new/"+ dataset_id +"/step2")
        else:
            if self.POST("indexed_dataset_title") \
               and self.POST("unindexed_dataset_description") \
               and self.POST("indexed_dataset_category") \
               and self.POST("indexed_license_id") \
               and self.POST("indexed_department"):
                try:
                    if self.user.role == "AGENCYADMIN":
                        uacs = self.user.uacs
                    elif self.user.role == "OPENDATAADMIN":
                        uacs = self.POST("operating_unit").split("->")[1]

                    dataset = APIData.create_initial_dataset(
                        dataset_name=self.POST("indexed_dataset_title"),
                        dataset_desc=self.POST("unindexed_dataset_description"),
                        category=self.POST("indexed_dataset_category"),
                        department=self.POST("indexed_department"),
                        uacs=uacs,
                        user=self.user,
                        license_id=self.POST("indexed_license_id"),
                        odi=self.POST("unindexed_odi_certificate"))

                    dataset.user = self.user.key
                    dataset.username = self.user.name

                    if self.user.role == "OPENDATAADMIN":
                        dataset.additional_data["agency"] = self.POST("agency")
                        dataset.additional_data["region"] = self.POST("region")
                        dataset.additional_data["operating_unit"] = self.POST("operating_unit").split("->")[0]
                    dataset.put()

                    log = self.POST("indexed_department").upper() + " added " + self.POST("indexed_dataset_title").upper() + " dataset."
                    Logs.add_log(
                        data={"action": log, "icon": "plus", "color": "primary" },
                        uacs_id=dataset.additional_data["uacs_id"],
                        user=self.user.key,
                        dataset=dataset.key)

                    # if not APP_IS_LOCAL:
                    #     notifications = User.send_notification_emails(dataset)

                    self.redirect("/dataset/new/" + str(dataset.key.id()) + "/step2")
                except DatasetExistsError as e:
                    error = e.msg
                    error_message(self, error)
                    self.redirect("/dataset/new")
                except Exception, e:
                    logging.exception(e)
                    error = "An error occured. Could not create a dataset."
                    error_message(self, error)
                    self.redirect("/dataset/new")
            else:
                error = "Please fill all required fields."
                error_message(self, error)
                self.redirect("/dataset/new")


class CreateDatasetStep2Handler(BaseHandler):
    @allowed_users(["AGENCYADMIN", "OPENDATAADMIN"])
    def get(self, dataset_id=None):
        """
            Handles the /dataset/new/{dataset}/step2 endpoint.
            Step 2 in creating a dataset.
        """
        if not dataset_id:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dataset/new")
            return

        dataset = APIData.get_by_id(int(dataset_id))
        if not dataset:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dataset/new")
            return

        self.tv["dataset"] = dataset.to_api_object()

        self.tv["breadcrumb"] = [
            {
                "name": "DATASETS",
                "link": "/dashboard"
            },
            {
                "name": self.tv["dataset"]["dataset_title"],
                "link": "/dataset/new/" + self.tv["dataset"]["id"] + "/step1"
            },
            {
                "name": "ADDITIONAL INFO",
                "link": "javascript:void(0);"
            }
        ]

        self.render("frontend/dataset-create-step2.html")

    @allowed_users(["AGENCYADMIN", "OPENDATAADMIN"])
    def post(self, dataset_id=None):
        """
            Handles the /dataset/new/{dataset}/step2 endpoint.
            Step 2 in creating a dataset.
        """
        if not dataset_id:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dataset/new")
            return

        dataset = APIData.get_by_id(int(dataset_id))
        if not dataset:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dataset/new")
            return

        try:
            info = {}
            for arg in self.request.arguments():
                value = self.request.POST.get(arg)
                arg = arg.replace("unindexed_", "")
                arg = arg.replace("indexed_", "")
                if not value:
                    info[arg] = ""
                else:
                    info[arg] = value

            dataset = APIData.add_additional_info_dataset(
                dataset_id=dataset_id,
                additional_info=info)

            self.redirect("/dataset/new/" + dataset_id + "/step3")
        except Exception, e:
            logging.exception(e)
            error = "An error occured. Could not save the additional info."
            error_message(self, error)
            self.redirect("/dataset/new/" + dataset_id + "/step2")


class CreateDatasetStep3Handler(BaseHandler):
    @allowed_users(["AGENCYADMIN", "OPENDATAADMIN"])
    def get(self, dataset_id=None):
        """
            Handles the /dataset/new/{dataset}/step3 endpoint.
            Step 3 in creating a dataset.
        """
        if not dataset_id:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dataset/new")
            return

        dataset = APIData.get_by_id(int(dataset_id))
        if not dataset:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dataset/new")
            return

        self.tv["dataset"] = dataset.to_api_object()
        logging.debug(self.tv["dataset"])
        self.tv["breadcrumb"] = [
            {
                "name": "DATASETS",
                "link": "/dashboard"
            },
            {
                "name": self.tv["dataset"]["dataset_title"],
                "link": "/dataset/new/" + self.tv["dataset"]["id"] + "/step1"
            },
            {
                "name": "ADDITIONAL INFO",
                "link": "javascript:void(0);"
            }
        ]

        self.render("frontend/dataset-create-step3.html")

    @allowed_users(["AGENCYADMIN", "OPENDATAADMIN"])
    def post(self, dataset_id=None):
        """
            Handles the /dataset/new/{dataset}/step3 endpoint.
            Step 3 in creating a dataset.
        """
        if not dataset_id:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dataset/new")
            return

        dataset = APIData.get_by_id(int(dataset_id))
        if not dataset:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dataset/new")
            return

        if not self.GET("unindexed_dataset_data") \
           and not self.GET("file_dataset_data"):
            error = "A link or file is required."
            error_message(self, error)
            self.redirect("/dataset/new" + str(dataset.key.id()) + "/step3")
            return

        if not self.GET("indexed_file_name"):
            error = "File name is required."
            error_message(self, error)
            self.redirect("/dataset/new" + str(dataset.key.id()) + "/step3")

        if not self.GET("unindexed_file_description"):
            error = "File description is required."
            error_message(self, error)
            self.redirect("/dataset/new" + str(dataset.key.id()) + "/step3")

        try:
            self.tv["dataset"] = dataset.to_api_object()

            resource = APIData()
            resource.additional_data = {}
            resource.additional_data["type"] = "RESOURCE"
            resource.additional_data["uacs_id"] = self.tv["dataset"]["uacs_id"]
            resource.additional_data["department"] = self.tv["dataset"]["department"]
            resource.additional_data["dataset_id"] = self.tv["dataset"]["id"]
            resource.additional_data["user_id"] = str(self.user.key.id())

            tag = create_indexed_tag("type", "RESOURCE")
            resource.indexed_data.append(tag)
            tag = create_indexed_tag("uacs_id", self.tv["dataset"]["uacs_id"])
            resource.indexed_data.append(tag)
            tag = create_indexed_tag("department", self.tv["dataset"]["department"])
            resource.indexed_data.append(tag)
            tag = create_indexed_tag("dataset_id", self.tv["dataset"]["id"])
            resource.indexed_data.append(tag)
            tag = create_indexed_tag("user_id", str(self.user.key.id()))
            resource.indexed_data.append(tag)

            for arg in self.request.arguments():
                if arg.startswith('unindexed_'):  # unindexed_
                    ad_key = arg.replace("unindexed_", "")
                    ad_value = self.request.POST.get(arg)

                    if ad_key == "dataset_data":
                        resource.additional_data[ad_key] = {}
                        resource.additional_data[ad_key]["file_url"] = ad_value
                        resource.additional_data[ad_key]["serving_url"] = ad_value
                    else:
                        resource.additional_data[ad_key] = ad_value.strip()

                if arg.startswith('indexed_'):
                    ad_key = arg.replace("indexed_", "")
                    ad_value = self.request.POST.get(arg)
                    resource.additional_data[ad_key] = ad_value

                    resource.indexed_data.append(
                        create_indexed_tag(
                            arg, self.request.POST.get(arg)))

                if arg.startswith("file_"):
                    ad_key = arg.replace("file_", "")
                    resource.additional_data[ad_key] = {}
                    filename = "/amt-dgph.appspot.com/uploads/"
                    filename += random_string(20) + "/"

                    try:
                        file_name = self.request.POST.get(arg).filename
                        filename += file_name

                        gcs_file = gcs.open(
                            filename, 'w',
                            options={'x-goog-acl': 'public-read'})
                        gcs_file.write(self.request.get(arg))
                        gcs_file.close()

                        full_url = "http://storage.googleapis.com" + filename
                        # data.additional_data["file"]["file_url"] = full_url

                        resource.file_url = full_url
                        resource.additional_data[ad_key]["file_url"] = full_url

                        try:
                            blob_key = blobstore.create_gs_key(
                                "/gs" + filename)
                            resource.serving_url = images.get_serving_url(blob_key)
                            resource.gcs_key = blobstore.BlobKey(blob_key)
                            resource.additional_data[ad_key]["serving_url"] = resource.serving_url
                        except Exception, e:
                            logging.exception(e)
                            logging.error("not an image??")
                            resource.additional_data[ad_key]["serving_url"] = full_url

                    except AttributeError, e:
                        logging.exception(e)
                        logging.exception("NO FILE ATTACHED")

            resource.indexed_data = uniquify(resource.indexed_data)
            resource.user = self.user.key
            resource.username = self.user.name
            resource.put()

            dataset.additional_data["status"] = "FOR REVIEW"
            for indexed_data in dataset.indexed_data:
                if indexed_data.startswith("STATUS"):
                    dataset.indexed_data.remove(indexed_data)

            tag = create_indexed_tag("STATUS", "FOR REVIEW")
            dataset.indexed_data.append(tag)
            dataset.put()

            if self.POST("message"):
                success = "Resource has been saved."
            else:
                success = "Dataset has been saved."

            success_message(self, success)
            self.redirect("/dataset/" + dataset_id)
        except Exception, e:
            logging.exception(e)
            error = "An error occured. Could not save the resource."
            error_message(self, error)
            self.redirect("/dataset/" + dataset_id)


class DatasetDetailsHandler(BaseHandler):
    @allowed_users(["AGENCYADMIN", "OPENDATAADMIN"])
    def get(self, dataset_id=None):
        """
            Handles the /dataset/{dataset} endpoint.
            Displays the dataset details.
        """
        if not dataset_id:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dashboard")
            return

        try:
            dataset = APIData.get_by_id(int(dataset_id))
            if not dataset:
                error = "Sorry, we couldn't find the dataset."
                error_message(self, error)
                self.redirect("/dashboard")
                return
        except Exception, e:
            logging.exception(e)
            self.tv["404"] = True
            self.render('frontend/error404.html')
            return

        if self.GET("success"):
            self.tv["success"] = "Data has been saved."

        if self.GET("version_id"):
            parent_key = ndb.Key("APIData", int(self.GET("version_key")))
            dataset_version = SL.get_by_id(int(self.GET("version_id")), parent=parent_key)
            if dataset_version:
                self.tv["dataset"] = dataset_version.to_api_object()
                success = "Showing dataset version " + self.GET("version_number") + "."
                self.tv["success"] = success
            else:
                error = "Could not load version "+self.GET("version_number")+". "
                error += "Current version has been loaded instead."
                self.tv["error"] = error
                self.tv["dataset"] = dataset.to_api_object()
        else:
            self.tv["dataset"] = dataset.to_api_object()

        self.tv["versions"] = sorted(
            dataset.get_all_versions(), key=lambda k: k['version'], reverse=True)

        if self.GET("version_number"):
            self.tv["v"] = int(self.GET("version_number"))
        else:
            self.tv["v"] = int(len(self.tv["versions"]))

        self.tv["breadcrumb"] = [
            {
                "name": "DATASET",
                "link": "/dashboard"
            },
            {
                "name": self.tv["dataset"]["dataset_title"],
                "link": "/dataset/" + self.tv["dataset"]["id"]
            }
        ]

        dataset_indexed_id = create_indexed_tag(
            "DATASET_ID", self.tv["dataset"]["id"])
        query = APIData.query()
        query = query.filter(APIData.indexed_data == dataset_indexed_id)
        resources = query.fetch()
        self.tv["resources"] = []

        if resources:
            for resource in resources:
                self.tv["resources"].append(resource.to_api_object())

        self.render("frontend/dataset-single.html")


class ResourceDetailsHandler(BaseHandler):
    def get(self, resource_id=None):
        """
            Handles the /resource/{resource} endpoint.
            Displays the resource details.
        """
        if not resource_id:
            error = "Sorry, we couldn't find the resource."
            error_message(self, error)
            self.redirect("/dashboard")
            return

        resource = APIData.get_by_id(int(resource_id))
        if not resource:
            error = "Sorry, we couldn't find the resource."
            error_message(self, error)
            self.redirect("/dashboard")
            return

        if self.GET("success"):
            self.tv["success"] = "Data has been saved."

        if self.GET("version_id"):
            parent_key = ndb.Key("APIData", int(self.GET("version_key")))
            resource_version = SL.get_by_id(int(self.GET("version_id")), parent=parent_key)
            if resource_version:
                self.tv["resource"] = resource_version.to_api_object()
                success = "Showing dataset version " + self.GET("version_number") + "."
                self.tv["success"] = success
                self.tv["version"] = self.GET("version_number")

            else:
                error = "Could not load version "+self.GET("version_number")+". "
                error += "Current version has been loaded instead."
                self.tv["error"] = error
                self.tv["resource"] = resource.to_api_object()
        else:
            self.tv["resource"] = resource.to_api_object()

        dataset = APIData.get_by_id(int(self.tv["resource"]["dataset_id"]))
        if not dataset:
            error = "Sorry, we couldn't find the resource."
            error_message(self, error)
            self.redirect("/dashboard")
            return

        dataset = dataset.to_api_object()

        query = APIData.query()
        tag = create_indexed_tag("TYPE", "RESOURCE")
        query = query.filter(APIData.indexed_data == tag)
        tag = create_indexed_tag("DATASET_ID", dataset["id"])
        query = query.filter(APIData.indexed_data == tag)
        resources = query.fetch()

        logging.info(query)

        self.tv["resources"] = []
        if resources:
            for r in resources:
                self.tv["resources"].append(r.to_api_object())

        self.tv["versions"] = sorted(
            resource.get_all_versions(), key=lambda k: k['version'], reverse=True)

        if self.GET("version_number"):
            self.tv["v"] = int(self.GET("version_number"))
        else:
            self.tv["v"] = int(len(self.tv["versions"]))

        self.tv["breadcrumb"] = [
            {
                "name": "DATASET",
                "link": "/dashboard"
            },
            {
                "name": dataset["dataset_title"],
                "link": "/dataset/" + dataset["id"]
            },
            {
                "name": self.tv["resource"]["file_name"],
                "link": "/resource/" + self.tv["resource"]["id"]
            }
        ]

        self.render("frontend/resource-details.html")


class ResourceEditHandler(BaseHandler):
    @allowed_users(["AGENCYADMIN", "OPENDATAADMIN"])
    def get(self, resource_id=None):
        """
            Handles the /resource/{resource}/edit endpoint.
            Edits the resource details.
        """
        if not resource_id:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dashboard")
            return

        resource = APIData.get_by_id(int(resource_id))
        if not resource:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dashboard")
            return

        self.tv["resource"] = resource.to_api_object()
        self.tv["breadcrumb"] = [
            {
                "name": "RESOURCE",
                "link": "/resource"
            },
            {
                "name": self.tv["resource"]["file_name"],
                "link": "/resource/" + self.tv["resource"]["id"]
            },
            {   "name": "EDIT",
                "link": "/resource/" + self.tv["resource"]["id"] + "/edit"
            }
        ]
        self.render("frontend/resource-edit.html")

    @allowed_users(["AGENCYADMIN", "OPENDATAADMIN"])
    def post(self, resource_id=None):
        """
            Handles the /resource/{resource}/edit endpoint.
            Edits the resource details.
        """
        if not resource_id:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dashboard")
            return

        resource = APIData.get_by_id(int(resource_id))
        if not resource:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dashboard")
            return


        if self.POST("delete_resource"):
            dataset_id = resource.additional_data["dataset_id"]
            resource_title = resource.additional_data["file_name"]
            dataset = APIData.get_by_id(int(dataset_id))

            if "CKAN_ID" in resource.additional_data:
                dataset_ckan = {}
                dataset_ckan["id"] = resource.additional_data["CKAN_ID"]

                url = "http://api.data.gov.ph/catalogue/api/action/resource_delete"

                dataset_ckan = json.dumps(dataset_ckan)

                logging.info(dataset_ckan)
                dataset_ckan_string = urllib.quote(dataset_ckan)
                headers = {"Authorization": CKAN_API_KEY}
                content = urlfetch.fetch(
                    url=url,
                    method=urlfetch.POST,
                    payload=dataset_ckan_string,
                    headers=headers,
                    deadline=15).content

                logging.info(content)
                try:
                    content = json.loads(content)
                except Exception, e:
                    logging.exception(e)
                    return

                if not content["success"]:
                    return

            resource.key.delete()

            log = "ODTF-Admin deleted " + resource_title.upper() + " resource."
            Logs.add_log(
                data={"action": log, "icon": "trash-o", "color": "danger" },
                user=self.user.key,
                uacs_id=dataset.additional_data["uacs_id"],
                dataset=dataset.key)

            success = "Resource has been deleted."
            success_message(self, success)
            self.redirect("/dataset/" + dataset_id)
        elif self.POST("update_resource"):
            for arg in self.request.arguments():
                if arg.startswith('unindexed_'):  # unindexed_
                    ad_key = arg.replace("unindexed_", "")
                    ad_value = self.request.POST.get(arg)

                    if ad_key == "dataset_data":
                        resource.additional_data[ad_key] = {}
                        resource.additional_data[ad_key]["file_url"] = ad_value
                        resource.additional_data[ad_key]["serving_url"] = ad_value
                    else:
                        resource.additional_data[ad_key] = ad_value.strip()

                if arg.startswith('indexed_'):
                    ad_key = arg.replace("indexed_", "")
                    ad_value = self.request.POST.get(arg)
                    resource.additional_data[ad_key] = ad_value

                    resource.indexed_data.append(
                        create_indexed_tag(
                            arg, self.request.POST.get(arg)))

                if arg.startswith('file_'):
                    ad_key = arg.replace("file_", "")
                    filename = "/amt-dgph.appspot.com/uploads/"
                    filename += random_string(20) + "/"

                    try:
                        # try:
                        file_name = self.request.POST.get(arg).filename
                        filename += file_name

                        gcs_file = gcs.open(
                            filename, 'w',
                            options={'x-goog-acl': 'public-read'})
                        gcs_file.write(self.request.get(arg))
                        gcs_file.close()

                        full_url = "http://storage.googleapis.com" + filename
                        # data.additional_data["file"]["file_url"] = full_url

                        resource.file_url = full_url
                        resource.additional_data[ad_key]["file_url"] = full_url

                        try:
                            blob_key = blobstore.create_gs_key(
                                "/gs" + filename)
                            resource.serving_url = images.get_serving_url(blob_key)
                            resource.gcs_key = blobstore.BlobKey(blob_key)
                            resource.additional_data[ad_key]["serving_url"] = resource.serving_url
                        except Exception, e:
                            logging.exception(e)
                            logging.error("not an image??")
                            resource.additional_data[ad_key]["serving_url"] = full_url

                    except AttributeError, e:
                        logging.exception(e)
                        logging.exception("NO FILE ATTACHED")

            resource.indexed_data = uniquify(resource.indexed_data)
            resource.put()

            success = "Resource has been updated."
            success_message(self, success)
            if self.POST("redirect"):
                self.redirect(self.POST("redirect"))
            else:
                self.redirect("/resource/" + str(resource.key.id()))
        else:
            error = "Could not update the resource."
            error_message(self, error)
            if self.POST("redirect"):
                self.redirect(self.POST("redirect"))
            else:
                self.redirect("/resource/" + str(resource.key.id()))


class DatasetStatusHandler(BaseHandler):
    @allowed_users(["OPENDATAADMIN"])
    def post(self, dataset_id=None):
        """
            Handles the /dataset/{dataset}/status endpoint.
            Updates the dataset status.
        """
        if not dataset_id:
            self.error(400)
            return

        dataset = APIData.get_by_id(int(dataset_id))
        if not dataset:
            self.error(400)
            return

        if self.POST("status"):
            if self.POST("status") == "PUBLISHED":
                dataset_ckan = {}
                dataset_ckan["name"] = dataset.additional_data["dataset_ckan_name"].lower()
                dataset_ckan["owner_org"] = self.POST("owner_org")
                # dataset_ckan["metadata_created"] = time.mktime(dataset.created_time.timetuple())
                # dataset_ckan["metadata_updated"] = time.mktime(dataset.updated_time.timetuple())
                # dataset_ckan["is_open"] = True
                dataset_ckan["extras"] = []

                for key, value in dataset.additional_data.items():
                    # key = key.replace("user_id", "creator_user_id")
                    key = key.replace("dataset_description", "notes")
                    key = key.replace("dataset_title", "title")
                    key = key.replace("maintainer_name", "maintainer")
                    key = key.replace("author_name", "author")

                    if key in ["status", "id", "comment", "uacs_id"]:
                        continue

                    if key == "CKAN_ID":
                        key = key.replace("CKAN_ID", "id")

                    if key == "type":
                        value = value.lower()

                    if key in ["temporal_date", "granularity", "frequency_update"]:
                        dataset_ckan["extras"].append({
                            "key": key.replace("_", " ").title(),
                            "value": value
                        })
                    else:
                        dataset_ckan[key] = value

                try:
                    if dataset.additional_data["CKAN_ID"]:
                        url = "http://api.data.gov.ph/catalogue/api/action/package_update"
                    else:
                        url = "http://api.data.gov.ph/catalogue/api/action/package_create"
                except Exception, e:
                    url = "http://api.data.gov.ph/catalogue/api/action/package_create"


                dataset_ckan = json.dumps(dataset_ckan)

                logging.info(dataset_ckan)
                dataset_ckan_string = urllib.quote(dataset_ckan)
                headers = {"Authorization": CKAN_API_KEY}
                content = urlfetch.fetch(
                    url=url,
                    method=urlfetch.POST,
                    payload=dataset_ckan_string,
                    headers=headers,
                    deadline=15).content

                logging.info(content)
                try:
                    content = json.loads(content)
                except Exception, e:
                    logging.exception(e)
                    return

                if not content["success"]:
                    if "That URL is already in use." in content["error"]["name"]:
                        error = "A dataset with name "
                        error += dataset_ckan["name"]
                        error += " already exists in the CKAN API. Please choose a different name "
                        error += " or delete the existing dataset."
                    else:
                        error = "An error occured. The dataset was not published."
                    #     try:
                    #         if dataset.additional_data["CKAN_ID"]:
                    #             url = "http://api.data.gov.ph/catalogue/api/action/package_update"
                    #         else:
                    #             url = "http://api.data.gov.ph/catalogue/api/action/package_create"
                    #     except Exception, e:
                    #         url = "http://api.data.gov.ph/catalogue/api/action/package_create"
                    error_message(self, error)
                    self.redirect("/dataset/" + str(dataset.key.id()))
                    return

                dataset.additional_data["CKAN_ID"] = content["result"]["id"]

                resource = dataset.get_all_resource()
                if resource:
                    for r in resource:
                        payload = {
                            "package_id": content["result"]["id"],
                            "url": r.additional_data["dataset_data"]["file_url"],
                            "name": r.additional_data["file_name"],
                            "description": r.additional_data["file_description"]
                        }

                        headers={"X-CKAN-API-Key": CKAN_API_KEY}
                        # payload = {"package_id": "26c4b1b3-51e6-4810-9a50-450cffd29711"}
                        resource = urlfetch.fetch(
                            url='http://api.data.gov.ph/catalogue/api/action/resource_create',
                            method=urlfetch.POST,
                            payload=json.dumps(payload),
                            headers=headers,
                            deadline=15).content
                        logging.info(resource)

                        result = json.loads(resource)

                        if not result["success"]:
                            return

                        r.additional_data["CKAN_ID"] = result["result"]["id"]
                        r.put()

                log = "ODTF-Admin published " + dataset.additional_data["dataset_title"] + " dataset."
                Logs.add_log(
                    data={"action": log, "icon": "check", "color": "info" },
                    user=self.user.key,
                    uacs_id=dataset.additional_data["uacs_id"],
                    dataset=dataset.key)

                success = "The dataset has been published."
                success_message(self, success)
                self.redirect("/dataset/" + str(dataset.key.id()))
            elif self.POST("status") == "SENT BACK":
                log = "ODTF-Admin sent back " + dataset.additional_data["dataset_title"] + " dataset."
                Logs.add_log(
                    data={"action": log, "icon": "reply", "color": "danger" },
                    user=self.user.key,
                    uacs_id=dataset.additional_data["uacs_id"],
                    dataset=dataset.key)
            elif self.POST("status") == "FOR CLEAN UP":
                log = "ODTF-Admin cleaning up " + dataset.additional_data["dataset_title"] + " dataset."
                Logs.add_log(
                    data={"action": log, "icon": "pencil", "color": "warning" },
                    user=self.user.key,
                    uacs_id=dataset.additional_data["uacs_id"],
                    dataset=dataset.key)

            if self.POST("comment"):
                dataset.additional_data["comment_for_sent_back"] = self.POST("comment").strip()
                try:
                    dataset.additional_data["comment"].append({
                        "comment": self.POST("comment").strip(),
                        "comment_date": global_vars.datetime_now_adjusted.strftime("%b %d, %Y %I:%H:%S %p"),
                        "comment_author": "ODTF-Admin"
                    })
                except Exception, e:
                    dataset.additional_data["comment"] = []
                    dataset.additional_data["comment"].append({
                        "comment": self.POST("comment").strip(),
                        "comment_date": global_vars.datetime_now_adjusted.strftime("%b %d, %Y %I:%H:%S %p"),
                        "comment_author": "ODTF-Admin"
                    })

            for key, value in dataset.additional_data.items():
                if key == "status":
                    dataset.additional_data[key] = self.POST("status").upper()

            try:
                tag = create_indexed_tag("status", self.POST("status").upper())
                for indexed_list in dataset.indexed_data:
                    if indexed_list.startswith("STATUS"):
                        dataset.indexed_data.remove(indexed_list)

                dataset.indexed_data.append(tag)
            except Exception, e:
                logging.exception(e)

            dataset.put()

    # def push_to_ckan(dataset):


class DatasetEditHandler(BaseHandler):
    @allowed_users(["AGENCYADMIN", "OPENDATAADMIN"])
    def get(self, dataset_id=None):
        """
            Handles the /dataset/{dataset}/edit endpoint.
            Edits the dataset details.
        """
        if not dataset_id:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dashboard")
            return

        dataset = APIData.get_by_id(int(dataset_id))
        if not dataset:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dashboard")
            return

        self.tv["dataset"] = dataset.to_api_object()
        self.tv["breadcrumb"] = [
            {
                "name": "DATASET",
                "link": "/dashboard"
            },
            {
                "name": self.tv["dataset"]["dataset_title"],
                "link": "/dataset/" + self.tv["dataset"]["id"]
            },
            {
                "name": "EDIT",
                "link": "/dataset/" + self.tv["dataset"]["id"]
            }
        ]

        dataset_indexed_id = create_indexed_tag(
            "DATASET_ID", self.tv["dataset"]["id"])
        query = APIData.query()
        query = query.filter(APIData.indexed_data == dataset_indexed_id)
        resources = query.fetch()
        self.tv["resources"] = []

        if resources:
            for resource in resources:
                self.tv["resources"].append(resource.to_api_object())

        self.render("frontend/dataset-edit.html")

    @allowed_users(["AGENCYADMIN", "OPENDATAADMIN"])
    def post(self, dataset_id=None):
        """
            Handles the /dataset/{dataset}/edit endpoint.
            Edits the dataset details.
        """
        if not dataset_id:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dashboard")
            return

        dataset = APIData.get_by_id(int(dataset_id))
        if not dataset:
            error = "Sorry, we couldn't find the dataset."
            error_message(self, error)
            self.redirect("/dashboard")
            return

        if self.POST("delete_dataset"):
            if "CKAN_ID" in dataset.additional_data:
                dataset_ckan = {}
                dataset_ckan["id"] = dataset.additional_data["CKAN_ID"]

                url = "http://api.data.gov.ph/catalogue/api/action/package_delete"

                dataset_ckan = json.dumps(dataset_ckan)

                logging.info(dataset_ckan)
                dataset_ckan_string = urllib.quote(dataset_ckan)
                headers = {"Authorization": CKAN_API_KEY}
                content = urlfetch.fetch(
                    url=url,
                    method=urlfetch.POST,
                    payload=dataset_ckan_string,
                    headers=headers,
                    deadline=15).content

                logging.info(content)
                try:
                    content = json.loads(content)
                except Exception, e:
                    logging.exception(e)
                    return

                if not content["success"]:
                    return

            dataset.key.delete()

            log = "ODTF-Admin deleted " + dataset.additional_data["dataset_title"].upper() + " dataset."
            Logs.add_log(
                data={"action": log, "icon": "trash-o", "color": "danger" },
                user=self.user.key,
                uacs_id=dataset.additional_data["uacs_id"],
                dataset=dataset.key)

            success = "Dataset has been deleted."
            success_message(self, success)
            self.redirect("/dashboard")
        elif self.POST("flag_dataset"):
            if not self.POST("dataset_comment"):
                error = "Comment is required."
                error_message(self, error)
                self.redirect("/dataset/" + str(dataset.key.id()))
                return

            dataset.additional_data["comment_for_deletion"] = self.POST("dataset_comment")
            dataset.additional_data["prev_status"] = dataset.additional_data["status"]
            dataset.additional_data["status"] = "FLAGGED FOR DELETION"

            for indexed_data in dataset.indexed_data:
                if indexed_data.startswith("STATUS"):
                    dataset.indexed_data.append("PREV_" + indexed_data)
                    dataset.indexed_data.remove(indexed_data)

            tag = create_indexed_tag("STATUS", "FLAGGED FOR DELETION")
            dataset.indexed_data.append(tag)
            dataset.put()

            log = dataset.additional_data["department"].upper() + " flagged " + dataset.additional_data["dataset_title"].upper() + " dataset for deletion."
            Logs.add_log(
                data={"action": log, "icon": "trash-o", "color": "inverse" },
                uacs_id=dataset.additional_data["uacs_id"],
                user=self.user.key,
                dataset=dataset.key)

            success = "Dataset has been flagged for deletion."
            success_message(self, success)
            self.redirect("/dataset/" + str(dataset.key.id()))
        elif self.POST("cancel_delete_dataset"):
            for indexed_data in dataset.indexed_data:
                if indexed_data.startswith("STATUS"):
                    dataset.indexed_data.remove(indexed_data)

                if indexed_data.startswith("PREV_STATUS"):
                    tag = indexed_data.replace("PREV_", "")
                    dataset.indexed_data.append(tag)
                    dataset.indexed_data.remove(indexed_data)

            dataset.additional_data["status"] = dataset.additional_data["prev_status"]
            dataset.additional_data["prev_status"] = "FLAGGED FOR DELETION"
            dataset.put()

            log = "ODTF-Admin cancelled " + dataset.additional_data["dataset_title"].upper() + " dataset request for deletion."
            Logs.add_log(
                data={"action": log, "icon": "times", "color": "danger" },
                uacs_id=dataset.additional_data["uacs_id"],
                user=self.user.key,
                dataset=dataset.key)

            success = "The dataset flagged for deletion request has been cancelled."
            success_message(self, success)
            self.redirect("/dataset/" + str(dataset.key.id()))
        elif self.POST("update_dataset"):
            if self.user.role == "OPENDATAADMIN":
                log = "ODTF-Admin updated " + dataset.additional_data["dataset_title"].upper() + " dataset."
            else:
                log = dataset.additional_data["department"].upper() + " updated " + dataset.additional_data["dataset_title"].upper() + " dataset."

            # dataset.additional_data = {}
            for arg in self.request.arguments():
                if not self.request.POST.get(arg):
                    continue

                if arg.startswith('unindexed_'):  # unindexed_
                    ad_key = arg.replace("unindexed_", "")
                    ad_value = self.request.POST.get(arg)
                    dataset.additional_data[ad_key] = ad_value.strip()

                if arg.startswith('indexed_'):
                    ad_key = arg.replace("indexed_", "")
                    ad_value = self.request.POST.get(arg)

                    if ad_key == "dataset_title":
                        ckan_name = ad_value.lower().replace(" ", "-")
                        dataset.additional_data["dataset_ckan_name"] = ckan_name
                        dataset.additional_data[ad_key] = ad_value
                    else:
                        dataset.additional_data[ad_key] = ad_value

                    if ad_key.lower() == "status":
                        for indexed_data in dataset.indexed_data:
                            if indexed_data.startswith("STATUS->"):
                                dataset.indexed_data.remove(indexed_data)

                    dataset.indexed_data.append(
                        create_indexed_tag(
                            arg, self.request.POST.get(arg)))
            tags = []
            if dataset.tags:
                tags = dataset.tags

            tags += create_tags(self.POST("indexed_dataset_title"))
            tags += create_tags(self.POST("indexed_department"))
            dataset.tags = uniquify(tags)
            dataset.indexed_data = uniquify(dataset.indexed_data)
            dataset.put()

            Logs.add_log(
                data={"action": log, "icon": "arrow-up", "color": "success" },
                uacs_id=dataset.additional_data["uacs_id"],
                user=self.user.key,
                dataset=dataset.key)

            success = "Dataset has been updated."
            success_message(self, success)
            self.redirect("/dataset/" + str(dataset.key.id()))
        else:
            error = "Could not save the update."
            error_message(self, error)
            self.redirect("/dataset/" + str(dataset.key.id()) + "/edit")


class IframeCommentsHandler(BaseHandler):
    def get(self):
        if self.request.get('redirect'):
            self.tv['redirect'] = self.request.get('redirect')
        else:
            self.tv['redirect'] = self.request.referer

        self.tv['dgph_node_id'] = self.request.get('dgph_node_id')
        self.tv['philgeps_org_id'] = self.request.get('philgeps_org_id')
        self.tv['philgeps_bid_reference_number'] = self.request.get('philgeps_bid_reference_number')
        self.tv['philgeps_project_name'] = self.request.get('philgeps_project_name')

        query = APIData.query()
        # query = query.filter(APIData.data_api_status == "APPROVED")
        # query = query.filter(APIData.data_type == "FEEDBACK")

        tag = create_indexed_tag('indexed_philgeps_org_id', self.tv['philgeps_org_id'])
        query = query.filter(APIData.indexed_data == tag)

        tag = create_indexed_tag('indexed_philgeps_bid_reference_number', self.tv['philgeps_bid_reference_number'])
        query = query.filter(APIData.indexed_data == tag)

        tag = create_indexed_tag('indexed_dgph_node_id', self.tv['dgph_node_id'])
        query = query.filter(APIData.indexed_data == tag)

        tag = create_indexed_tag('indexed_type', "FEEDBACK")
        query = query.filter(APIData.indexed_data == tag)

        tag = create_indexed_tag('indexed_status', "APPROVED")
        query = query.filter(APIData.indexed_data == tag)

        self.tv['feedbacks'] = query.fetch(10)

        self.render("frontend/comments-form.html")


class PasswordResetHandler(BaseHandler):
    def get(self):
        """
            Handles the /password/reset endpoint.
            Resets password of the user.
        """
        if self.GET("token") and self.GET("uid"):
            user = User.get_by_id(int(self.GET("uid")))
            if user:
                if user.password_token == self.GET("token"):
                    self.tv["reset"] = True
                    self.tv["token"] = self.GET("token")
                    self.tv["uid"] = self.GET("uid")
                    self.render("frontend/password-reset.html")
                else:
                    error = "You may have clicked an expired link "
                    error += "or mistyped the address."
                    error_message(self, error)
                    self.redirect("/login")
            else:
                error = "Sorry, we couldn't process your request. "
                error += "Please try again."
                error_message(self, error)
                self.redirect("/password/reset")
        else:
            self.render("frontend/password-reset.html")

    def post(self):
        """
            Handles the /password/reset endpoint.
            Resets password of the user.
        """
        if self.POST("email"):
            email = self.POST("email").lower().strip()

            query = User.query()
            query = query.filter(User.current_email == email)
            user = query.get()

            if user:
                user.password_token = generate_token()
                user.put()

                content = {
                    "token": user.password_token,
                    "uid": str(user.key.id())
                }

                send_email(
                    receiver_name=user.first_name,
                    receiver_email=user.current_email,
                    subject="Reset Password",
                    content=content,
                    email_type="password_reset")

                success = "We sent an email to "
                success += self.POST("email") + ". Please open the "
                success += "email and click on the password reset link "
                success += "to reset your password."
                success_message(self, success)
                self.redirect("/password/reset")
            else:
                error = "Sorry, " + self.POST("email")
                error += " does not belong to an existing account."
                error_message(self, error)
                self.redirect("/password/reset")
        elif self.POST("new_password") and self.POST("confirm_password") \
             and self.POST("uid") and self.POST("token"):
            if self.POST("new_password") == self.POST("confirm_password"):
                user = User.get_by_id(int(self.POST("uid")))
                if user:
                    if user.password_token == self.POST("token"):
                        password = hp(user.original_email, self.POST("new_password"))
                        user.password_token = generate_token()
                        user.previous_passwords.append(password)
                        user.password_update = datetime.datetime.now()
                        user.password = password
                        user.put()

                        success = "Your password has been changed. "
                        success += "You can now login."
                        success_message(self, success)
                        self.redirect("/login")
                    else:
                        error = "Sorry, your password reset request has expired."
                        error += " Please create a new request."
                        error_message(self, error)
                        self.redirect("/password/reset")
                else:
                    error = "Sorry, we couldn't process your request. "
                    error += "Please try again."
                    error_message(self, error)
                    self.redirect("/password/reset")
            else:
                error = "Passwords do not match."
                error_message(self, error)
                url = "/password/reset?token=" + self.POST("token")
                url += "&uid=" + self.POST("uid")
                self.redirect(url)
        else:
            error = "Please fill all required fields."
            error_message(self, error)
            self.redirect("/password/reset")


class CRONDatasetCheckHandler(BaseHandler):
    def get(self):
        """
            Handles the /tasks/datasets/check endpoint.
            Sends updates to the ODTF team at exactly 3pm.
        """
        query = Logs.query()
        from_time = datetime.datetime.now() - datetime.timedelta(hours=24)
        query = query.filter(Logs.created_time > from_time)
        query = query.filter(Logs.created_time < datetime.datetime.now())
        query = query.order(-Logs.created_time)
        logs = query.fetch()

        logging.info(query)

        logs_dict = []

        if logs:
            for l in logs:
                l = l.to_object()
                l["url"] = ""
                try:
                    dataset = ndb.Key(urlsafe=l["dataset"]).get()
                    if dataset:
                        l["url"] = CURRENT_URL + "/dataset/" + str(dataset.key.id())
                except Exception, e:
                    logging.exception(e)
                    logging.info("log has no dataset")

                logs_dict.append(l)

        logging.info(logs_dict)

        query = User.query()
        query = query.filter(User.role == "OPENDATAADMIN")
        ODTF = query.fetch()

        logging.info(ODTF)

        if ODTF:
            for od in ODTF:
                send_email(
                    receiver_name=od.first_name,
                    receiver_email=od.current_email,
                    subject="Data Manager Updates",
                    content={"action": logs_dict},
                    email_type="odtf_update")


class ErrorHandler(BaseHandler):
    def get(self, error):
        """
            Handles the 404 errors.
            Shows a 404 error page if page is not found.
        """
        self.tv["show_breadcrumb"] = False
        self.tv["show_add_dataset"] = False
        self.render('frontend/error404.html')


app = webapp2.WSGIApplication([
    routes.DomainRoute(r'<:.*>', [
        webapp2.Route('/', MainHandler),
        webapp2.Route('/dashboard', DashboardHandler),
        webapp2.Route('/login', LoginHandler),
        webapp2.Route('/login/authorize', LoginOauthHandler),
        webapp2.Route(r'/login/verify/<:.*>', VerifyLoginCode),
        webapp2.Route('/logout', LogoutHandler),
        webapp2.Route('/register', RegisterHandler),
        webapp2.Route('/admin/register', AdminRegisterHandler),
        webapp2.Route('/agency/admins', AgencyAdminRegistrationHandler),
        webapp2.Route('/opendata/admins',  OpenDataAdminManageHandler),
        webapp2.Route('/password/reset', PasswordResetHandler),
        webapp2.Route('/register/verify', VerifyRegisterHandler),
        webapp2.Route('/register/verify/send', SendVerificationHandler),
        webapp2.Route('/logs', LogsHandler),
        webapp2.Route('/feedback', FeedbacksHandler),
        webapp2.Route('/api/v1/data', DataApiHandler),
        webapp2.Route('/api/v1/uacs', UACSAPIHandler),
        webapp2.Route('/post/success', PostSuccessHandler),
        webapp2.Route('/dataset/new', CreateDatasetStep1Handler),
        webapp2.Route(r'/dataset/new/<:.*>/step1', CreateDatasetStep1Handler),
        webapp2.Route(r'/dataset/new/<:.*>/step2', CreateDatasetStep2Handler),
        webapp2.Route(r'/dataset/new/<:.*>/step3', CreateDatasetStep3Handler),
        webapp2.Route(r'/resource/<:.*>/edit', ResourceEditHandler),
        webapp2.Route(r'/resource/<:.*>', ResourceDetailsHandler),
        webapp2.Route(r'/dataset/<:.*>/status', DatasetStatusHandler),
        webapp2.Route(r'/dataset/<:.*>/edit', DatasetEditHandler),
        webapp2.Route(r'/dataset/<:.*>', DatasetDetailsHandler),
        webapp2.Route('/iframes/v1/comments', IframeCommentsHandler),
        webapp2.Route('/tasks/datasets/check', CRONDatasetCheckHandler),
        webapp2.Route(r'/<:.*>', ErrorHandler)
    ])
], debug=True)
