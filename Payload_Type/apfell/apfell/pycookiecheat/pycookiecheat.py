#!/usr/bin/env python3
# Taken from https://github.com/n8henrie/pycookiecheat
import sqlite3
import os.path
import base64
import sys
import json
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import traceback

salt = b'saltysalt'
iv = b' ' * 16
length = 16

def decrypt(encrypted_value, key) -> str:
    """This function decrypts the given value with the provided key"""
    # Encrypted cookies should be prefixed with 'v10' according to the
    # Chromium code. Strip it off.
    encrypted_value = encrypted_value[3:]

    # Strip padding by taking off number indicated by padding
    # eg if last is '\x0e' then ord('\x0e') == 14, so take off 14.
    # You'll need to change this function to use ord() for python2.
    def clean(x):
        return x[:-x[-1]].decode('utf8')

    cipher = AES.new(key, AES.MODE_CBC, IV=iv)
    decrypted = cipher.decrypt(encrypted_value)

    return clean(decrypted)


def crisp(args: dict) -> None:
    """This function accepts a path to a Cookies db file and key to decrypt chrome cookies"""
    cookies_db = args.get("cookies_file")
    login_db = args.get("login_file")
    key = args.get("key")
    out_file = args.get("output")

    raw_secret = key.encode('utf8')
    iterations = 1003
    # obtain the derived key
    dk = PBKDF2(raw_secret, salt, length, iterations)

    if cookies_db and os.path.exists(cookies_db):
        try:
            conn = sqlite3.connect(cookies_db)
        except Exception as e:
            print("Failed to connect to the sqlite3 db: " + str(e))
            sys.stdout.flush()
            return

        sql = 'select name, value, encrypted_value, path, host_key, expires_utc, is_httponly, samesite, is_secure, priority, last_access_utc, is_persistent, has_expires, source_scheme from cookies '

        cookies_list = []

        with conn:
            for k, v, ev, path, domain, expirationDate, httpOnly, samesite, secure, priority, last_access, is_persistent, has_expires, source_scheme in conn.execute(sql):
                temp_val = {"name": k, "value": v, "path": path, "domain": domain, "expirationDate": expirationDate, "httpOnly": httpOnly, "samesite": samesite, "secure": secure, "id": priority, "session": is_persistent, "hostOnly": False, "storeId":"firefox-default", "sameSite":"no_restriction","firstPartyDomain":""}
                temp_val["httpOnly"] = False if httpOnly == 0 else True
                temp_val["secure"] = False if httpOnly == 0 else True

                if temp_val["session"] == 1:
                    temp_val["session"] = False
                else:
                    temp_val["session"] = True
                    # if there is a not encrypted value or if the encrypted value
                # doesn't start with the 'v10' prefix, return v
                if v or (ev[:3] != b'v10'):
                    pass #cookies_list.append((k, v, path, domain, expirationDate, httpOnly, samesite, secure, priority))
                else:
                    temp_val['value'] = decrypt(ev, key=dk)

                cookies_list.append(temp_val)

        out = json.dumps(cookies_list, sort_keys=True, indent=4)

        sys.stdout.flush()

        outfile = open(out_file, 'w')
        outfile.write(out)
        outfile.close()
    elif login_db and os.path.exists(login_db):
        try:
            conn = sqlite3.connect(login_db)
        except Exception as e:
            print("Failed to connect to the sqlite3 db: " + str(e))
            sys.stdout.flush()
            return
        sql = 'select username_value, password_value, origin_url from logins'
        decryptedList = []
        with conn:
            for user, encryptedPass, url in conn.execute(sql):
                if user == "" or (
                        encryptedPass[:3] != b'v10'):  # user will be empty if they have selected "never" store password
                    continue
                else:
                    print("Working on url: {}".format(url))
                    urlUserPassDecrypted = (url, user, decrypt(encryptedPass, key=key))
                    decryptedList.append(urlUserPassDecrypted)
        out = json.dumps(decryptedList, sort_keys=True, indent=4)

        sys.stdout.flush()

        outfile = open(out_file, 'w')
        outfile.write(out)
        outfile.close()
    else:
        print("Cookies file doesn't exist")


if __name__ == "__main__":
    crisp(args=args)
