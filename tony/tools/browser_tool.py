from __future__ import annotations

import socket
import webbrowser
from urllib.parse import urlparse


class BrowserTool:
    TRUSTED_HOSTS = {"localhost", "127.0.0.1"}

    def open_url(self, url: str) -> str:
        if not self.is_safe_url(url):
            return "External URLs require approval and are not auto-opened by Tony V3."
        webbrowser.open(url)
        return f"Opening browser: {url}"

    def search_web(self, query: str) -> str:
        return f"Web search is a placeholder in V3. Query saved locally only: {query}"

    def open_localhost(self, port: int) -> str:
        url = f"http://localhost:{port}"
        webbrowser.open(url)
        return f"Opening localhost: {url}"

    def check_localhost(self, port: int) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.5)
            result = sock.connect_ex(("127.0.0.1", int(port)))
        if result == 0:
            return f"localhost:{port} is accepting connections."
        return f"localhost:{port} is not accepting connections."

    def is_safe_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and parsed.hostname in self.TRUSTED_HOSTS
