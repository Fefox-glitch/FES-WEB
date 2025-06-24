from flask import Flask, request, jsonify
from flask import after_this_request

def apply_security_headers(app: Flask):
    @app.after_request
    def set_security_headers(response):
        # Enforce HTTPS
        if request.scheme != 'https':
            url = request.url.replace('http://', 'https://', 1)
            return jsonify({"message": "Please use HTTPS"}), 301

        # Security headers
        response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=()'
        return response

def register_security(app: Flask):
    apply_security_headers(app)
