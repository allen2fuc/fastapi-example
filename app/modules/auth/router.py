import random
import string

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import BaseModel
from redis.asyncio import Redis

from app.core.dept import get_user_crud
from app.core.jinja import render_template
from app.core.middleware import _REMEMBER_COOKIE, _REMEMBER_MAX_AGE, make_remember_token
from app.core.redis import get_redis, rate_limit, rate_limit_incr, rate_limit_reset
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
    import time
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    request.session[_CAPTCHA_KEY] = code.upper()
    request.session[_CAPTCHA_KEY + "_at"] = int(time.time())
    svg = _make_captcha_svg(code)
    return Response(content=svg, media_type="image/svg+xml",
                    headers={"Cache-Control": "no-store"})


# ── 登录 ────────────────────────────────────────────────────────────────────

@router.get("/login")
async def login_page(request: Request):
    return render_template(request, "auth/login.jinja", {})


@router.post("/login", dependencies=[rate_limit(max_attempts=5, window=60, key_prefix="login")])
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    captcha_input: str = Form(...),
    remember_me: str = Form(""),
    user_crud: UserCrud = Depends(get_user_crud),
    redis: Redis = Depends(get_redis),
):
    import time
    expected = request.session.pop(_CAPTCHA_KEY, "")
    generated_at = request.session.pop(_CAPTCHA_KEY + "_at", 0)
    if not expected or captcha_input.upper() != expected:
        await rate_limit_incr(request, redis)
        return render_template(request, "auth/login.jinja",
                               {"error": "验证码错误"}, status_code=400)
    if int(time.time()) - generated_at > 60:
        return render_template(request, "auth/login.jinja",
                               {"error": "验证码已过期，请刷新"}, status_code=400)

    user = await user_crud.get_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        await rate_limit_incr(request, redis)
        attempts = int(await redis.get(request.state.rate_limit_key) or 0)
        remaining = max(5 - attempts, 0)
        hint = f"，还剩 {remaining} 次机会" if remaining > 0 else "，账号已被临时锁定"
        return render_template(request, "auth/login.jinja",
                               {"error": f"邮箱或密码错误{hint}"}, status_code=400)

    if not user.is_active:
        return render_template(request, "auth/login.jinja",
                               {"error": "账号已停用"}, status_code=400)

    await rate_limit_reset(request, redis)

    request.session[USER_ID_KEY] = user.id
    request.session["user_email"] = user.email
    request.session["is_superuser"] = user.is_superuser
    if not user.is_superuser:
        request.session["permissions"] = await user_crud.get_permissions(user.id)
    redirect = RedirectResponse(url="/dashboard", status_code=303)
    if remember_me:
        redirect.set_cookie(
            _REMEMBER_COOKIE,
            make_remember_token(user.id),
            max_age=_REMEMBER_MAX_AGE,
            httponly=True,
            samesite="lax",
        )
    return redirect


# ── 退出 ────────────────────────────────────────────────────────────────────

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie(_REMEMBER_COOKIE)
    return response


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
