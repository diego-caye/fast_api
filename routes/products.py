from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Path
from sqlalchemy.orm import Session
from typing import Optional, List
import json
from database import get_db
import models
from utils.file import save_uploaded_file, delete_uploaded_file
from schemas.product import ProductResponse
from auth.utils import get_current_user

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_products(product_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not result:
        raise HTTPException(status_code=404, detail='product is not found')
    return result

@router.post("/", response_model=ProductResponse)
async def create_product(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    image_main: UploadFile = File(...),
    images_secundary: List[UploadFile] = File(...),
    active: bool = Form(...),
    category_ids: Optional[str] = Form(None)
):

    image_main_path = save_uploaded_file(image_main)
    image_paths = [save_uploaded_file(img) for img in images_secundary]


    db_product = models.Products(
        name=name,
        description=description,
        image_main=image_main_path,
        images_secundary=json.dumps(image_paths),
        active=active
    )

    if category_ids:
        try:
            category_ids = [int(i) for i in category_ids.split(",")]
        except:
            raise HTTPException(status_code=400, detail="category_ids debe ser separados por coma, como: 1,2")

        categories = db.query(models.Categories).filter(models.Categories.id.in_(category_ids)).all()
        db_product.categories = categories

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", response_model=dict)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.image_main:
        delete_uploaded_file(file=product.image_main)
    if product.images_secundary:
        try:
            image_list = json.loads(product.images_secundary)
            delete_uploaded_file(multiple_file=image_list)
        except json.JSONDecodeError:
            pass

    db.delete(product)
    db.commit()
    return {"detail":"Product Eliminated"}

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    current_user: dict = Depends(get_current_user),
    product_id: int = Path(...),
    db: Session = Depends(get_db),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    image_main: Optional[UploadFile] = File(None),
    images_secundary: Optional[List[UploadFile]] = File(None),
    active: Optional[bool] = Form(None),
    category_ids: Optional[str] = Form(None)
):
    product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if image_main:
        if product.image_main:
            delete_uploaded_file(file=product.image_main)
    if images_secundary:
        if product.images_secundary:
            try:
                image_list = json.loads(product.images_secundary)
                delete_uploaded_file(multiple_file=image_list)
            except json.JSONDecodeError:
                pass

    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if active is not None:
        product.active = active
    if image_main:
        product.image_main = save_uploaded_file(image_main)
    if images_secundary:
        paths = [save_uploaded_file(img) for img in images_secundary]
        product.images_secundary = json.dumps(paths)

    if category_ids:
        try:
            ids = [int(cid) for cid in category_ids.split(",")]
        except:
            raise HTTPException(status_code=400, detail="category_ids must be comma separated: 1,2,3")

        categories = db.query(models.Categories).filter(models.Categories.id.in_(ids)).all()
        product.categories = categories
    else:
        product.categories = []

    db.commit()
    db.refresh(product)
    return product
