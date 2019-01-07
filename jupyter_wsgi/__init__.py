import asyncio
import getpass
from aiohttp import web
from aiohttp_wsgi import WSGIHandler
from aiohttp.web_runner import TCPSite
from IPython import display

class AppViewer(object):

    def __init__(self, base_url, port=8050):
        self.web_app = web.Application()
        self.port = port
        self.requests_pathname_prefix = '/user/{}/proxy/{}/'.format(getpass.getuser(), port)
        self.url = '{}/{}'.format(base_url, self.requests_pathname_prefix)
        self.site = None
        
    async def show(self, wsgi_app, width=300, height=300):
        if self.site is None:
            self.wsgi_handler = WSGIHandler(wsgi_app)
            self.resource = self.web_app.router.add_route("*", "/{path_info:.*}", self.wsgi_handler)
            self.runner = web.AppRunner(self.web_app)
            await self.runner.setup()
            self.site = TCPSite(self.runner, port=self.port)
        await self.site.start()
        display.display(display.IFrame(self.url, width, height))

    async def stop(self):
        await self.site.stop()

    async def terminate(self):
        await self.site.stop()
        
