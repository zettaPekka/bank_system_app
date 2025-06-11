from fastapi import APIRouter, Request, Response, HTTPException, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt_processing import create_jwt, check_jwt
from database.init_db import engine
from database.services.user_service import UserService
from database.services.transaction_service import TransactionService
from schemas.user_schema import UserSchema
from schemas.finance_schemas import TopupSchema, SendMoneySchema
from bank_transactions.producer import add_transaction_to_queue


router = APIRouter()


async def get_session():
    async with AsyncSession(engine) as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)


def get_transaction_service(session: AsyncSession = Depends(get_session)) -> TransactionService:
    return TransactionService(session)


@router.get('/profile/', tags=['🏠 Профиль'], summary='Профиль пользователя')
async def profile(request: Request, user_service: UserService = Depends(get_user_service)):
    current_jwt = request.cookies.get('access_token')
    if not current_jwt or not (uid := check_jwt(current_jwt)):
        raise HTTPException(status_code=401, detail='Unauthorized')

    user = await user_service.user_repo.get_user_by_id(uid)

    return {
        'login': user.login,
        'balance': user.balance,
        'history': user.history
    }


@router.post('/login/', tags=['🔐 Аутентификация'], summary='Логин')
async def login(user: UserSchema, request: Request, user_service: UserService = Depends(get_user_service)):
    current_jwt = request.cookies.get('access_token')
    if current_jwt and check_jwt(current_jwt):
        raise HTTPException(status_code=400, detail='Already logged in')

    user_info = await user_service.authenticate_user(user.login, user.password)
    if user_info:
        response_data = {'status': 'ok'}
        response = JSONResponse(content=response_data)
        response.set_cookie(key='access_token', value=create_jwt(user_info.id), max_age=2592000)
        return response

    raise HTTPException(status_code=400, detail='Invalid login or password')


@router.post('/registration/', tags=['🔐 Аутентификация'], summary='Регистрация')
async def registration(
    user: UserSchema,
    request: Request,
    user_service: UserService = Depends(get_user_service)
):
    current_jwt = request.cookies.get('access_token')
    if current_jwt and check_jwt(current_jwt):
        raise HTTPException(status_code=400, detail='Already logged in')

    success = await user_service.register_user(user.login, user.password)
    if not success:
        raise HTTPException(status_code=400, detail='User already exists')

    created_user = await user_service.user_repo.get_user_by_login(user.login)
    if not created_user:
        raise HTTPException(status_code=500, detail='User not found after registration')

    response_data = {'status': 'ok'}
    response = JSONResponse(content=response_data)
    response.set_cookie(key='access_token', value=create_jwt(created_user.id), max_age=2592000)
    return response


@router.post('/logout/', tags=['🔐 Аутентификация'], summary='Выход')
async def logout(response: Response):
    response.delete_cookie('access_token')
    return {'status': 'ok'}


@router.post('/balance/send/', tags=['💰 Финансы'], summary='Перевод денежных средств другому пользователю')
async def send_money(
    request: Request,
    data: SendMoneySchema = Body(),
    tx_service: TransactionService = Depends(get_transaction_service),
    user_service: UserService = Depends(get_user_service)
):
    current_jwt = request.cookies.get('access_token')
    if not current_jwt or not (uid := check_jwt(current_jwt)):
        raise HTTPException(status_code=401, detail='Unauthorized')

    sender = await user_service.user_repo.get_user_by_id(uid)

    if sender.login == data.receiver_login:
        raise HTTPException(status_code=400, detail='You can\'t send money to yourself')

    receiver_exists = await user_service.user_repo.get_user_by_login(data.receiver_login)
    if not receiver_exists:
        raise HTTPException(status_code=400, detail='User not found')

    if sender.balance < data.amount:
        raise HTTPException(status_code=400, detail='Not enough money')

    try:
        res = await tx_service.initiate_transfer(sender.login, data.receiver_login, data.amount)
        print(res)
        add_transaction_to_queue(sender.login, data.receiver_login, data.amount)
        return {'status': 'ok', 'message': 'Transaction added to queue'}
    except Exception as e:
        await tx_service.fail_transfer(sender.login, data.receiver_login, data.amount)
        raise HTTPException(status_code=500, detail='Transaction failed')


@router.post('/balance/topup/', tags=['💰 Финансы'], summary='Пополнить баланс')
async def top_up_balance(
    request: Request,
    amount: TopupSchema = Body(),
    user_service: UserService = Depends(get_user_service)
):
    current_jwt = request.cookies.get('access_token')
    if not current_jwt or not (uid := check_jwt(current_jwt)):
        raise HTTPException(status_code=401, detail='Unauthorized')

    user = await user_service.user_repo.get_user_by_id(uid)
    await user_service.add_balance_to_user(user, amount.amount)
    await user_service.session.commit()

    return {'status': 'ok'}


@router.post('/balance/deposit/', tags=['💰 Финансы'], summary='Банковский вклад')
async def deposit_balance():
    ...
