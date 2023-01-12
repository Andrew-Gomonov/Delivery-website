import requests
x = requests.post(
    "http://127.0.0.1:5000/api/users?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOj"
    "E2NzM2MzczNTMsImlhdCI6MTY3MzU1MDk1Mywic3ViIjotMTk2OX0.hB1eBrNKhg-fwsVvqzG4VtZ6jt7ks4uNOQW86aZWIxM",
    {
        "data": "1234"
    }
)
print(x.json())
