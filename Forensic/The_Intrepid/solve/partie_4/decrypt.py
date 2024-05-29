from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from pwn import xor
from itertools import product
from Crypto.Cipher import AES
from pathlib import Path
from sys import argv

### TAKEN FROM APPLICATION SOURCE CODE ###
FILENAME_LEN = 20
AES_KEY_SIZE = 32
AES_IV_SIZE = 16
HMAC_SIGNATURE_SIZE = 12

AES_KEY_SIZE_HEX = AES_KEY_SIZE * 2
AES_IV_SIZE_HEX = AES_IV_SIZE * 2
HMAC_SIGNATURE_SIZE_HEX = HMAC_SIGNATURE_SIZE * 2


def hmac_text(key: bytes, text: bytes):
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(text)
    return h.finalize()[:12].hex()


def decrypt_text(key: bytes, iv: bytes, ciphertext: bytes):
    cipher = AES.new(key, AES.MODE_CTR, initial_value=iv, nonce=b"")
    cleartext = cipher.decrypt(ciphertext)
    return cleartext


###

XOR_KEYS = ["sCYHnZC97X", "4W2TwpmFMz", "ZAijP8972D", "c63duF2UpW"]


def generate_aes_decrypt_structs(filename: str, scrambled_prng_data: bytes):
    # We try to recover the raw prandom_u32_state output
    raw_prng_data_candidates = []
    for key in XOR_KEYS:
        raw_prng_data_candidates.append(xor(scrambled_prng_data, key.encode()))

    # Now, we assume we have four potential raw prandom_u32_state outputs
    # What we do, is that we xor each of them with every xor key
    # This gives us in total 4 raw_prng_data_candidates * 4 XOR_KEYS = 16 possibilities
    # One of the 16 possibilities was the PRNG data outputted when the files were encrypted
    candidates = []
    for raw_prng_data_candidate in raw_prng_data_candidates:
        for key in XOR_KEYS:
            candidates.append(xor(raw_prng_data_candidate, key.encode()))

    # Now, we depend on the key and the iv, and each one of them can be a different one from the
    # 16 possibilities
    # EX :
    # key = prandom_u32_state(1689862823) ^ "sCYHnZC97X"
    # iv = prandom_u32_state(1689862823) ^ "4W2TwpmFMz"
    # So here, we try every combination
    aes_decrypt_structs = []
    for candidates_set in product(candidates, repeat=2):
        aes_decrypt_struct = {}
        key = aes_decrypt_struct["key"] = candidates_set[0][:AES_KEY_SIZE]
        iv = aes_decrypt_struct["iv"] = candidates_set[1][:AES_IV_SIZE]
        # Reconstruct link (optional)
        link_digest = hmac_text(key, f"{filename}{iv.hex()}".encode())
        aes_decrypt_struct["link"] = f"{filename}#{key.hex()}{iv.hex()}{link_digest}"
        #
        aes_decrypt_structs.append(aes_decrypt_struct)

    return aes_decrypt_structs


def main(encrypted_file_path: str, scrambled_prng_data: str):
    scrambled_prng_data = bytes.fromhex(scrambled_prng_data)
    file_to_decrypt = Path(encrypted_file_path)
    if not file_to_decrypt.is_file():
        print(f"{encrypted_file_path} does not exist")
        exit(1)

    with open(file_to_decrypt, "rb") as f:
        encrypted = f.read()

    aes_decrypt_structs = generate_aes_decrypt_structs(
        file_to_decrypt.name, scrambled_prng_data
    )

    # Try to decrypt with each pair of (key, iv)
    for aes_decrypt_struct in aes_decrypt_structs:
        cleartext = decrypt_text(
            aes_decrypt_struct["key"], aes_decrypt_struct["iv"], encrypted
        )
        # ZIP magic bytes
        if cleartext.startswith(b"\x50\x4B\x03\x04"):
            with open(f"{file_to_decrypt.name}_decrypted.zip", "wb+") as f:
                f.write(cleartext)
            print(aes_decrypt_struct)
            break


if __name__ == "__main__":
    if len(argv) < 3:
        print(
            "Usage: decrypt.py <file_path> <prng_data>\nEx: decrypt.py test.enc 6764a8d8dd36475d1f4cd7a7d95718cb24b73be756aa9d31db97d8288e84761e"
        )
        exit(1)

    main(argv[1], argv[2])
