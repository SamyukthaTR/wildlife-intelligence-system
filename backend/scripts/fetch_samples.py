import urllib.request
import os

images = [
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Zebra_in_Serengeti.jpg/640px-Zebra_in_Serengeti.jpg", "zebra.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Lion_waiting_in_Namibia.jpg/640px-Lion_waiting_in_Namibia.jpg", "lion.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Loxodonta_africana_-_old_bull_%28Ngorongoro%2C_2009%29.jpg/640px-Loxodonta_africana_-_old_bull_%28Ngorongoro%2C_2009%29.jpg", "elephant.jpg")
]

os.makedirs("/app/scripts/sample_data", exist_ok=True)

for url, filename in images:
    path = f"/app/scripts/sample_data/snapshot_serengeti_{filename}"
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, path)

print("Done downloading sample images.")
