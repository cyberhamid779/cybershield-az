import csv
import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth import get_current_admin
from app.services.database import get_db

router = APIRouter()


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    department: str | None

    class Config:
        from_attributes = True


@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    return db.query(User).filter(User.org_id == current_user.org_id, User.is_admin == False).all()


@router.post("/upload-csv", summary="CSV ilə əməkdaş yüklə")
async def upload_employees_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    """
    CSV formatı: name,email,department
    Birinci sıra başlıqdır, atlanır.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Yalnız CSV fayl qəbul edilir")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))

    required_columns = {"name", "email", "department"}
    if not required_columns.issubset(set(reader.fieldnames or [])):
        raise HTTPException(
            status_code=400,
            detail=f"CSV-də bu sütunlar olmalıdır: {', '.join(required_columns)}",
        )

    added, skipped = 0, 0
    for row in reader:
        email = row["email"].strip().lower()
        if not email:
            skipped += 1
            continue
        exists = db.query(User).filter(User.email == email, User.org_id == current_user.org_id).first()
        if exists:
            skipped += 1
            continue
        user = User(
            org_id=current_user.org_id,
            email=email,
            name=row["name"].strip(),
            department=row.get("department", "").strip() or None,
            is_admin=False,
        )
        db.add(user)
        added += 1

    db.commit()
    return {"added": added, "skipped": skipped}
