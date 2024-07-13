import io
import json
import os.path
import zipfile

from Crypto.Cipher import AES


def aes_cfb_decrypt(data, key, iv):
    cipher = AES.new(key, AES.MODE_CFB, iv=iv)
    return cipher.decrypt(data)


def from_contents_json(data):
    return json.loads(data)


def decrypt_pack(decryption_key, zip_path):
    output_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_path, 'r') as zip_file, zipfile.ZipFile(output_buffer, 'w',
                                                                     zipfile.ZIP_DEFLATED) as output_zip:
        contents = None

        for file_info in zip_file.infolist():
            if file_info.filename == 'contents.json':
                with zip_file.open(file_info.filename) as f:
                    data = f.read()[0x100:]
                    data = aes_cfb_decrypt(data, decryption_key, decryption_key[:16])
                    contents = from_contents_json(data.decode('utf-8'))
                    break

        if contents is None:
            raise ValueError("No contents table found.")

        for file_info in zip_file.infolist():
            if file_info.filename != 'contents.json':
                with zip_file.open(file_info.filename) as f:
                    file_data = f.read()

                    for info_2 in contents.get("content", []):
                        if info_2["path"] == file_info.filename:
                            key = info_2.get("key", "").encode()
                            if key == b"":
                                output_zip.writestr(file_info.filename, file_data)
                                break
                            decrypted_data = aes_cfb_decrypt(file_data, key, key[:16])
                            output_zip.writestr(file_info.filename, decrypted_data)
                            break
                    else:
                        output_zip.writestr(file_info.filename, file_data)

    return output_buffer.getvalue()


key = input("Pack key : ").encode()

if len(key) != 32:
    print("Error ! Key must be 32 bytes long.")
    exit()

zip_path = input("Pack path : ")
if not os.path.isfile(zip_path):
    print("Error ! Pack doesn't exists here")
    exit()
output_path = input("Decrypted pack path : ")
if not os.path.isdir(output_path):
    print("Output directory doesn't exists, creating ...")
    os.makedirs(output_path, exist_ok=True)

name = os.path.splitext(os.path.basename(zip_path))[0]
decrypted_data = decrypt_pack(key, zip_path)
with open(os.path.join(output_path, name + "_decrypted.zip"), 'wb+') as f:
    f.write(decrypted_data)
print("Successfully Decrypted !")
