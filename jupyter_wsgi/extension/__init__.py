import yaml
import os.path
import importlib
import signal
from contextlib import contextmanager
from notebook.utils import url_path_join
from notebook.extensions import SYSTEM_CONFIG_PATH
from tornado.wsgi import WSGIContainer
from tornado.log import access_log, app_log
from .handlers import WSGIHandler, IndexHandler


@contextmanager
def timeout(time):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout).
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError

def _jupyter_server_extension_paths():
    return [{
        'module': 'jupyterlab_wsgi',
    }]

def load_jupyter_server_extension(nb_server_app):
    web_app = nb_server_app.web_app
    jupyter_base_url = web_app.settings['base_url']    
    extension_path = 'wsgi'
    wsgi_modules = []
    debug = False
    
    for p in SYSTEM_CONFIG_PATH:
        try:
            yamlfn = os.path.join(p, 'jupyter_wsgi.yaml')
            with open(yamlfn) as fp:
                jupyter_wsgi_conf = yaml.load(fp)                
        except:
            app_log.warning(f'Failed to load {yamlfn}')
        else:
            app_log.info(f'Loaded {yamlfn}')
            extension_path = jupyter_wsgi_conf.get('extension_path', 'wsgi')
            wsgi_modules = jupyter_wsgi_conf.get('wsgi_modules', [])
            debug = jupyter_wsgi_conf.get('debug', False)
            break

    root_endpoint = url_path_join(jupyter_base_url, extension_path)

    IndexHandler.set_extension_path(root_endpoint)
    IndexHandler.set_base_url(jupyter_base_url)    
    
    handlers = []
    for import_name in wsgi_modules:
        app_log.warning( f'Loading {import_name}' )
        try:
            mod = importlib.import_module(f'{import_name}.extension')
            endpoint = url_path_join( root_endpoint, import_name.split('.')[-1] +'/')
            environ = dict(endpoint=endpoint, debug=debug, extension_title=None )
            with timeout(3):
                app = mod.setup( environ )
            
            if app is None:
                app_log.warning( f'Failed to load {import_name} at {endpoint}' )

            else:
                IndexHandler.add_endpoint( endpoint, getattr(mod, 'title', import_name), import_name )           
                handlers.append( (f'{endpoint}.*$', WSGIHandler, dict(app=WSGIContainer(app))) )
                app_log.info( f'Loaded {import_name} at {endpoint}' )  
        except:
            app_log.exception("Error loading server extension %s", import_name)

    app_log.info( f'Serving wsgi index at {root_endpoint}' )  
    handlers.append( (root_endpoint, IndexHandler)  )
    web_app.add_handlers('.*$', handlers )

