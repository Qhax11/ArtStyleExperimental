"""Decode an MCP capture result (JSON with base64 image) into a PNG. Usage: decode_capture.py <in.txt> <out.png>"""
import base64, json, re, sys
raw = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r'"data"\s*:\s*"([A-Za-z0-9+/=]+)"', raw)
open(sys.argv[2], "wb").write(base64.b64decode(m.group(1)))
