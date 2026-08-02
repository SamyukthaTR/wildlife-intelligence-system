import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://lilawildlife.blob.core.windows.net/lila-wildlife/snapshotserengeti-unzipped/S1/B06/B06_R1/S1_B06_R1_PICT0016.JPG'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, context=ctx) as response:
        print(f'OK: {response.status}')
except Exception as e:
    print(f'Failed: {e}')
