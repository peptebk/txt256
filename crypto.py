import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives.ciphers.modes import CFB
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64


def encrypt(plaintext, password):
    salt = os.urandom(16)

    # ключ
    key = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000, dklen=32
    )
    iv = os.urandom(16)

    # Создаём шифр
    cipher = Cipher(algorithms.AES(key), CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Добавляем паддинг к данным
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()

    # Шифруем
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Возвращаем salt + iv + ciphertext
    result = salt + iv + ciphertext
    return base64.b64encode(result)


def decrypt(encrypted_data, password):
    encrypted_data = base64.b64decode(encrypted_data)

    # Извлечение
    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]

    # Восстанавление ключа
    key = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000, dklen=32
    )

    # Создаём дешифратор
    cipher = Cipher(algorithms.AES(key), CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Убираем паддинг
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    return plaintext.decode('utf-8')
