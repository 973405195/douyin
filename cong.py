import requests


url = 'http://124.220.56.196/:7800/post_json'
data = {
  "video_id": 4994
}

res = requests.post(url,json=data).text
print(res)