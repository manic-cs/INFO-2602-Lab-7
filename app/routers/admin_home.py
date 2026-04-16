from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, or_
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep
from app.models.user import User, Todo
from app.utilities.pagination import Pagination
from . import router, templates

@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    q: Optional[str] = None,
    done: str = "any",
    page: int = 1,
    limit: int = 10
):
    stmt = select(Todo).join(User)

    if q:
        stmt = stmt.where(
            or_(
                Todo.text.ilike(f"%{q}%"),
                User.username.ilike(f"%{q}%")
            )
        )

    if done == "true":
        stmt = stmt.where(Todo.done == True)
    elif done == "false":
        stmt = stmt.where(Todo.done == False)

    results = db.exec(stmt).all()
    total = len(results)
    pagination = Pagination(total, page, limit)

    stmt = stmt.offset(pagination.offset).limit(pagination.limit)
    todos = db.exec(stmt).all()

    return templates.TemplateResponse(
        request=request, 
        name="admin.html",
        context={
            "user": user,
            "todos": todos,
            "pagination": pagination,
            "q": q,
            "done": done
        }
    )
