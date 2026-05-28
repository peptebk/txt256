#txt256 — Encrypted notes

** TXT256** is an application for creating and storing notes with AES-256 protection. All notes are stored in a local database in encrypted form. Decryption is possible only with the help of a password, which is stored in encrypted form in the database.

## Main features

- Create and edit notes
- Content encryption using AES-256
- Export/import of an encrypted file

## How it works

1. The user enters the password at startup.
2. A key (PBKDF2) is generated based on this password.
3. The note file is encrypted/decrypted on the device.
