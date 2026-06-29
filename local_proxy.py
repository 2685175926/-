import http.server
import urllib.request
import urllib.parse
import json
import ssl
import os

TARGET_HOST = "https://ad.adintl.cn"
PUSHPLUS_SEND_URL = "https://www.pushplus.plus/send"
PORT = 8899

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{self.command}] {args[0]}")

    def do_GET(self):
        if self.path == "/" or self.path == "/login.html":
            self.send_file("login.html", "text/html")
        elif self.path == "/ad_monitor.html":
            self.send_file("ad_monitor.html", "text/html")
        elif self.path == "/proxy.py":
            self.send_error(403)
        elif self.path.startswith("/api/"):
            api_path = self.path[4:]
            self.forward("GET", api_path)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/pushplus/send":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else None
            self.forward_pushplus(body)
        elif self.path.startswith("/api/"):
            api_path = self.path[4:]
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else None
            self.forward("POST", api_path, body)
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept, X-Access-Token, X-Sign, X-TIMESTAMP, advertiserId, tenant-id")
        self.end_headers()

    def forward(self, method, path, body=None):
        url = TARGET_HOST + path if path.startswith("/") else TARGET_HOST + "/" + path
        req = urllib.request.Request(url, data=body, method=method)
        token = self.headers.get("X-Access-Token")
        if token:
            req.add_header("X-Access-Token", token)
        xsign = self.headers.get("X-Sign")
        if xsign:
            req.add_header("X-Sign", xsign)
        xts = self.headers.get("X-TIMESTAMP")
        if xts:
            req.add_header("X-TIMESTAMP", xts)
        if body:
            req.add_header("Content-Type", "application/json;charset=UTF-8")
        req.add_header("Accept", "application/json, text/plain, */*")
        req.add_header("Referer", "https://ad.adintl.cn/dsp/materialReport")
        req.add_header("advertiserId", "2099")
        req.add_header("tenant-id", "0")
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self.send_header("Access-Control-Allow-Origin", "*")
                ct = resp.headers.get("Content-Type", "application/json")
                self.send_header("Content-Type", ct)
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "message": str(e)}, ensure_ascii=False).encode("utf-8"))

    def forward_pushplus(self, body=None):
        req = urllib.request.Request(PUSHPLUS_SEND_URL, data=body, method="POST")
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/json;charset=UTF-8")
        try:
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self.send_header("Access-Control-Allow-Origin", "*")
                ct = resp.headers.get("Content-Type", "application/json")
                self.send_header("Content-Type", ct)
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"code": 500, "success": False, "message": str(e)}, ensure_ascii=False).encode("utf-8"))

    def send_file(self, filename, ct):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{ct}; charset=utf-8")
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, f"File {filename} not found")

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), ProxyHandler)
    print("=" * 50)
    print(f"  Local Proxy: http://localhost:{PORT}")
    print(f"  Two files needed: proxy.py + login.html")
    print("=" * 50)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
