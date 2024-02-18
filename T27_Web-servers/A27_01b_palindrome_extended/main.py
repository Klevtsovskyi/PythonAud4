import urllib.parse


def is_palindrome(string):
    """ Повертає True, якщо рядок string є паліндромом,
    або False в іншому випадку.
    """
    s = ""
    for ch in string:
        if ch.isalpha():
            s += ch.lower()
    return s == s[::-1]


def application(environ, start_response):
    path = environ.get("PATH_INFO", "").lstrip("/")
    query_string = environ.get("QUERY_STRING")

    if path == "":
        start_response("200 OK", [("Content-type", "text/html; charset=utf-8"), ])
        with open("templates/palindrome.html", encoding="utf-8") as f:
            content = f.read()

    elif path == "favicon.ico":
        start_response("200 OK", [("Content-type", "image/x-icon")])
        with open("favicon.ico", "rb") as f:
            return [f.read()]

    elif path == "style.css":
        start_response("200 OK", [("Content-type", "text/css")])
        with open("styles/style.css", encoding="utf-8") as f:
            content = f.read()

    elif path == "palindrome":
        query_params = urllib.parse.parse_qs(query_string, encoding="utf-8")
        string = query_params["string"][0] if "string" in query_params else ""
        result = f"<span>{string}</span> - це{'' if is_palindrome(string) else ' не'} паліндром!"
        start_response("200 OK", [("Content-type", "text/plain; charset=utf-8"), ])
        content = result

    else:
        start_response("404 NOT FOUND", [("Content-type", "text/html; charset=utf-8"), ])
        with open("templates/error_404.html", encoding="utf-8") as f:
            content = f.read()

    return [bytes(content, encoding="utf-8")]


HOST = ""
PORT = 8997

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server(HOST, PORT, application)
    print(f"Local webserver is running at http://localhost:{PORT}")
    httpd.serve_forever()
