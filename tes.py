import requests

url = "https://api.ipify.org?format=json"
print(requests.get(url).text)