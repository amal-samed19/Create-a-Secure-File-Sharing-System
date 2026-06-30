# Create-a-Secure-File-Sharing-System
1. Project Overview
A lightweight, secure file-sharing web application built with Python Flask, AES-256-CBC
Encryption, and HMAC-SHA256 Signed URLs. This system provides a robust architecture for
uploading files securely, encrypting them at rest, and generating time-bound, tamper-proof
download links. It is designed and tested within a Kali Linux environment as a cybersecurity
engineering project.

2. Core Features
 AES-256-CBC Encryption: All uploaded files are encrypted at rest using a strong
cryptographic cipher with a unique Initialization Vector (IV) per file.
 HMAC-SHA256 URL Signing: Download links are cryptographically signed to prevent
URL tampering. If a malicious actor alters the file ID or expiration timestamp, the
signature becomes invalid.
 Expiration Timestamps: Shared download links automatically expire after a
configurable duration (e.g., 30 minutes).
 Secure Virtual Environment: Fully isolated and containerized dependencies managed
cleanly via Python venv.

3. System Architecture &amp; Workflow
Upload Phase:
• The user uploads a file through the Flask web interface.
• The backend generates a random 16-byte Initialization Vector (IV).
• The file data is padded (PKCS7) and encrypted using AES-256-CBC.
• The encrypted payload and IV are saved securely on the server storage disk.
Sharing Phase:
• The system generates a unique download token containing the file_id and an expires UNIX
timestamp.
• An HMAC-SHA256 signature is generated over the token using a protected server-side
SECRET_KEY.
• The user receives a signed URL:
/download/&lt;file_id&gt;?expires=&lt;timestamp&gt;&amp;signature=&lt;hmac&gt;
Download Phase:

• The server intercepts the download request and validates the current time against the
expires timestamp.
• The server recalculates the HMAC signature and matches it with the one provided in the
URL.
• If valid, the server reads the encrypted file, decrypts it using the stored IV and AES key,
strips the padding, and streams the original file back to the user.

4. Project Directory Structure
secure-file-sharing/
│
├── app.py # Main Flask application &amp; routing
├── crypto_utils.py # Cryptographic functions (AES &amp; HMAC logic)
├── config.py # Application settings and environment keys
├── requirements.txt # Project dependencies
├── test_system.py # Automated validation script (integrity &amp; tampering test)
│
├── storage/ # Isolated directory for encrypted files
│ └── .gitkeep
└── templates/ # UI Templates
├── index.html # Portal Dashboard (Upload panel &amp; link generator)
└── download.html # Secure Download validation page

4. Expiration Enforcement: Simulates an expired timestamp to ensure the system blocks
access immediately.
