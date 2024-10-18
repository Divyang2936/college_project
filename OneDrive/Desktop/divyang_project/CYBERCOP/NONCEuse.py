from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_aes_gcm(plaintext, key):
    # Generate a small nonce 
    nonce = b'\x00' * 4  # 4 bytes nonce (32 bits)

    # Create AES cipher object with GCM mode
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    # Encrypt data and obtain ciphertext + tag
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    print(nonce)
    print(ciphertext)
    print(tag)
    print(nonce, ciphertext, tag)
    return (nonce, ciphertext, tag)
    
def decrypt_aes_gcm(nonce, ciphertext, tag, key):
    # Create AES cipher object with GCM mode
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    print(cipher)
    # Decrypt and verify integrity
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
   
    return plaintext

# Example usage
key = get_random_bytes(16)  # 128-bit key
plaintext = b"13"  # Sample plaintext

# Encrypt plaintext
nonce, ciphertext, tag = encrypt_aes_gcm(plaintext, key)

# Decrypt ciphertext
decrypted_plaintext = decrypt_aes_gcm(nonce, ciphertext, tag, key)

print("Original plaintext:", plaintext)
print("Decrypted plaintext:", decrypted_plaintext)
