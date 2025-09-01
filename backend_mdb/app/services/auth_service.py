from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.database import user_collection
from app.core.security import create_access_token


async def google_login(google_token: str, client_id: str):
    try:
        # Xác thực token Google
        id_info = id_token.verify_oauth2_token(
            google_token, google_requests.Request(), client_id
        )

        # Lấy thông tin user
        user_data = {
            "sub": id_info["sub"],
            "email": id_info.get("email"),
            "name": id_info.get("name"),
            "picture": id_info.get("picture"),
        }

        # Tìm user trong MongoDB (await)
        user = await user_collection.find_one({"email": user_data["email"]})

        if not user:
            # Nếu chưa có -> tạo mới (await insert)
            new_user = {
                "name": user_data.get("name") or "",
                "avatar": user_data.get("picture") or None,
                "email": user_data.get("email"),
                "password": None,
                "provider_name": "google",
                "provider_id": user_data["sub"],
                "is_outside": True,
                "status": "active",
                "role": "user",
            }
            result = await user_collection.insert_one(new_user)
            user = await user_collection.find_one({"_id": result.inserted_id})

        # Tạo JWT
        access_token = create_access_token(
            data={"sub": str(user["_id"]), "email": user["email"], "role": user["role"]}
        )

        return {
            "access_token": access_token,
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "avatar": user.get("avatar"),
            },
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Google không hợp lệ",
        )
