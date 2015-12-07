import re
import email
import Cookie
import calendar
import datetime


def _utf8(s):
    if isinstance(s, unicode):
        return s.encode("utf-8")
    assert isinstance(s, str)
    return s


def cookies(self):
    """A dictionary of Cookie.Morsel objects."""
    if not hasattr(self, "_cookies"):
        self._cookies = Cookie.BaseCookie()
        if "Cookie" in self.request.headers:
            try:
                self._cookies.load(self.request.headers["Cookie"])
            except:
                self.clear_all_cookies()
    return self._cookies


def get_cookie(self, name, default=False):
    """Gets the value of the cookie with the given name,else default."""
    if name in self.request.cookies:
        return self.request.cookies[name]
    return default


def set_cookie(
        self, name, value, expires=None,
        domain=None, expires_days=None, path="/"):
    """Sets the given cookie name/value with the given options."""
    name = _utf8(name)
    value = _utf8(value)

    # Don't let us accidentally inject bad stuff
    if re.search(r"[\x00-\x20]", name + value):
        raise ValueError("Invalid cookie %r:%r" % (name, value))

    new_cookie = Cookie.BaseCookie()
    new_cookie[name] = value
    if domain:
        new_cookie[name]["domain"] = domain
    if expires_days is not None and not expires:
        expires = datetime.datetime.utcnow()
        expires += datetime.timedelta(days=expires_days)
    if expires:
        timestamp = calendar.timegm(expires.utctimetuple())
        new_cookie[name]["expires"] = email.utils.formatdate(
            timestamp, localtime=False, usegmt=True)
    if path:
        new_cookie[name]["path"] = path
    for morsel in new_cookie.values():
        self.response.headers.add_header(
            'Set-Cookie', morsel.OutputString(None))


def clear_cookie(self, name, path="/", domain=None):
    """Deletes the cookie with the given name."""
    expires = datetime.datetime.utcnow() - datetime.timedelta(days=365)
    set_cookie(self, name, value="", path=path, expires=expires, domain=domain)
