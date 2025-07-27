from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Path
from sqlalchemy.orm import Session
from typing import Optional, List
import json
from database import get_db
import models
from utils.file import save_uploaded_file, delete_uploaded_file
from schemas.category import CategoryCreate, CategoryResponse
from auth.utils import get_current_user
router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_categories(category_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Categories).filter(models.Categories.id == category_id).first()
    if not result:
        raise HTTPException(status_code=404, detail='category is not found')
    return result

@router.post("/", response_model=CategoryResponse)
async def create_categories(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    image: UploadFile = File(...)
):
    image_main_file = save_uploaded_file(image)

    db_category = models.Categories(
        name=name,
        description=description,
        image=image_main_file
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category



@router.delete("/{category_id}", response_model=dict)
def delete_product(category_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    category = db.query(models.Categories).filter(models.Categories.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if category.image:
        delete_uploaded_file(file=category.image)

    db.delete(category)
    db.commit()
    return {"detail":"Category Eliminated"}


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_product(
    current_user: dict = Depends(get_current_user),
    category_id: int = Path(...),
    db: Session = Depends(get_db),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    category = db.query(models.Categories).filter(models.Categories.id == category_id).first()
    if image:
        if category.image:
            delete_uploaded_file(file=category.image)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if name is not None:
        category.name = name
    if description is not None:
        category.description = description
    if image:
        category.image = save_uploaded_file(image)

    db.commit()
    db.refresh(category)
    return category