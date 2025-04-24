from fastapi import APIRouter, Request, Response

from auth.jwt_processing import create_jwt, check_jwt
from database.cruds import add_user, check_user
from schemas import UserSchema


router = APIRouter()


@router.get('/profile/',
            tags=['profile'],
            summary='Профиль')
async def profile():
    ...

@router.post('/login/',
                tags=['auth'])
async def login(user: UserSchema):
    res = await check_user(user.login, user.password)
    if res:
        return {'status': 'ok'}
    return {'status': 'error', 'message': 'invalid login or password'}

@router.post('/registration/',
                tags=['auth'])
async def registration(user: UserSchema):
    res = await add_user(user.login, user.password)
    if res:
        return {'status': 'ok'}
    return {'status': 'error', 'message': 'user already exists'}

@router.post('/balance/send',
                tags=['balance'])
async def send_money():
    ...

@router.post('/balance/get',
                tags=['balance'])
async def top_up_balance():
    ...

@router.post('/balance/deposit',
                tags=['balance'])
async def deposit_balance():
    ...