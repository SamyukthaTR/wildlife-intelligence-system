import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def test_url(url, name):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response:
            print(f"{name}: OK - {response.status}")
            return True
    except Exception as e:
        print(f"{name}: Failed - {e}")
        return False

test_url('https://lilablobssc.blob.core.windows.net/snapshotserengeti-unzipped/S1/B06/B06_R1/S1_B06_R1_PICT0016.JPG', 'Serengeti')

try:
    req = urllib.request.Request('https://api.inaturalist.org/v1/observations?quality_grade=research&has[]=photos&per_page=1', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode())
        photo_url = data['results'][0]['photos'][0]['url'].replace('square', 'medium')
        test_url(photo_url, 'iNaturalist Image')
except Exception as e:
    print(f'iNaturalist API failed: {e}')

try:
    req = urllib.request.Request('https://api.gbif.org/v1/occurrence/search?mediaType=StillImage&limit=1', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode())
        media_url = data['results'][0]['media'][0]['identifier']
        test_url(media_url, 'GBIF Image')
except Exception as e:
    print(f'GBIF API failed: {e}')

try:
    req = urllib.request.Request('https://xeno-canto.org/api/2/recordings?query=q:A', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode())
        audio_url = data['recordings'][0]['file']
        if audio_url.startswith('//'):
            audio_url = 'https:' + audio_url
        test_url(audio_url, 'Xeno-canto Audio')
except Exception as e:
    print(f'Xeno-canto API failed: {e}')
