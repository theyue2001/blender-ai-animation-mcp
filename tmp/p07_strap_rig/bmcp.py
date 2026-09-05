import socket, json, sys, time

HOST, PORT = "127.0.0.1", 9876

def send(payload, timeout=1800.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((HOST, PORT))
    s.sendall(json.dumps(payload).encode("utf-8"))
    buf = b""
    while True:
        try:
            chunk = s.recv(65536)
        except socket.timeout:
            raise RuntimeError("timeout waiting for Blender")
        if not chunk:
            break
        buf += chunk
        try:
            obj = json.loads(buf.decode("utf-8"))
            s.close()
            return obj
        except json.JSONDecodeError:
            continue
    s.close()
    return json.loads(buf.decode("utf-8"))

def run_code(code, timeout=1800.0):
    return send({"type": "execute_code", "params": {"code": code}}, timeout)

if __name__ == "__main__":
    path = sys.argv[1]
    to = float(sys.argv[2]) if len(sys.argv) > 2 else 1800.0
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    t0 = time.time()
    try:
        r = run_code(code, to)
    except Exception as e:
        print("ERR:", type(e).__name__, e)
        sys.exit(1)
    dt = time.time() - t0
    if r.get("status") == "success":
        res = r.get("result", {})
        out = res.get("result") if isinstance(res, dict) else res
        print(out if out is not None else json.dumps(res)[:4000])
    else:
        print("FAIL:", json.dumps(r)[:4000])
    print("--- %.1fs" % dt, file=sys.stderr)
