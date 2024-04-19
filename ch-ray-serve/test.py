import requests

ray_logo_bytes = requests.get(
    "https://tuna.moe/assets/img/service/mirrors.png"
).content

resp = requests.post("http://localhost:8901/", data=ray_logo_bytes)
print(resp.json())