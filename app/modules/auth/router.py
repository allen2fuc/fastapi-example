import random
import string

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import BaseModel

from app.core.dept import get_user_crud
from app.core.jinja import render_template
from app.core.security import USER_ID_KEY, get_current_user, get_password_hash, verify_password
from app.models.user import User
from app.modules.user.crud import UserCrud

router = APIRouter()

_CAPTCHA_KEY = "captcha_code"


def _make_captcha_svg(code: str) -> str:
    """生成简单 SVG 验证码图片"""
    width, height = 120, 40
    bg_color = "#f0f4ff"
    chars = []
    colors = ["#1d4ed8", "#7c3aed", "#b45309", "#065f46", "#9d174d"]
    for i, ch in enumerate(code):
        x = 12 + i * 20 + random.randint(-3, 3)
        y = 26 + random.randint(-4, 4)
        rotate = random.randint(-18, 18)
        color = colors[i % len(colors)]
        chars.append(
            f'<text x="{x}" y="{y}" fill="{color}" font-size="22" font-weight="bold" '
            f'font-family="monospace" transform="rotate({rotate},{x},{y})">{ch}</text>'
        )
    # 干扰线
    lines = []
    for _ in range(4):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        r, g, b = random.randint(150, 220), random.randint(150, 220), random.randint(150, 220)
        lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="rgb({r},{g},{b})" stroke-width="1"/>')
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        f'<rect width="{width}" height="{height}" fill="{bg_color}" rx="4"/>'
        + "".join(lines)
        + "".join(chars)
        + "</svg>"
    )
    return svg


# ── 验证码 ──────────────────────────────────────────────────────────────────

@router.get("/captcha")
async def captcha(request: Request):
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    request.session[_CAPTCHA_KEY] = code.upper()
    svg = _make_captcha_svg(code)
    return Response(content=svg, media_type="image/svg+xml",
                    headers={"Cache-Control": "no-store"})


# ── 登录 ────────────────────────────────────────────────────────────────────

@router.get("/login")
async def login_page(request: Request):
    return render_template(request, "auth/login.jinja", {})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    captcha_input: str = Form(...),
    user_crud: UserCrud = Depends(get_user_crud),
):
    expected = request.session.pop(_CAPTCHA_KEY, "")
    if captcha_input.upper() != expected:
        return render_template(request, "auth/login.jinja",
                               {"error": "验证码错误"}, status_code=400)

    user = await user_crud.get_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        return render_template(request, "auth/login.jinja",
                               {"error": "邮箱或密码错误"}, status_code=400)

    if not user.is_active:
        return render_template(request, "auth/login.jinja",
                               {"error": "账号已停用"}, status_code=400)

    request.session[USER_ID_KEY] = user.id
    request.session["user_email"] = user.email
    return RedirectResponse(url="/dashboard", status_code=303)


# ── 退出 ────────────────────────────────────────────────────────────────────

@router.post("/logout")
async def logout(request: Request):
    request.session.pop(USER_ID_KEY, None)
    request.session.pop("user_email", None)
    return RedirectResponse(url="/auth/login", status_code=303)


# ── 修改密码（需要已登录，不需要特定权限） ──────────────────────────────────

class ChangePasswordBody(BaseModel):
    old_password: str
    new_password: str


@router.post("/change-password")
async def change_password(
    body: ChangePasswordBody,
    current_user: User = Depends(get_current_user),
    user_crud: UserCrud = Depends(get_user_crud),
):
    if not verify_password(body.old_password, current_user.hashed_password):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="当前密码错误")
    await user_crud.update(current_user, {"hashed_password": get_password_hash(body.new_password)})
    return {"ok": True}
