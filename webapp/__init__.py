import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
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

