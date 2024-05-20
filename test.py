import requests

#base server of the API (localhost:port)
BASE = "http://127.0.0.1:5000/"

data = [ {"likes": 78, "name": "Aidan", "views":1000},
        {"likes": 100, "name": "Bobby", "views":9999},
        {"likes": 100, "name": "Tim", "views":100000}
]
'''
for i in range(len(data)):
    response = requests.put(BASE + "video/" + str(i), data[i])
    print(response.json())

input()
'''

response = requests.patch(BASE + "video/1", {"likes": 55, "name": "Joshua", "views": 123456})
print(response.json())

