import requests, os

url = "https://sourceforge.net/projects/gfpgan.mirror/files/v1.3.4/GFPGANv1.4.pth/download"
out = "gfpgan/weights/GFPGANv1.4.pth"

os.makedirs(os.path.dirname(out), exist_ok=True)
print("Downloading GFPGAN v1.4 model...")

resp = requests.get(url, allow_redirects=True, stream=True)
if resp.status_code == 200:
    with open(out, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"✅ Download complete: {out}")
else:
    print(f"❌ Failed: HTTP {resp.status_code}")
