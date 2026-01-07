# Digital Signature Verifier 🔐

**A web-based tool for demonstrating RSA digital signatures, document integrity validation, and forensic analysis.**

[![Status](https://img.shields.io/badge/Status-Active-success)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)]()
[![Framework](https://img.shields.io/badge/Flask-3.0.0-green)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

## 📖 Project Overview

The **Digital Signature Verifier** is an educational platform designed to teach the fundamentals of **Public Key Cryptography (RSA)**. It provides a secure, interactive environment where users can generate cryptographic key pairs, sign documents to ensure non-repudiation, and verify signatures to detect tampering.

---

## 📸 Interface Screenshots

| **Landing Page** | **Key Generation** |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/a3541cce-50b2-4234-95a9-a6279bf19abe" alt="Landing Page" width="100%"> | <img src="https://github.com/user-attachments/assets/7d96651a-3cc7-4885-a714-4eb65e329138" alt="Key Generation" width="100%"> |
| *Secure Dashboard* | *RSA Key Pair Creation* |

| **Document Signing** | **Signature Verification** |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/f2db671f-93aa-4f6f-b411-72575d32b7b8" alt="Signing Interface" width="100%"> | <img src="https://github.com/user-attachments/assets/572ec55d-6819-435f-8b5d-3c4134fa25d0" alt="Verification Result" width="100%"> |
| *SHA-256 Signing* | *Tamper Detection* |

---

## 🚀 Key Features

### 🔑 RSA Key Management
* **Generation:** Create robust 2048-bit RSA key pairs (Public/Private).
* **Download:** Export keys in standard PEM format (PKCS#8).
* **Security:** Session-based ephemeral storage ensures keys are never permanently stored on the server.

### ✍️ Document Signing
* **Algorithm:** SHA-256 hashing with PKCS#1 v1.5 padding.
* **File Support:** Signs PDF, DOCX, TXT, and Images.
* **Output:** Generates detachable `.sig` signature files.

### ✅ Signature Verification
* **Integrity Check:** Verifies that the document hash matches the signed digest.
* **Authentication:** Confirms the document was signed by the owner of the corresponding Private Key.
* **Tamper Detection:** Instantly flags modified files or invalid signatures.

### 🕵️ Forensic Challenges
* Includes built-in scenarios (e.g., "Suspect.txt") to practice digital forensic analysis and evidence validation.

---

## 🛠️ Technical Architecture

The application follows a modular architecture separating cryptographic logic from the web interface.

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python Flask | API routes and session management |
| **Crypto Engine** | `cryptography` lib | RSA operations, SHA-256 hashing |
| **Validation** | `python-magic` | MIME type detection via magic numbers |
| **Frontend** | Bootstrap 5 + JS | Responsive, cybersecurity-themed UI |

### Workflows

**1. Signing Process:**
`User Upload` → `SHA-256 Hash` → `RSA Sign (Private Key)` → `Download .sig`

**2. Verification Process:**
`User Upload (Doc + Sig + Public Key)` → `Decrypt Sig (Public Key)` == `Hash(Doc)`? → `Valid/Invalid`

---

## 👥 Authors & Acknowledgments

* **Author:** Mostafa ELSaeed
* **Supervisor:** Dr. Tamer Mostafa
* **Institution:** Faculty of Engineering - Cyber Forensics Lab

---

## 💻 Installation & Usage

### Prerequisites
* Python 3.8 or higher
* `pip` package manager

### Steps

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/digital-signature-verifier.git](https://github.com/your-username/digital-signature-verifier.git)
    cd digital-signature-verifier
    ```

2.  **Install Dependencies**
    *(Note: On Windows, this installs `python-magic-bin` automatically)*
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    python app.py
    ```

4.  **Access the Interface**
    Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 🧪 Testing

The project includes unit tests for the cryptographic engine.

```bash
# Run hash function tests
python test_hashing.py

# Run signature verification tests
python test_signature.py
