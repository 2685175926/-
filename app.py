import os
from hmac import compare_digest

import requests
from flask import Flask, Response, jsonify, render_template, request


TARGET_HOST = "https://ad.adintl.cn"
TIMEOUT_SECONDS = 30

app = Flask(__name__)


@app.before_request
def require_basic_auth():
    username = os.environ.get("SITE_USERNAME")
    password = os.environ.get("SITE_PASSWORD")
    if not username or not password:
        return None

    auth = request.authorization
    if (
        auth
        and compare_digest(auth.username or "", username)
        and compare_digest(auth.password or "", password)
    ):
        return None

    return Response(
        "Authentication required",
        401,
        {"WWW-Authenticate": 'Basic realm="Octopus Monitor"'},
    )


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/healthz")
def healthz():
    return jsonify({"ok": True})


@app.route("/api/<path:api_path>", methods=["GET", "POST", "OPTIONS"])
def proxy(api_path):
    if request.method == "OPTIONS":
        return add_cors_headers(Response(status=204))

    target_url = f"{TARGET_HOST}/{api_path}"
    headers = build_forward_headers()

    try:
        upstream = requests.request(
            method=request.method,
            url=target_url,
            params=request.args,
            data=request.get_data() if request.method == "POST" else None,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        response = jsonify({"success": False, "message": str(exc)})
        response.status_code = 502
        return add_cors_headers(response)

    content_type = upstream.headers.get("Content-Type", "application/json")
    response = Response(
        upstream.content,
        status=upstream.status_code,
        content_type=content_type,
    )
    return add_cors_headers(response)


def build_forward_headers():
    forwarded = {
        "Accept": request.headers.get("Accept", "application/json, text/plain, */*"),
        "Referer": "https://ad.adintl.cn/dsp/materialReport",
        "tenant-id": request.headers.get("tenant-id", "0"),
        "advertiserId": request.headers.get("advertiserId", "2099"),
    }

    for name in ("X-Access-Token", "X-Sign", "X-TIMESTAMP", "Content-Type"):
        value = request.headers.get(name)
        if value:
            forwarded[name] = value

    return forwarded


def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = (
        "Content-Type, Accept, X-Access-Token, X-Sign, X-TIMESTAMP, "
        "advertiserId, tenant-id"
    )
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8899"))
    app.run(host="0.0.0.0", port=port)
