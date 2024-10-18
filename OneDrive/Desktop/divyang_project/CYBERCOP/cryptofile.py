from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_file(input_file, output_file, key):
    chunk_size = 64 * 1024  # 64 KB

    # Generate initialization vector
    iv = get_random_bytes(16)

    # Create AES cipher object
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Open input and output files
    with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
        outfile.write(iv)  # Write the initialization vector to the output file

        # Encrypt data in chunks
        while True:
            chunk = infile.read(chunk_size)
            if len(chunk) == 0:
                break
            elif len(chunk) % 16 != 0:
                # Padding the last chunk if needed
                chunk += b' ' * (16 - len(chunk) % 16)

            # Encrypt and write to output file
            outfile.write(cipher.encrypt(chunk))

def decrypt_file(input_file, output_file, key):
    chunk_size = 64 * 1024  # 64 KB

    # Open input and output files
    with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
        # Read initialization vector from the input file
        iv = infile.read(16)

        # Create AES cipher object
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Decrypt data in chunks
        while True:
            chunk = infile.read(chunk_size)
            if len(chunk) == 0:
                break

            # Decrypt and write to output file
            outfile.write(cipher.decrypt(chunk))

# Path to the input file
input_file_path = '/home/yeshtra/Downloads/cheatsheet.pdf'

# Path to the encrypted output file
encrypted_file_path = '/home/yeshtra/Downloads/encrypted_file.bin'

# Path to the decrypted output file
decrypted_file_path = '/home/yeshtra/Downloads/decrypted_file.pdf'

# Generate a random key for encryption
key = get_random_bytes(16)  # 16 bytes for AES-128

# Encrypt file
encrypt_file(input_file_path, encrypted_file_path, key)

# Decrypt file
decrypt_file(encrypted_file_path, decrypted_file_path, key)
