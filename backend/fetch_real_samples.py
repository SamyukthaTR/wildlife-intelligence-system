import os
import urllib.request
import json
import ssl
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base_dir = "/app/scripts/sample_data"

def download_file(url, dest):
    print(f"Downloading {url} -> {dest}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            with open(dest, 'wb') as out:
                out.write(response.read())
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

# 1. Snapshot Serengeti (LILA BC)
print("Fetching Snapshot Serengeti...")
ss_dir = os.path.join(base_dir, "snapshot_serengeti")
os.makedirs(ss_dir, exist_ok=True)
download_file('https://lilawildlife.blob.core.windows.net/lila-wildlife/snapshotserengeti-unzipped/S1/B06/B06_R1/S1_B06_R1_PICT0016.JPG', os.path.join(ss_dir, 'S1_B06_R1_PICT0016.JPG'))
download_file('https://lilawildlife.blob.core.windows.net/lila-wildlife/snapshotserengeti-unzipped/S1/B06/B06_R1/S1_B06_R1_PICT0017.JPG', os.path.join(ss_dir, 'S1_B06_R1_PICT0017.JPG'))

# 2. BirdCLEF (Xeno-canto)
print("Fetching BirdCLEF (Xeno-canto)...")
bc_dir = os.path.join(base_dir, "birdclef")
os.makedirs(bc_dir, exist_ok=True)
try:
    req = urllib.request.Request('https://xeno-canto.org/api/2/recordings?query=cnt:brazil', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode())
        count = 0
        for rec in data['recordings']:
            if count >= 2: break
            audio_url = rec['file']
            if audio_url.startswith('//'):
                audio_url = 'https:' + audio_url
            download_file(audio_url, os.path.join(bc_dir, f"{rec['id']}.mp3"))
            count += 1
except Exception as e:
    print(f"Xeno-canto failed: {e}")

# 3. iNaturalist
print("Fetching iNaturalist...")
inat_dir = os.path.join(base_dir, "inaturalist")
os.makedirs(inat_dir, exist_ok=True)
try:
    req = urllib.request.Request('https://api.inaturalist.org/v1/observations?quality_grade=research&has[]=photos&per_page=1', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode())
        obs = data['results'][0]
        photo_url = obs['photos'][0]['url'].replace('square', 'medium')
        license_code = obs['photos'][0].get('license_code', 'unknown')
        print(f"iNaturalist License: {license_code}")
        
        # Save metadata for the adapter to use
        with open(os.path.join(inat_dir, 'metadata.json'), 'w') as f:
            json.dump([{"id": obs['id'], "license": license_code}], f)
            
        download_file(photo_url, os.path.join(inat_dir, f"{obs['id']}.jpg"))
except Exception as e:
    print(f"iNaturalist failed: {e}")

# 4. GBIF
print("Fetching GBIF...")
gbif_dir = os.path.join(base_dir, "gbif")
os.makedirs(gbif_dir, exist_ok=True)
try:
    req = urllib.request.Request('https://api.gbif.org/v1/occurrence/search?mediaType=StillImage&limit=1', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode())
        obs = data['results'][0]
        media_url = obs['media'][0]['identifier']
        
        with open(os.path.join(gbif_dir, 'metadata.json'), 'w') as f:
            json.dump([{"id": obs['key']}], f)
            
        download_file(media_url, os.path.join(gbif_dir, f"{obs['key']}.jpg"))
except Exception as e:
    print(f"GBIF failed: {e}")

print("All sample data fetched.")
