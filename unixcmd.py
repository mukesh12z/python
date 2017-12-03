import subprocess
from Crypto.Cipher import DES

def pad(text):
    while len(text) % 8 != 0:
        text += ' '
    return text

def subp(one,two):
    proc = subprocess.Popen([one, two],
                            stdin = subprocess.PIPE,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE
                        )

    (out, err) = proc.communicate()
    return out 

key = 'abcd1234'
name = 'test'

des = DES.new(key, DES.MODE_ECB)
out=subp("echo"," memory usage --")
out=out+subp("free","-m")
out=out+subp("echo","cpu usage --")
out=out+subp("mpstat","")
padded_text = pad(out)
encrypted_text = des.encrypt(padded_text)
print encrypted_text 
