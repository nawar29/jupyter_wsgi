from tornado import web
from notebook.base.handlers import IPythonHandler

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
    
    @classmethod
    def add_endpoint(cls, endpoint, title, import_name):
        cls._endpoints.append((endpoint, title, import_name))
        
    @web.authenticated
    async def get(self):
        if len(self._endpoints) > 0:
            ul = '<ul>'
            for endpoint, title, mod_name in self._endpoints:            
                ul += f"<li><a href='{endpoint}'>{title}</a></li>"
            ul += '</ul>'
            body = f'<html><body><p>{path}</p>{ul}</body></html>'
        else:
            body = f'<html><body>No wsgi extensions found</body></html>'
            self.set_header("Content-Type", "text/html")
        self.finish(body)
        
