import os, requests

def register(request):
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return None, ("email and password are required", 400)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/register",
        json={
            "email": email,
            "password": password
        },
        timeout=5
    )
    if response.status_code == 201:
        return response.text, None
    else:
        return None, (response.text, response.status_code)

def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)
    basicAuth = (auth.username, auth.password)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
        auth=basicAuth,
        timeout=5
    )
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
