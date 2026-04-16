from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select, or_, func
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
    q: str = "",
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

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(total_stmt)
    
    pagination = Pagination(total, page, limit)

    stmt = stmt.offset(pagination.offset).limit(pagination.limit)
    todos = db.scalars(stmt).all()

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
