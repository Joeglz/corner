from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, oauth2
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from passlib.hash import bcrypt
import jwt
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .models import User, Data
import os

from .get_service_data import get_values

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title='Credi Justo', 
                description='Exposes the current exchange rate of USD to MXN from three different sources in the same endpoint.',
                version='1.0.1' )
        
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

JWT_SECRET = os.environ.get('JWT_SECRET')

User_Pydantic = pydantic_model_creator(User, name='User')

UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True )

Data_Pydantic = pydantic_model_creator(Data, name='Data')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def autenticate_user(username: str, password: str):
    user = await User.get(username=username)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user

async def create_token(username: str, password : str):
    user = await autenticate_user(username, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid Username or password'
        )
    
    user_obj = await User_Pydantic.from_tortoise_orm(user)

    user_encode = {
        'id' : user_obj.id,
        'username' : user_obj.username
    }

    token = jwt.encode(user_encode, JWT_SECRET )

    return token


@app.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await autenticate_user(form_data.username, form_data.password)

    token = await create_token(form_data.username, form_data.password)
    return {'access_token' : token, 'token_type' : 'bearer'}

async def check_token(token:str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = await User.get(id = payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid Username or password'
        )
    
    return await User_Pydantic.from_tortoise_orm(user)


@app.post('/users', response_model=User_Pydantic, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserIn_Pydantic):
    user_obj = User(username= user.username, password_hash=bcrypt.hash(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)

@app.get('/data')
@limiter.limit("5/minute")
async def get_data(request: Request, user: UserIn_Pydantic = Depends(check_token)):
    return await get_values()


register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models' : ['app.models']},
    generate_schemas = True,
    add_exception_handlers=True
)