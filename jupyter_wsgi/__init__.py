import asyncio
import logging
import getpass
import traceback
from aiohttp import web
from aiohttp_wsgi import WSGIHandler
from aiohttp.web_runner import TCPSite
from IPython import display

class AppViewer(object):

    _exception_ = ''
    _running = False
    site = None
    
    def __init__(self, base_url, port=8050):
        self.web_app = web.Application()
        self.port = port
        self.requests_pathname_prefix = '/user/{}/proxy/{}/'.format(getpass.getuser(), port)
        self.url = '{}/{}'.format(base_url, self.requests_pathname_prefix)

    def setup_dash(self, dash_app, debug=False, logger=None):
        dash_app.config.update({'requests_pathname_prefix': self.requests_pathname_prefix})
        if debug:
            dash_app.enable_dev_tools(debug=True)
            dash_app.server.logger.setLevel(logging.DEBUG)
        if logger is not None:
            dash_app.server.logger.addHandler(logger)
    
    async def setup(self, wsgi_app):
         if self.site is None:
            self.wsgi_handler = WSGIHandler(wsgi_app)
            self.resource = self.web_app.router.add_route("*", "/{path_info:.*}", self.wsgi_handler)
            self.runner = web.AppRunner(self.web_app)
            await self.runner.setup()
            self.site = TCPSite(self.runner, port=self.port)

    async def show(self, wsgi_app, width=300, height=300):
        await self.setup(wsgi_app)
        if not self._running:            
            await self.site.start()
            self._running = True        
        self.iframe_dh = display.display(display_id=True)
        self.iframe_dh.display( display.IFrame(self.url, width, height) )
        self.exception_dh = display.display(display_id=True)
        self.exception_dh.display(display.Code(self._exception_, language='python'))
        
    async def stop(self):
        await self.site.stop()
        self._running = False

    async def terminate(self):
        await self.stop()

    def handle_exceptions(self, the_type):
        def notenook_decorate(func):
            def wrapper(arg):
                rval = the_type()
                try:
                    rval = func(arg)
                except Exception as e:
                    self._exception_ = traceback.format_exc()
                else:
                    self._exception_ = ''
                self.exception_dh.update( display.Code(self._exception_, language='python') )
                return rval
            return wrapper
        return notenook_decorate
