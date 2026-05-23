import urllib.request
import urllib.parse
import json
import base64
import sys

AUTH_URL = "http://localhost:8081/api/v1/auth"
NOTIF_URL = "http://localhost:8081/api/v1/jobs"

def print_header(title: str):
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60)

def decode_token_payload(token: str):
    try:
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        decoded = base64.urlsafe_b64decode(payload_b64).decode("utf-8")
        return json.loads(decoded)
    except Exception as e:
        return f"Error: {e}"

def make_request(url: str, method: str = "GET", data: dict = None, headers: dict = None, params: dict = None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    
    req_data = None
    if data:
        if headers and headers.get("Content-Type") == "application/json":
            req_data = json.dumps(data).encode("utf-8")
        else:
            req_data = urllib.parse.urlencode(data).encode("utf-8")
            
    req = urllib.request.Request(url, method=method, data=req_data)
    
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
            
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body)
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"detail": e.reason}
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Please ensure the microservices are running locally via docker compose.")
        sys.exit(1)

def main():
    print_header("Step 1: Authenticate Superadmin (Admin Role)")
    status, res = make_request(
        f"{AUTH_URL}/login",
        method="POST",
        data={"username": "superadmin", "password": "admin123"}
    )

    if status != 200:
        print(f"Failed to login superadmin: {status} - {res}")
        sys.exit(1)

    admin_token = res["access_token"]
    print("Superadmin successfully authenticated!")
    
    admin_payload = decode_token_payload(admin_token)
    print("\nDecoded JWT Payload for Superadmin:")
    for k, v in admin_payload.items():
        print(f"  {k}: {v}")

    print_header("Step 2: Trigger Background Email as Admin")
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    status, res = make_request(
        f"{NOTIF_URL}/trigger-email",
        method="POST",
        headers=headers,
        params={"email": "test@saas.com", "template_type": "welcome"}
    )
    print(f"HTTP Status: {status}")
    print(f"Response Body: {res}")

    print_header("Step 3: Register Standard User (User Role)")
    status, res = make_request(
        f"{AUTH_URL}/register",
        method="POST",
        headers={"Content-Type": "application/json"},
        data={
            "username": "johndoe",
            "email": "john@saas.com",
            "password": "userpass123",
            "role": "user"
        }
    )
    if status == 400 and "Username already registered" in str(res):
        print("User 'johndoe' already registered. Proceeding...")
    elif status != 200:
        print(f"Failed to register: {status} - {res}")
        sys.exit(1)
    else:
        print("Successfully registered user 'johndoe' with 'user' role!")

    print_header("Step 4: Authenticate Standard User")
    status, res = make_request(
        f"{AUTH_URL}/login",
        method="POST",
        data={"username": "johndoe", "password": "userpass123"}
    )
    if status != 200:
        print(f"Failed to login johndoe: {status} - {res}")
        sys.exit(1)

    user_token = res["access_token"]
    user_payload = decode_token_payload(user_token)
    print("\nDecoded JWT Payload for Johndoe:")
    for k, v in user_payload.items():
        print(f"  {k}: {v}")

    print_header("Step 5: Attempt Background Email as Standard User (Should Fail)")
    user_headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    status, res = make_request(
        f"{NOTIF_URL}/trigger-email",
        method="POST",
        headers=user_headers,
        params={"email": "test@saas.com", "template_type": "welcome"}
    )
    print(f"HTTP Status: {status}")
    print(f"Response Body: {res}")
    if status == 403:
        print("\nSUCCESS: Access was Denied with 403 Forbidden because 'johndoe' lacks 'jobs.trigger' permission!")
    else:
        print("\nFAILURE: Standard user was not blocked!")

if __name__ == "__main__":
    main()
