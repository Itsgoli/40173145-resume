from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Form
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import asyncio
from fastapi import WebSocket



app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="SUPER_SECRET_KEY_123"
)

requests_data = []
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "goli"

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("resume.html", {"request": request})

@app.post("/request")
def request_form(
    name: str = Form(...),
    email: str = Form(...),
    description: str = Form(...),
    project_type: str = Form(...),
    budget: int = Form(...)
):
    requests_data.append({
    "id": len(requests_data),   
    "name": name,
    "email": email,
    "description": description,
    "project_type": project_type,
    "budget": budget,
    "status": "در انتظار"
})

    return RedirectResponse("/", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    if not request.session.get("admin"):
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "data": requests_data}
    )



@app.get("/admin/delete/{req_id}")
def delete_request(req_id: int):
    global requests_data
    requests_data = [
        r for r in requests_data if r["id"] != req_id
    ]
    return RedirectResponse("/admin", status_code=303)

@app.get("/admin/status/{req_id}/{new_status}")
def change_status(req_id: int, new_status: str):
    for r in requests_data:
        if r["id"] == req_id:
            r["status"] = new_status
            break
    return RedirectResponse("/admin", status_code=303)


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})

@app.post("/login")
def login_post(request: Request,
               user_login: str = Form(...),
               user_pass: str = Form(...)):
    if user_login == ADMIN_USERNAME and user_pass == ADMIN_PASSWORD:
        request.session["admin"] = True
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "نام کاربری یا رمز عبور اشتباه است"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

active_connections: list[WebSocket] = []

@app.websocket("/ws/online")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            for conn in active_connections:
                await conn.send_text(str(len(active_connections)))
            await asyncio.sleep(1)
    except Exception as e:
        print("WebSocket error:", e)
    finally:
        active_connections.remove(websocket)


