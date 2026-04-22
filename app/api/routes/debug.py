import os
import subprocess
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from markupsafe import escape

from app.db.session import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/ping")
def ping_host(host: str = Query(..., description="Host to ping")):
    # Уязвимость: Command Injection
    # Source: host параметр
    # Sink: subprocess.check_output
    
    command = f"ping -c 1 {host}"
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return {"output": output.decode()}
    except Exception as e:
        # Уязвимость: Детальная ошибка может раскрывать внутреннюю информацию
        return {"error": str(e)}

    # Уязвимость устранена: чистим input от спец символов
    # if not host.replace(".", "").replace("-", "").isalnum():
    #     raise HTTPException(status_code=400, detail="Invalid host format")
    
    # try:
    #     # Используем список аргументов без shell=True
    #     output = subprocess.check_output(["/bin/ping", "-c", "1", host], stderr=subprocess.STDOUT)
    #     return {"output": output.decode()}
    # except subprocess.CalledProcessError:
    #     return {"error": "Ping failed", "detail": "Host unreachable"}
    # except Exception:
    #     return {"error": "Internal server error"}


@router.get("/read-config")
def read_file(filename: str = Query(..., description="Config file to read")):
    # Уязвимость: Path Traversal
    # Source: filename parameter
    # Sink: open()
    
    # try:
    #     with open(filename, "r") as f:
    #         return {"content": f.read()}
    # except Exception as e:
    #     return {"error": str(e)}

    # Уязвимость устранена: ограничиваем доступ к определенной директории и проверяем путь
    SAFE_DIR = os.path.abspath("configs")
    if not os.path.exists(SAFE_DIR):
        os.makedirs(SAFE_DIR, exist_ok=True)
    
    requested_path = os.path.abspath(os.path.join(SAFE_DIR, filename))
    if not requested_path.startswith(SAFE_DIR):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        with open(requested_path, "r") as f:
            return {"content": f.read()}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Error reading file")


@router.get("/search-users")
def search_users(username: str, db: Session = Depends(get_db)):
    # Уязвимость: SQL Injection
    # Source: username parameter
    # Sink: db.execute(raw SQL)
    
    # query = f"SELECT * FROM users WHERE username = '{username}'"
    # result = db.execute(text(query))
    # return {"users": [dict(row._mapping) for row in result]}

    # Уязвимость устранена: используем параметризованные запросы
    query = text("SELECT * FROM users WHERE username = :username")
    result = db.execute(query, {"username": username})
    return {"users": [dict(row._mapping) for row in result]}


@router.get("/greet", response_class=HTMLResponse)
def greet_user(name: str):
    # Уязвимость: Cross-Site Scripting (XSS)
    # Source: name parameter
    # Sink: HTMLResponse with unescaped input
    
    # html_content = f"<h1>Hello, {name}!</h1>"
    # return HTMLResponse(content=html_content)

    # Уязвимость устранена: экранируем пользовательский ввод
    html_content = f"<h1>Hello, {escape(name)}!</h1>"
    return HTMLResponse(content=html_content)


@router.get("/debug-info")
def get_debug_info():
    # Уязвимость: Information Exposure (Sensitive Environment Variables)
    # Sink: Returning all environment variables
    # if settings.DEBUG:
    #     return dict(os.environ)
    # return {"status": "Debug is disabled"}

    # Уязвимость устранена: возвращаем только безопасную информацию
    if settings.debug:
        return {
            "app_name": "Telecom Billing MVP",
            "version": "1.0.0",
            "python_version": os.sys.version
        }
    return {"status": "Debug is disabled"}


@router.post("/legacy-login")
def legacy_login(username: str, password: str, db: Session = Depends(get_db)):
    # Уязвимость: Insecure Cryptography / Hardcoded Logic
    # if username == "admin" and password == "admin123":
    #     return {"token": "ADMIN_HARDCODED_TOKEN"}
    
    # # Уязвимость: SQL Injection in login
    # query = f"SELECT * FROM users WHERE username = '{username}' AND password_hash = '{password}'"
    # user = db.execute(text(query)).fetchone()

    # Уязвимость устранена: используем безопасную аутентификацию и параметризованные запросы
    from app.services import auth_service
    from app.schemas.auth import LoginRequest
    try:
        return auth_service.login(db, LoginRequest(username=username, password=password))
    except HTTPException:
        return {"status": "failure"}
