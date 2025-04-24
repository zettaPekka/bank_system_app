from fastapi import APIRouter, Request, Response

from auth.jwt_processing import create_jwt, check_jwt


router = APIRouter()


@router.get('/')
async def index():
    return {'app': 'bank'}

@router.get('/profile/')
async def profile():
    ...

@router.post('/login/')
async def login():
    ...

@router.post('/registration/')
async def registration():
    ...

@router.post('/balance/send')
async def send_money():
    ...

@router.post('/balance/get')
async def top_up_balance():
    ...

@router.post('/balance/deposit')
async def deposit_balance():
    ...