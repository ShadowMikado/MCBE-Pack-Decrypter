import io
import json
import zipfile

import customtkinter as ctk
from Crypto.Cipher import AES


class DecryptException(Exception):

    def __init__(self, *args):
        super().__init__(*args)


def aes_cfb_decrypt(data, key, iv):
    cipher = AES.new(key, AES.MODE_CFB, iv=iv)
    return cipher.decrypt(data)


def from_contents_json(data):
    return json.loads(data)


def decrypt_pack(decryption_key, zip_path, var: ctk.DoubleVar, lbl: ctk.CTkProgressBar):
    output_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_path, 'r') as zip_file, zipfile.ZipFile(output_buffer, 'w',
                                                                     zipfile.ZIP_DEFLATED) as output_zip:
        contents = None
        tt_file = len(zip_file.infolist()) - 1
        count = 0
        for file_info in zip_file.infolist():
            if file_info.filename == 'contents.json':
                with zip_file.open(file_info.filename) as f:
                    data = f.read()[0x100:]
                    data = aes_cfb_decrypt(data, decryption_key, decryption_key[:16])
                    contents = from_contents_json(data.decode('utf-8'))
                    break

        if contents is None:
            raise DecryptException("No contents table found.")

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
                    count += 1
                    var.set(count / tt_file)
                    lbl.update()

    return output_buffer.getvalue()
