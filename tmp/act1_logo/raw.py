import sys, json
sys.path.insert(0,".")
from bmcp import run_code
code = open("q1.py",encoding="utf-8").read()
r = run_code(code, 120)
print(json.dumps(r, ensure_ascii=False)[:6000])
