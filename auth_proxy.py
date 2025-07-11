from fastapi import HTTPException, Request, requests

class AuthProxy:
    def __init__(self, auth_url: str):
        self.auth_url = auth_url

    def auth(self, request: Request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # 获取token 并验证
        token = auth_header.split(" ")[1]
        if not token:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        response = requests.post(self.auth_url, params={"token": token})
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # 验证token是否有效
        if response.json().get("code") != 0:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        return True
    