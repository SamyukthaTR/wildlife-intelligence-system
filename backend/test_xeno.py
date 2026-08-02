import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://xeno-canto.org/api/2/recordings?query=cnt:brazil', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx) as response:
    data = json.loads(response.read().decode())
    audio_url = data['recordings'][0]['file']
    print(f'Found audio: {audio_url}')
