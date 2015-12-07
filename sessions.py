from models import Session, User, LoginCode
import uuid
import os
import datetime
import time
import logging
from functions import random_string, generate_token, generate_uuid
# from user_exceptions import *
from google.appengine.ext import ndb
LIFETIME = datetime.timedelta(hours=8)


class SessionHandler(object):
    def __init__(self, user=None):
        self.user = user
        self.datenow = (datetime.datetime.now() + datetime.timedelta(hours=8))
        from gaesessions import get_current_session
        self._sess = get_current_session()
        if "user" in self._sess:
            self._s_id = self._sess["user"]
        else:
            self._s_id = None
        logging.info(self._s_id)

    @property
    def sess(self):
        return self._sess

    @sess.setter
    def sess(self, v):
        self._sess = v

    @property
    def s_id(self):
        return self._s_id

    @s_id.setter
    def s_id(self, v):
        self._s_id = v

    @property
    def session(self):
        return Session.get_by_id(self.s_id)

    @property
    def session_id(self):
        return self._s_id

    @property
    def user_id(self):
        return self.session["user"] if "user" in self.session else None

    @property
    def isActive(self):
        if self.s_id:
            sess = Session.get_by_id(self.s_id)
            if sess:
                if sess.status:
                    return True

        return False

    @property
    def owner(self):
        if self.isActive:
            if self.s_id:
                s = Session.get_by_id(self.s_id)
                if s:
                    return s.owner.get()
        return None

    @property
    def login_token(self):
        if self.s_id:
            sess = Session.get_by_id(self.s_id)
            if sess:
                return sess.login_token

        return None

    @property
    def data(self):
        if self.s_id:
            s = Session.get_by_id(self.s_id)
            if s:
                user = s.owner.get()
                d = user.toObject(expanded=True)
                d["expires"] = time.mktime(self.session.expires.timetuple())
        return None

    # METHODS

    def login(self):
        logging.info("login")
        if not self.user or type(self.user) is not User:
            raise SessionError()

        logging.info(self.session_id)
        if self.sess.is_active():
            self.logout()

        results = Session.query(
            Session.owner == self.user.key,
            Session.status == True).fetch(20)
        items = []
        for result in results:
            result.status = False
            items.append(result)
        ndb.put_multi(items)

        sessionkey = str(uuid.uuid4()) + random_string(20)
        session = Session(id=sessionkey)
        session.owner = self.user.key
        expires = datetime.datetime.now()
        expires += datetime.timedelta(hours=16)
        session.expires = expires
        session.ip_address = os.environ.get('REMOTE_ADDR')
        session.user_agent = os.environ.get('HTTP_USER_AGENT')
        session.put()

        logging.info(session)

        from gaesessions import get_current_session
        # s = get_current_session
        self.sess.start(
            expiration_ts=time.mktime((self.datenow + LIFETIME).timetuple()))
        self.sess["user"] = sessionkey
        logging.info(sessionkey)
        self.s_id = sessionkey
        self.sess = get_current_session()

        logging.info(self.sess)

    def logout(self):
        if self._s_id:
            s = Session.get_by_id(self._s_id)
            if s:
                s.status = False
                s.put()

        from gaesessions import get_current_session
        session = get_current_session()
        session.terminate()
        logging.info("logout")


    def generate_login_code(self):
        logging.info(self.s_id)
        if self.isActive:
            query = LoginCode.query()
            query = query.filter(LoginCode.expiry > datetime.datetime.now())
            query = query.filter(LoginCode.session == self.session.key)
            login_code = query.get()
            if login_code:
                return a.login_code
            else:
                code = generate_uuid() + generate_uuid()
                logincode = LoginCode(id=code)
                logincode.session = self.session.key
                logincode.expiry = self.session.expires
                logincode.put()

                return code
        logging.info("giveme_appcode returned `None` because the session has not been logged in:" + self.user.username)
        return None


def force_logout():
    from gaesessions import get_current_session
    session = get_current_session()
    session.terminate()
