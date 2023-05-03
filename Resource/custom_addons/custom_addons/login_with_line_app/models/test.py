import requests
import json

# line_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
# token_line_params = {
#     "grant_type": "authorization_code",
#     "code": "AOljrKUpV5hAfj7khDQn",
#     "redirect_uri": "https://haohaochi.subuy.net/auth_oauth/signin",
#     "client_id": "1656530902",
#     "client_secret": "948f4566998ac5d71f8d3cf733162e80",
#     }
# response_token = requests.post("https://api.line.me/oauth2/v2.1/token", params=token_line_params)
# print(response_token.json())
# print(response_token.json().get("error"))
# # .get("access_token")

r = requests.post(
    "https://api.line.me/oauth2/v2.1/token",
    data={
        "grant_type": "authorization_code",
        "code": "mDFCTGgEQt0FGXnktMaL",
        "redirect_uri": "https://haohaochi.subuy.net/auth_oauth/signin",
        "client_id": "1656530902",
        "client_secret": "948f4566998ac5d71f8d3cf733162e80",
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
payload = json.loads(r.text)
print(payload)
print(payload.get('access_token'))

profile_line_params = {
                "id_token": payload.get('id_token'),
                "client_id": "1656530902",
            }
# params["access_token"] = payload.get('access_token')
validation = requests.post("https://api.line.me/oauth2/v2.1/verify", data=profile_line_params,headers={"Content-Type": "application/x-www-form-urlencoded"})
validation = json.loads(validation.text)
validation['user_id'] = validation['sub']
print(validation)
print(validation['sub'])
print(validation['user_id'])