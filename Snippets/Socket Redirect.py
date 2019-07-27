import socket

def listen_redirect():
    data = None
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 8080))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            chunk = conn.recv(1024)
            if chunk:
                conn.send("\n".join([
                    'HTTP/1.1 200 OK',
                    'Content-Type: text/html',
                    '\n',
                    '<h1>Success!</h1>']).encode())
                data = chunk.decode()
        s.close()
    return data
