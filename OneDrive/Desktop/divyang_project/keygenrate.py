import os

# Generate a random encryption key
encryption_key = os.urandom(32)

# Convert the bytes to a hexadecimal string for easy use in settings.py
encryption_key_hex = encryption_key.hex()

print(encryption_key_hex)
