from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.schemas.user import LoginUser, UserCreate, UserResponse
from app.crud.user import user_crud
from app.dependencies import db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Login")

templates = Jinja2Templates(directory='app/templates')
router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(db.get_db)):
    return user_crud.create_user(db, user_data)
  

@router.post("/Login", response_class=HTMLResponse)
def login(res: Request, login_input: LoginUser, db: Session = Depends(db.get_db)):
        user_name = (user_crud.login_user(db, login_input))
        return templates.TemplateResponse('login.html', {'request': res, "name": user_name})
