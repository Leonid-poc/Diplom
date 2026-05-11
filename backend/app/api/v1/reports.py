"""Аналитические отчёты."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.analytics import AnalyticsReport
from app.models.user import User
from app.schemas.analytics import AnalyticsReportRead

router = APIRouter()


@router.get("", response_model=list[AnalyticsReportRead])
def list_reports(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return db.execute(
        select(AnalyticsReport).order_by(AnalyticsReport.created_at.desc())
    ).scalars().all()
