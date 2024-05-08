import requests

prompt = "Could you explain what is dask?"

response = requests.post("http://localhost:8000/", json=prompt)
print(response.text)