from flask import Flask, request, jsonify, send_file, render_template_string
import os
import time
import secrets
from datetime import datetime
from crypto_utils import AES256FileEncryptor
from signed_urls import generate_signed_url, verify_signed_url
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

UPLOAD_FOLDER = 'uploads'
ENCRYPTED_FOLDER = 'encrypted_files'
ENCRYPTION_PASSWORD = "InterneeSecure2025!"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv', 'png', 'jpg', 'xlsx'}

encryptor = AES256FileEncryptor(ENCRYPTION_PASSWORD)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Internee.pk | CryptoVault File Exchange</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Consolas, monospace;
            background: #0d1117;
            background-image:
                linear-gradient(rgba(0,255,170,0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,255,170,0.04) 1px, transparent 1px);
            background-size: 24px 24px;
            color: #c9d1d9;
            margin: 0;
            padding: 40px 20px;
        }
        .wrap { max-width: 900px; margin: 0 auto; }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }
        .topbar h1 {
            font-size: 22px;
            color: #00ffaa;
            margin: 0;
            letter-spacing: 1px;
        }
        .topbar h1 span { color: #6e7681; font-weight: normal; }

        .pulse {
            display: inline-block;
            width: 9px; height: 9px;
            background: #00ffaa;
            border-radius: 50%;
            margin-right: 6px;
            box-shadow: 0 0 8px #00ffaa;
            animation: blink 1.4s infinite;
        }
        @keyframes blink { 50% { opacity: 0.3; } }

        .card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 22px;
            margin-bottom: 20px;
        }
        .card-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }
        .card-head h2 {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #8b949e;
            margin: 0;
        }
        .tag {
            font-size: 11px;
            padding: 3px 9px;
            border-radius: 4px;
            background: rgba(0,255,170,0.1);
            color: #00ffaa;
            border: 1px solid rgba(0,255,170,0.3);
        }

        .badges { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 4px; }
        .badge {
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 4px;
            background: #21262d;
            color: #58a6ff;
            border: 1px solid #30363d;
        }

        .dropzone {
            border: 2px dashed #30363d;
            border-radius: 8px;
            padding: 28px;
            text-align: center;
            color: #8b949e;
            margin-bottom: 14px;
        }

        input[type="file"] {
            width: 100%;
            padding: 8px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 5px;
            color: #c9d1d9;
            margin-bottom: 12px;
        }
        button {
            width: 100%;
            padding: 11px;
            background: #00ffaa;
            color: #0d1117;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 14px;
            cursor: pointer;
            letter-spacing: 0.5px;
        }
        button:hover { background: #00e69a; }
        button.secondary {
            background: transparent;
            color: #58a6ff;
            border: 1px solid #30363d;
        }

        .alert {
            border-left: 3px solid #00ffaa;
            background: rgba(0,255,170,0.06);
            padding: 12px 16px;
            border-radius: 4px;
            font-size: 13px;
            margin-top: 14px;
            word-break: break-all;
        }
        .alert b { color: #00ffaa; }
        .alert small { color: #8b949e; display:block; margin-top:6px; font-family: monospace; }

        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { text-align: left; color: #8b949e; font-weight: normal; padding: 8px; border-bottom: 1px solid #30363d; }
        td { padding: 10px 8px; border-bottom: 1px solid #21262d; }
        td a { color: #58a6ff; text-decoration: none; }
        td a:hover { text-decoration: underline; }
        .lock-icon { color: #00ffaa; margin-right: 6px; }

        .footer-note { text-align: center; color: #484f58; font-size: 11px; margin-top: 25px; }
    </style>
</head>
<body>
<div class="wrap">

    <div class="topbar">
        <h1>🛡 CryptoVault <span>// secure exchange</span></h1>
        <div><span class="pulse"></span><span style="font-size:12px;color:#8b949e;">SYSTEM ONLINE</span></div>
    </div>

    <div class="card">
        <div class="card-head">
            <h2>Security Layer</h2>
            <span class="tag">ACTIVE</span>
        </div>
        <div class="badges">
            <span class="badge">🔐 AES-256-CBC</span>
            <span class="badge">🔑 HMAC-SHA256 Signed URLs</span>
            <span class="badge">⏱ 15-min Expiry</span>
            <span class="badge">🧹 Auto-purge Plaintext</span>
        </div>
    </div>

    <div class="card">
        <div class="card-head">
            <h2>Upload &amp; Encrypt</h2>
        </div>
        <form action="/upload" method="POST" enctype="multipart/form-data">
            <div class="dropzone">📁 Choose a file — it will be AES-256 encrypted instantly on upload</div>
            <input type="file" name="file" required>
            <button type="submit">Encrypt &amp; Store</button>
        </form>

        {% if message %}
        <div class="alert">
            <b>✔ {{ message }}</b>
            {% if signed_url %}
            <small>SIGNED URL → {{ signed_url[:90] }}...</small>
            {% endif %}
        </div>
        {% endif %}
    </div>

    <div class="card">
        <div class="card-head">
            <h2>Encrypted Vault</h2>
            <form action="/list" method="GET"><button class="secondary" type="submit" style="width:auto;padding:6px 14px;font-size:12px;">↻ Refresh</button></form>
        </div>

        {% if files %}
        <table>
            <tr><th>File</th><th>Status</th><th>Action</th></tr>
            {% for f in files %}
            <tr>
                <td><span class="lock-icon">🔒</span>{{ f }}</td>
                <td style="color:#00ffaa;">Encrypted</td>
                <td><a href="/download/{{ f }}?decrypt=true">⬇ Decrypt &amp; Download</a></td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p style="color:#484f58; font-size:13px;">No files yet. Upload one above to populate the vault.</p>
        {% endif %}
    </div>

    <div class="footer-note">Internee.pk Cybersecurity Internship — Secure File Exchange Module</div>
</div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No filename"}), 400

    filename = secure_filename(file.filename)
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    encrypted_path = os.path.join(ENCRYPTED_FOLDER, filename + '.enc')

    file.save(upload_path)
    encryptor.encrypt_file(upload_path, encrypted_path)
    os.remove(upload_path)

    signed_url, expiry, sig = generate_signed_url(filename, expiry_minutes=15)
    message = f"'{filename}' encrypted with AES-256 and stored in vault."

    return render_template_string(HTML_TEMPLATE, message=message, signed_url=signed_url)

@app.route('/list', methods=['GET'])
def list_files():
    files = [f.replace('.enc', '')
             for f in os.listdir(ENCRYPTED_FOLDER)
             if f.endswith('.enc')]
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route('/download/<filename>')
def download_file(filename):
    encrypted_path = os.path.join(ENCRYPTED_FOLDER, filename + '.enc')
    decrypted_path = os.path.join(UPLOAD_FOLDER, 'decrypted_' + filename)

    if not os.path.exists(encrypted_path):
        return jsonify({"error": "File not found"}), 404

    encryptor.decrypt_file(encrypted_path, decrypted_path)
    return send_file(decrypted_path, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)
    print("[+] CryptoVault Secure File Exchange Starting...")
    print("[+] Encryption: AES-256-CBC")
    print("[+] URL: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

