import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://lila.science/datasets/snapshot-serengeti', headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode()
        links = re.findall(r'href=[\'\"]?([^\'\" >]+)', html)
        found = False
        for href in links:
            if '.blob.core.windows.net' in href and href.endswith(('.jpg', '.JPG', '.zip')):
                print(f'Found LILA link: {href}')
                found = True
        if not found:
            print("No direct blob links found on the page.")
except Exception as e:
    print(f'Failed: {e}')
