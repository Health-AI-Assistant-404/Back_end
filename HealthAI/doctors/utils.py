import re
import requests

def get_build_id():
    html = requests.get("https://doctoreto.com").text
    match = re.search(r'/_next/static/([^/]+)/_buildManifest.js', html)
    if match:
        return match.group(1)
    return None
