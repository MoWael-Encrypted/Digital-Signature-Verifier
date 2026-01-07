import unittest
import tempfile
import os
from crypto_utils import hash_file, hash_data, generate_key_pair, save_keys

class TestHashing(unittest.TestCase):
    def test_hash_data_empty(self):
        self.assertEqual(
            hash_data(b""),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

    def test_hash_data_hello_world(self):
        self.assertEqual(
            hash_data(b"Hello, World!"),
            "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
        )

    def test_hash_file_empty(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            pass
        self.assertEqual(hash_file(f.name),
                         "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        os.unlink(f.name)

    def test_hash_file_content(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Hello, World!")
        self.assertEqual(hash_file(f.name),
                         "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f")
        os.unlink(f.name)

    def test_key_generation_and_saving(self):
        private_key, public_key = generate_key_pair()
        self.assertTrue(private_key.startswith("-----BEGIN PRIVATE KEY-----"))
        self.assertTrue(public_key.startswith("-----BEGIN PUBLIC KEY-----"))
        with tempfile.TemporaryDirectory() as tmp:
            priv = os.path.join(tmp, "priv.pem")
            pub = os.path.join(tmp, "pub.pem")
            save_keys(private_key, public_key, priv, pub)
            self.assertTrue(os.path.exists(priv))
            self.assertTrue(os.path.exists(pub))

if __name__ == '__main__':
    unittest.main()
