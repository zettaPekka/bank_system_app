from fastapi import APIRouter, Request, Response, HTTPException, Body
from fastapi.responses import JSONResponse

from auth.jwt_processing import create_jwt, check_jwt
from database.cruds import add_user, check_user, get_user_by_id, get_user_id_by_login, add_balance, add_transaction_to_history
from schemas import UserSchema, TopupSchema, SendMoneySchema
from bank_transactions.bank_transfer_handler import add_transaction_to_queue


router = APIRouter()

@router.get('/profile/', tags=['🏠 Профиль'], summary='Профиль пользователя')
async def profile(request: Request):
    current_jwt = request.cookies.get('access_token')
    if not current_jwt or not (uid := check_jwt(current_jwt)):
        raise HTTPException(status_code=401, detail='Unauthorized')

    user = await get_user_by_id(uid)

    return {
        'login': user.login,
        'balance': user.balance,
        'history': user.history
    }


@router.post('/login/', tags=['🔐 Аутентификация'], summary='Логин')
async def login(user: UserSchema, request: Request):
    current_jwt = request.cookies.get('access_token')
    if current_jwt and check_jwt(current_jwt):
        raise HTTPException(status_code=400, detail='Already logged in')

    user_info = await check_user(user.login, user.password)
    if user_info: 
        response_data = {'status': 'ok'}
        response = JSONResponse(content=response_data)
        response.set_cookie(key='access_token', value=create_jwt(user_info.id), max_age=64000)
        return response

    raise HTTPException(status_code=400, detail='Invalid login or password')


@router.post('/registration/', tags=['🔐 Аутентификация'], summary='Регистрация')
async def registration(user: UserSchema, request: Request):
    current_jwt = request.cookies.get('access_token')
    if current_jwt and check_jwt(current_jwt):
        raise HTTPException(status_code=400, detail='Already logged in')

    res = await add_user(user.login, user.password)
    if not res:
        raise HTTPException(status_code=400, detail='User already exists')

    user_id = await get_user_id_by_login(user.login)
    response_data = {'status': 'ok'}
    response = JSONResponse(content=response_data)
    response.set_cookie(key='access_token', value=create_jwt(user_id), max_age=64000)
    return response


@router.post('/logout/', tags=['🔐 Аутентификация'], summary='Выход')
async def logout(response: Response):
    response.delete_cookie('access_token')
    return {'status': 'ok'}


@router.post('/balance/send/', tags=['💰 Финансы'], summary='Перевод денежных средств другому рользователю')
async def send_money(request: Request, data: SendMoneySchema = Body()):
    current_jwt = request.cookies.get('access_token')
    if not current_jwt or not (uid := check_jwt(current_jwt)):
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    sender = await get_user_by_id(uid)
    
    if sender.login == data.receiver_login:
        raise HTTPException(status_code=400, detail='You can\'t send money to yourself')
    
    to_user = await get_user_id_by_login(data.receiver_login)
    if not to_user:
        raise HTTPException(status_code=400, detail='User not found')

    if sender.balance < data.amount:
        raise HTTPException(status_code=400, detail='Not enough money')
    
    await add_transaction_to_history(sender.login, data.receiver_login, data.amount)
    await add_transaction_to_queue(sender.login, data.receiver_login, data.amount)
    return {'status': 'ok', 'message': 'Transaction added to queue'}


@router.post('/balance/topup/', tags=['💰 Финансы'], summary='Пополнить баланс')
async def top_up_balance(request: Request, amount: TopupSchema = Body()):
    current_jwt = request.cookies.get('access_token')
    if not current_jwt or not (uid := check_jwt(current_jwt)):
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    await add_balance(uid, amount.amount)
    return {'status': 'ok'}


@router.post('/balance/deposit/', tags=['💰 Финансы'], summary='Банковский вклад')
async def deposit_balance():
    ...