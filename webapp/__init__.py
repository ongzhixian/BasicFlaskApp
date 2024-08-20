import os
from datetime import datetime
from uuid import uuid4
from flask import Flask, request, current_app
import json
import logging
# from flask import (
#     Blueprint, flash, g, redirect, render_template, request, url_for
# )


# from logging.config import dictConfig

# dictConfig({
#     'version': 1,
#     'formatters': {'default': {
#         'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s aaaa',
#     }},
#     'handlers': {'wsgi': {
#         'class': 'logging.StreamHandler',
#         'stream': 'ext://flask.logging.wsgi_errors_stream',
#         'formatter': 'default'
#     }},
#     'root': {
#         'level': 'INFO',
#         'handlers': ['wsgi']
#     }
# })


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Configure logging

    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s | %(name)s [%(module)s.%(funcName)s]', datefmt='%H:%M:%S')
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    app.logger.addHandler(ch)

    #from logging.handlers import TimedRotatingFileHandler
    #fh = TimedRotatingFileHandler('webapp.log', when='M', interval=1)
    fh = logging.FileHandler('webapp.log')
    fh.setLevel(logging.DEBUG)
    #fh.setFormatter(formatter)
    fh.setFormatter(JsonLogRecordFormatter()) # default is  '%Y-%m-%d %H:%M:%S,uuu'
    app.logger.addHandler(fh)

    # Remove the default logging handler
    # from flask.logging import default_handler
    # app.logger.removeHandler(default_handler)

    # Configure signal and middleware

    # before_request signal handlers (these will execute in sequence)
    #app.before_request(log_request)
    #

    # after_request signal handlers (these will execute in the reverse order; last one executes first)
    #app.after_request(after_req2)
    app.after_request(add_response_headers)
    
    # Middleware (these will execute in the reverse order; last one executes first)
    # Note: Middlewares will executes first before before_request handlers
    #app.wsgi_app = SimpleMiddleWare(app.wsgi_app)
    app.wsgi_app = CorrelationIdMiddleWare(app.wsgi_app)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'webapp.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    from . import db
    db.init_app(app)

    from . import e2e
    e2e.init_app(app)

    #load_modules(app)
    dynamic_load_modules(app)

    return app


# FUNCTIONS

def dynamic_load_modules(app):
    ignore_list = ['__init__', 'db', 'e2e']
    
    import importlib
    
    with os.scandir('webapp') as dirEntryIterator:
        for entry in dirEntryIterator:
            if entry.is_dir(): continue
            
            file_name, file_extension = os.path.splitext(entry.name)
            if file_extension == '.py' and file_name not in ignore_list:
                module = importlib.import_module(f'.{file_name}', package='webapp')
                app.register_blueprint(module.bp)


def load_modules(app):
    from . import db
    db.init_app(app)
    
    from . import welcome
    app.register_blueprint(welcome.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    #app.add_url_rule('/blog', endpoint='index')
    
    from . import news
    app.register_blueprint(news.bp)
    
    from . import algotrade
    app.register_blueprint(algotrade.bp)
    
    from . import notes
    app.register_blueprint(notes.bp)
    
    from . import cloud_assets
    app.register_blueprint(cloud_assets.bp)
    
    from . import tools
    app.register_blueprint(tools.bp)
    
    from . import users
    app.register_blueprint(users.bp)
    
    from . import roles
    app.register_blueprint(roles.bp)
    
    from . import file_upload
    app.register_blueprint(file_upload.bp)

    from . import issues
    app.register_blueprint(issues.bp)

    from . import tool_manager
    app.register_blueprint(tool_manager.bp)
    
    from . import fixed_deposit
    app.register_blueprint(fixed_deposit.bp)


def serializer(obj): 
    if isinstance(obj, datetime): 
        return obj.isoformat() 
    raise TypeError("Type not serializable") 


# MIDDLEWAREs

class CorrelationIdMiddleWare(object):
    """
    Adds a Correlation ID (UUID4) to `request.environ`
    
    Unlike .NET we cannot add headers directly to the request headers 
    (request.header is an werkzeug.datastructures.EnvironHeaders which is immutable!)
    So instead, of adding request headers directly, we add the X-Correlation-ID to `request.environ`
    (since `request.environ` has all these stuff)

    Note: Middleware seems to have a higher execution precedence over before_request hooks
    (that is to say it will execute first followed by before_request functions)
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if 'X-Correlation-ID' not in environ:
            environ['X-Correlation-ID'] = str(uuid4())
        if 'Request-Id' not in environ:
            environ['Request-Id'] = str(uuid4())
        return self.app(environ, start_response)


# before_request HANDLERs

def log_request():
    #print(f'Handling url {request.url} -- {len(request.headers)}')
    #request.environ['XXXX-YYYY-ZZZ'] = 'asd'
    #current_app.logger.info("Receive %s", request)
    pass


# after_request HANDLERs

def add_response_headers(response):
    if 'X-Correlation-ID' in request.environ:
        response.headers['X-Correlation-ID'] = request.environ['X-Correlation-ID']
    if 'Request-Id' in request.environ:
        response.headers['Request-Id'] = request.environ['Request-Id']
    return response
    


# STRUCTURED LOGGING

class StructuredMessage:
    def __init__(self, message, /, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return '%s >>> %s' % (self.message, json.dumps(self.kwargs))

class JsonLogRecordFormatter(logging.Formatter):
    """Formatter to dump error message into JSON"""
    from logging import LogRecord
    

    def format(self, record: LogRecord) -> str:
        # print(request)
        record_dict = {
            "level": record.levelname,
            "date": self.formatTime(record, datefmt='%Y-%m-%d %H:%M:%S%z'),
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "asctime": record.asctime
        }
        for arg in record.args:
            record_dict[arg] = record.args[arg]
        if 'X-Correlation-ID' in request.environ:
            record_dict['X-Correlation-ID'] = request.environ['X-Correlation-ID']
        if 'Request-Id' in request.environ:
            record_dict['Request-Id'] = request.environ['Request-Id']

        return json.dumps(record_dict)

    # import pytz
    # def formatTime(self, record, datefmt=None):
    #     dt = datetime.fromtimestamp(record.created, tz=pytz.UTC)
    #     if datefmt:
    #         s = dt.strftime(datefmt)
    #     else:
    #         s = dt.isoformat()
    #     return s

    # Reference: logging.Formatter's formatTime method looks like this:
    # (or why we cannot easily customize microseconds part of the formatter):
    # def formatTime(self, record, datefmt=None):
    #     ct = self.converter(record.created)
    #     if datefmt:
    #         s = time.strftime(datefmt, ct)
    #     else:
    #         t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
    #         s = "%s,%03d" % (t, record.msecs)
    #     return s


# Threadsafe

# class ThreadSafeCounter:
#     def __init__(self):
#         self.value = 0
#         self.lock = threading.Lock()
#         self.last_reset = datetime.now()

#     def increment(self):
#         with self.lock:
#             current_time = datetime.now()
#             if (current_time - self.last_reset).seconds >= 60:
#                 self.value = 0
#                 self.last_reset = current_time
#             self.value += 1
#             return self.value

# SAMPLE CODE; 

class SimpleMiddleWare(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        print('SimpleMiddleWare do somethign')
        return self.app(environ, start_response)

def sample_before_request_handler():
    #print(f'Handling url {request.url} -- {len(request.headers)}')
    #request.environ['XXXX-YYYY-ZZZ'] = 'asd'
    pass
    

