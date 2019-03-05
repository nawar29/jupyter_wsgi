from tornado import web
from notebook.base.handlers import IPythonHandler
from notebook.extensions import SYSTEM_CONFIG_PATH
import json

class WSGIHandler(IPythonHandler):

    def initialize(self, app):
        self.app = app

    @web.authenticated
    async def invoke_wsgi(self):
        self.app(self.request)
        self.finish()

    def get(self, *args):
        return self.invoke_wsgi()

    def post(self, *args):
        return self.invoke_wsgi()

    def put(self, *args):
        return self.invoke_wsgi()

    def head(self, *args):
        return self.invoke_wsgi()

    def delete(self, *args):
        return self.invoke_wsgi()

    def connect(self, *args):
        return self.invoke_wsgi()

    def options(self, *args):
        return self.invoke_wsgi()

    def trace(self, *args):
        return self.invoke_wsgi()

    def check_xsrf_cookie(self):
        pass # Delegate xsrf checking to extension

class IndexHandler(IPythonHandler):
    _endpoints = []
    _modules = []
    _name = 'Webapps'
    _extension_path = 'wsgi'
    _base_url = None
    _bad_yaml = False

    @classmethod
    def set_bad_yaml(cls, bad_yaml):
        cls._bad_yaml = bad_yaml

    @classmethod
    def set_name(cls, name):
        cls._name = name

    @classmethod
    def set_extension_path(cls, extension_path):
        cls._extension_path = extension_path

    @classmethod
    def set_base_url(cls, extension_path):
        cls._base_url = extension_path

    @classmethod
    def add_module(cls, mod):
        cls._modules.append(mod)

    @classmethod
    def add_endpoint(cls, url, name, module):
        cls._endpoints.append({'url':url,'name':name,'mod':module})

    def _make_html_body(self):
        body = f'''No wsgi extensions found<br/>'''
        if self._bad_yaml:
            body = f'''No wsgi extensions found<br/>
                       Make sure there a yaml config in: <br/>
                       { '<br/>'.join(SYSTEM_CONFIG_PATH)}
                       '''
        elif len(self._endpoints) > 0:
            ul = '<ul>'
            for ep in self._endpoints:
                ul += f"<li><a href='{ep['url']}'>{ep['name']}</a></li>"
            ul += '</ul>'
            body = f'<H1>{self._name}:</H1>{ul}</body>'
        return f'<html><body>{body}</body></html>'

    def _make_json_body(self):
        return json.dumps( {'name': self._name,
                            'endpoints': self._endpoints })

    @web.authenticated
    async def get(self):
        is_rest = self.get_argument('json', False)
        if is_rest:
            body = self._make_json_body()
            self.set_header("Content-Type", "application/json")
        else:
            body = self._make_html_body()
            self.set_header("Content-Type", "text/html")
        self.finish(body)
