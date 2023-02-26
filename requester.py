import requests


# Requests makes it simple to upload Multipart-encoded files 

url = 'http://127.0.0.1:5000/models'
auth = ("admin", "admin")
response =requests.get(url)


    # Successful POST request
if response.status_code == 200:
        response_data = response.json()
        print(response_data)
else:
    print(f"Error sending image: {response.text}")

