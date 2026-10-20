import base64, json
from urllib.request import Request, urlopen
TOKEN = open("/tmp/opencode/camp/token").read().strip()
REPO = "Fikra-API/fikra-benchmark"
def call(url, method="GET", body=None):
    r = Request(url if url.startswith("http") else "https://api.github.com"+url, method=method,
                data=json.dumps(body).encode() if body is not None else None,
                headers={"Authorization": "token "+TOKEN, "Accept": "application/vnd.github+json",
                         "Content-Type": "application/json","User-Agent":"dawn-pixellate"})
    try:
        resp = urlopen(r, timeout=40); txt = resp.read().decode()
        return resp.status, (json.loads(txt) if txt.strip().startswith(("{","[")) else txt)
    except Exception as e:
        try: return e.code, json.loads(e.read().decode())
        except Exception: return 0, str(e)
import os
files = []
for root, _, names in os.walk("."):
    if ".git" in root: continue
    for n in names:
        p = os.path.join(root, n)
        files.append((os.path.relpath(p, "."), open(p,"rb").read()))
for path, content in files:
    s, cur = call(f"/repos/{REPO}/contents/{path}?ref=main")
    body = {"message": "add %s" % path, "content": base64.b64encode(content).decode(), "branch": "main"}
    if s == 200: body["sha"] = cur["sha"]
    s, resp = call(f"/repos/{REPO}/contents/{path}", "PUT", body)
    print(path, s)
