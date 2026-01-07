import hashlib
import os
import logging
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey, RSAPrivateKey
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
_key_cache = {}

def hash_file(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def hash_data(data):
    if not isinstance(data, bytes):
        raise TypeError("Data must be bytes")
    return hashlib.sha256(data).hexdigest()

def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_pem.decode('utf-8'), public_pem.decode('utf-8')

def save_keys(private_key, public_key, private_path, public_path):
    with open(private_path, 'w') as f:
        f.write(private_key)
    os.chmod(private_path, 0o600)
    with open(public_path, 'w') as f:
        f.write(public_key)


def load_public_key(key_path):
    if key_path in _key_cache:
        key = _key_cache[key_path]
        if isinstance(key, RSAPublicKey):
            return key
        # If cached key is not public, reload it (or raise error, but reloading is safer if path content changed, though here it's likely wrong usage)
        # However, if the path IS a private key, we should fall through to the file check which will raise ValueError
        
    with open(key_path, 'rb') as f:
        pem_data = f.read()

    # Strictly check PEM type
    if b"-----BEGIN PUBLIC KEY-----" not in pem_data:
        raise ValueError(f"{key_path} does not contain a valid PUBLIC key")

    key = serialization.load_pem_public_key(pem_data, backend=default_backend())
    if not isinstance(key, RSAPublicKey):
        raise ValueError("Loaded key is not a valid RSA public key.")
    
    _key_cache[key_path] = key
    return key

def load_private_key(key_path):
    if key_path in _key_cache:
        key = _key_cache[key_path]
        if isinstance(key, RSAPrivateKey):
            return key
            
    with open(key_path, 'rb') as f:
        key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
        if not isinstance(key, RSAPrivateKey):
            raise ValueError("Loaded key is not a valid RSA private key.")
        _key_cache[key_path] = key
        return key

def sign_file(file_path, private_key_path):
    private_key = load_private_key(private_key_path)
    file_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            file_hash.update(chunk)
    return private_key.sign(
        file_hash.digest(),
        padding.PKCS1v15(),
        utils.Prehashed(hashes.SHA256())
    )


def verify_signature(file_path, signature, public_key_path):
    public_key = load_public_key(public_key_path)
    file_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            file_hash.update(chunk)
    try:
        public_key.verify(
            signature,
            file_hash.digest(),
            padding.PKCS1v15(),
            utils.Prehashed(hashes.SHA256())
        )
        return True
    except InvalidSignature:
        return False


def save_signature(signature, signature_path):
    with open(signature_path, 'wb') as f:
        f.write(signature)
    os.chmod(signature_path, 0o644)

def load_signature(signature_path):
    with open(signature_path, 'rb') as f:
        return f.read()
