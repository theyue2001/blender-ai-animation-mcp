import socket, json, sys
s=socket.socket(); s.settimeout(20)
try:
    s.connect(("127.0.0.1",9876))
    s.sendall(json.dumps({"type":"execute_code","params":{"code":"import bpy\nprint(bpy.data.filepath)"}}).encode())
    buf=b""
    while True:
        c=s.recv(65536)
        if not c: break
        buf+=c
        try:
            json.loads(buf.decode()); break
        except Exception: continue
    print("ALIVE")
    sys.exit(0)
except Exception as e:
    print("BUSY", type(e).__name__)
    sys.exit(1)
