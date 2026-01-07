import unittest
import tempfile
import os
from crypto_utils import generate_key_pair, save_keys, sign_file, verify_signature, save_signature, load_signature

class TestSignatureVerification(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.doc_path = os.path.join(self.temp_dir.name, "doc.txt")
        with open(self.doc_path, 'w') as f:
            f.write("Test file for signing.")

        self.priv_key, self.pub_key = generate_key_pair()
        self.priv_path = os.path.join(self.temp_dir.name, "private.pem")
        self.pub_path = os.path.join(self.temp_dir.name, "public.pem")
        save_keys(self.priv_key, self.pub_key, self.priv_path, self.pub_path)

    def test_private_key_rejected_as_public_key(self):
        sig = sign_file(self.doc_path, self.priv_path)
    # Should raise ValueError when using private key for public key operation
        with self.assertRaises(ValueError):
            verify_signature(self.doc_path, sig, self.priv_path)



    
    def tearDown(self):
        self.temp_dir.cleanup()

    def test_valid_signature(self):
        sig = sign_file(self.doc_path, self.priv_path)
        self.assertTrue(verify_signature(self.doc_path, sig, self.pub_path))

    def test_invalid_signature_modified_doc(self):
        sig = sign_file(self.doc_path, self.priv_path)
        with open(self.doc_path, 'w') as f:
            f.write("Modified content")
        self.assertFalse(verify_signature(self.doc_path, sig, self.pub_path))

    def test_invalid_signature_wrong_key(self):
        sig = sign_file(self.doc_path, self.priv_path)
        new_priv, new_pub = generate_key_pair()
        new_pub_path = os.path.join(self.temp_dir.name, "wrong_pub.pem")
        with open(new_pub_path, 'w') as f:
            f.write(new_pub)
        self.assertFalse(verify_signature(self.doc_path, sig, new_pub_path))

    def test_signature_file_save_and_load(self):
        sig = sign_file(self.doc_path, self.priv_path)
        sig_path = os.path.join(self.temp_dir.name, "sig.sig")
        save_signature(sig, sig_path)
        loaded = load_signature(sig_path)
        self.assertEqual(sig, loaded)

if __name__ == '__main__':
    unittest.main()
