import urllib.request
import ssl
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base_dir = '/app/scripts/sample_data/birdclef'
os.makedirs(base_dir, exist_ok=True)

def download(url, name):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        with open(os.path.join(base_dir, name), 'wb') as f:
            f.write(response.read())

try:
    download('https://xeno-canto.org/123456/download', 'XC123456.mp3')
    print('Audio 1 downloaded')
except Exception as e:
    print(f'Audio 1 failed: {e}')
try:
    download('https://xeno-canto.org/123457/download', 'XC123457.mp3')
    print('Audio 2 downloaded')
except Exception as e:
    print(f'Audio 2 failed: {e}')

