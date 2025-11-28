import hashlib

target = "06afa6c8b54d3cc80d269379d8b6a078"
base = "Teste123"

variations = [
    base,
    base + "\n",
    base + "\r\n",
    base + " ",
    " " + base,
    "<Dados>" + base + "</Dados>",
    "Teste123\x00",
]

encodings = ["utf-8", "iso-8859-1", "ascii", "utf-16", "utf-16le", "utf-16be"]

print(f"Target: {target}")

for v in variations:
    for enc in encodings:
        try:
            h = hashlib.md5(v.encode(enc)).hexdigest()
            if h == target:
                print(f"MATCH FOUND! String: '{repr(v)}', Encoding: {enc}")
                exit(0)
            # print(f"Tested: {repr(v)} ({enc}) -> {h}")
        except:
            pass

print("No match found.")
