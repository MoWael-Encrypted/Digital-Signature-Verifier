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

def load_public_key(key_path):
    """Load and validate a public key from a PEM file."""
    if key_path in _key_cache:
        return _key_cache[key_path]
        
    with open(key_path, 'rb') as f:
        pem_data = f.read()
    
    # Strict PEM format validation
    if b"-----BEGIN PUBLIC KEY-----" not in pem_data:
        raise ValueError("Invalid key type: Expected a public key but received a different key type. Please provide a valid public key for verification.")
    
    try:
        key = serialization.load_pem_public_key(pem_data, backend=default_backend())
    except Exception as e:
        raise ValueError(f"Failed to load public key: {str(e)}")
    
    if not isinstance(key, RSAPublicKey):
        raise ValueError("Invalid key type: The provided key is not a valid RSA public key")
    
    _key_cache[key_path] = key
    return key

def verify_signature(file_path, signature, public_key_path):
    """Verify a file's signature using a public key."""
    try:
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
    except ValueError as e:
        # Propagate key validation errors
        raise ValueError(f"Signature verification failed: {str(e)}") 