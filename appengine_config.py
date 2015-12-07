from gaesessions import SessionMiddleware
from request import global_vars
import datetime


def initialize_global_vars():
    global_vars.datetime_now = datetime.datetime.now()
    adjusted = global_vars.datetime_now + datetime.timedelta(hours=8)
    global_vars.datetime_now_adjusted = adjusted
    global_vars.user = None


def webapp_add_wsgi_middleware(app):
    initialize_global_vars()
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
    cookie_key = "XjDzoCInuFhX1Jt3ZrSSNPQlu6rHLPJUe5DIeujJzZQwQRm7ZRPyOdQZoFzSi5y6CGOprcXgRCaXjDdHnl2RXOVak6fMyk6WJmJ8j9wayI8JoNznIGw7md9XurD7DheB"
    app = SessionMiddleware(app, cookie_key=cookie_key)
    return app
