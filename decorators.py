from functions import *
from settings import *
import urllib


def required_permission(permissions=[]):  # this is a handler level decorator
    def decorator(fn):
        def wrapper(self, *args, **kwargs):
            if not self.user.permissions:
                self.render("frontend/error404.html")
                return

            # this will overide superadmin, will still go through...
            if self.user.permissions in permissions:
                return fn(self, *args, **kwargs)

            self.render('frontend/no-access.html')
            return

        return wrapper
    return decorator


def csrf_protect(fn):
    '''So we can decorate any RequestHandler with #@csrf_protect'''
    def wrapper(self, *args, **kwargs):
        if not self.user:
            logging.info('no user')
            self.error(400)
            return
        else:
            if self.user:
                if self.user.csrf_token == self.request.get('token'):
                    return fn(self, *args, **kwargs)
            logging.info('wrong token')
            self.error(400)
            return
    return wrapper


def login_required(fn):
    '''So we can decorate any RequestHandler with #@admin_required'''
    def wrapper(self, *args, **kwargs):
        if not self.user:
            if self.request.get('redirect'):
                self.redirect(get_login_url(
                    self.request.uri[0:(self.request.uri.find('?'))],
                    "Please Log In"))
                return
            else:
                self.redirect(get_login_url(self.request.uri, "Please Log In"))
                return
        else:
            return fn(self, *args, **kwargs)

    return wrapper


def allowed_users(permissions=[]):  # this is a handler level decorator
    def decorator(fn):
        def wrapper(self, *args, **kwargs):
            if self.user:
                if self.user.role in permissions:
                    return fn(self, *args, **kwargs)

                self.tv["error_PAGE"] = True
                self.error(404)
                self.render('frontend/error404.html')
                return
            else:
                if self.request.get('redirect'):
                    uri = self.request.uri.find('?')
                    self.redirect(get_login_url(
                        self.request.uri[0:(uri)], "Please Log In"))
                else:
                    self.redirect(get_login_url(
                        self.request.uri, "Please Log In"))

        return wrapper
    return decorator
