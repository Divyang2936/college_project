# utils.py (for key generation and decryption)
# utils.py (for key generation and decryption)
import os
import base64
from cryptography.fernet import Fernet

def generate_aes_key():
    from cryptography.fernet import Fernet

    """
    Generate a key for encryption
    """
    key = Fernet.generate_key()
    return key

# # Generating a key
# encryption_key = generate_key()
# print("Encryption Key:", encryption_key)


def encrypt_file(file_data, key):
    print(key,'ENCCCCCCCCCCCCCCCCCCCCC')
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(file_data)
    return encrypted_data

def decrypt_file(encrypted_data, key):
    print(key,'DDDDDNCCCCCCCCCCCCCCCCCCCCC')
    # key = base64.urlsafe_b64decode(key)
    fernet = Fernet(key.encode())
    decrypted_data = fernet.decrypt(encrypted_data)
    return decrypted_data
