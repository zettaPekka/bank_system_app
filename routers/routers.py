from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse

from auth.jwt_processing import create_jwt, check_jwt
from database.cruds import add_user, check_user, get_user_by_id, get_user_id_by_login
from schemas import UserSchema


router = APIRouter()

@router.get('/profile/', tags=['profile'], summary='Профиль пользователя')
async def profile(request: Request):
    current_jwt = request.cookies.get('access_token')
    if not current_jwt:
        raise HTTPException(status_code=401, detail="Unauthorized")

    uid = check_jwt(current_jwt)
    if not uid:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = await get_user_by_id(uid)

    return {
        'login': user.login,
        'balance': user.balance,
        'history': user.history
    }


@router.post('/login/', tags=['auth'])
async def login(user: UserSchema, request: Request):
    current_jwt = request.cookies.get('access_token')
    if current_jwt and check_jwt(current_jwt):
        raise HTTPException(status_code=400, detail="Already logged in")

    user_info = await check_user(user.login, user.password)
    if user_info: 
        response_data = {"status": "ok"}
        response = JSONResponse(content=response_data)
        response.set_cookie(key='access_token', value=create_jwt(user_info.id), max_age=64000)
        return response

    raise HTTPException(status_code=400, detail="Invalid login or password")

@router.post('/registration/', tags=['auth'])
async def registration(user: UserSchema, request: Request):
    current_jwt = request.cookies.get('access_token')
    if current_jwt and check_jwt(current_jwt):
        raise HTTPException(status_code=400, detail="Already logged in")

    res = await add_user(user.login, user.password)
    if not res:
        raise HTTPException(status_code=400, detail="User already exists")

    user_id = await get_user_id_by_login(user.login)
    response_data = {"status": "ok"}
    response = JSONResponse(content=response_data)
    response.set_cookie(key='access_token', value=create_jwt(user_id), max_age=64000)
    return response

@router.post('/balance/send', tags=['balance'])
async def send_money():
    ...

@router.post('/balance/topup', tags=['balance'])
async def top_up_balance():
    ...

@router.post('/balance/deposit', tags=['balance'])
async def deposit_balance():
    ...