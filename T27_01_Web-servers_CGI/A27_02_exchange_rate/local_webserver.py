""" Створюємо локальний веб-сервер.

Для того щоб зайти на нього потрібно запустити цей файл і
перейти у веб-браузері за такою адресою:
localhost:8000
або за явною IP адресою
127.0.0.1:8000
"""

# Знаходиться у головній директорії
from http.server import HTTPServer, CGIHTTPRequestHandler


class RequestHandler(CGIHTTPRequestHandler):

    def do_GET(self) -> None:
        if self.path.startswith("/templates") or self.path.startswith("/data"):
            self.send_error(403, "FORBIDDEN")
        else:
            super().do_GET()


HOST = ""
PORT = 8000

if __name__ == '__main__':
    print("=== Local webserver ===")
    HTTPServer((HOST, PORT), RequestHandler).serve_forever()
