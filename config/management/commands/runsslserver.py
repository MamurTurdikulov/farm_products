
# config/management/commands/runsslserver.py
import os
import ssl
from wsgiref.simple_server import make_server, WSGIRequestHandler, WSGIServer
from django.core.management.base import BaseCommand, CommandError
from django.core.wsgi import get_wsgi_application

class SSLWSGIServer(WSGIServer):
    def __init__(self, server_address, RequestHandlerClass, certfile, keyfile):
        super().__init__(server_address, RequestHandlerClass)
        self.socket = ssl.wrap_socket(
            self.socket,
            certfile=certfile,
            keyfile=keyfile,
            server_side=True,
        )

class Command(BaseCommand):
    help = "Run an HTTPS Django dev server."

    def add_arguments(self, parser):
        parser.add_argument("addrport", nargs="?", help="address:port")
        parser.add_argument("--cert", required=True, help="Path to cert PEM")
        parser.add_argument("--key", required=True, help="Path to key PEM")

    def handle(self, *args, **opts):
        addrport = opts.get("addrport") or "127.0.0.1:8000"
        cert = opts["cert"]
        key = opts["key"]

        if not os.path.exists(cert):
            raise CommandError(f"Cert not found: {cert}")
        if not os.path.exists(key):
            raise CommandError(f"Key not found: {key}")

        if ":" in addrport:
            host, port = addrport.split(":")
            host = host or "127.0.0.1"
            port = int(port)
        else:
            host = "127.0.0.1"
            port = int(addrport)

        app = get_wsgi_application()

        self.stdout.write(
            f"Starting HTTPS server at https://{host}:{port}/ (DEV ONLY)"
        )

        try:
            httpd = make_server(
                host, port, app,
                server_class=SSLWSGIServer,
                handler_class=WSGIRequestHandler,
                certfile=cert, keyfile=key
            )
        except TypeError:
            httpd = SSLWSGIServer((host, port), WSGIRequestHandler, cert, key)
            httpd.set_app(app)

        httpd.serve_forever()
