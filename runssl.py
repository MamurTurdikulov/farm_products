
import os, sys, ssl
from wsgiref.simple_server import make_server, WSGIRequestHandler, WSGIServer

def main():
    if "--cert" not in sys.argv or "--key" not in sys.argv:
        print("Usage: python runssl.py host:port --cert cert.pem --key key.pem")
        sys.exit(1)

    addr = sys.argv[1]
    cert = sys.argv[sys.argv.index("--cert")+1]
    key = sys.argv[sys.argv.index("--key")+1]

    if ":" in addr:
        host, port = addr.split(":")
        host = host or "127.0.0.1"
        port = int(port)
    else:
        host = "127.0.0.1"
        port = int(addr)

    if not os.path.exists(cert):
        print("Cert not found:", cert); sys.exit(1)
    if not os.path.exists(key):
        print("Key not found:", key); sys.exit(1)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()

    class SSLWSGIServer(WSGIServer):
        def __init__(self, addr, handler):
            super().__init__(addr, handler)
            self.socket = ssl.wrap_socket(
                self.socket, certfile=cert, keyfile=key, server_side=True
            )

    print(f"Starting HTTPS server: https://{host}:{port} (DEV ONLY)")
    httpd = make_server(host, port, app, server_class=SSLWSGIServer, handler_class=WSGIRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
