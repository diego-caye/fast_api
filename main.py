from fastapi import FastAPI, HTTPException, Depends, UploadFile, Form, File, Path
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
import json

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    image: str

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_main: Optional[str] = None
    images_secundary: str
    active: bool

class ProductCreate(ProductBase):
    category_ids: Optional[List[int]] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_uploaded_file(upload_file: UploadFile, upload_dir: str = "uploads") -> str:
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(upload_file.filename)[1]
    
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())

    return file_path

def delete_uploaded_file(file: str = None, multiple_file: list[str] = None):
    if file and os.path.exists(file):
        os.remove(file)

    if multiple_file:
        for f in multiple_file:
            path = os.path.normpath(f)
            if os.path.exists(path):
                os.remove(path)

    return ""


@app.get("/products/{product_id}")
async def get_products(product_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not result:
        raise HTTPException(status_code=404, detail='product is not found')
    return result

@app.get("/category/{category_id}")
async def get_categories(category_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Categories).filter(models.Categories.id == category_id).first()
    if not result:
        raise HTTPException(status_code=404, detail='category is not found')
    return result

@app.post("/products/")
async def create_product(
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


@app.post("/category/")
async def create_categories(
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

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Products).filter(models.Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
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

@app.delete("/category/{category_id}")
def delete_product(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Categories).filter(models.Categories.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    if category.image:
        delete_uploaded_file(file=category.image)

    db.delete(category)
    db.commit()
    return {"detail":"Category Eliminated"}

@app.put("/products/{product_id}")
async def update_product(
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
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
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
            raise HTTPException(status_code=400, detail="category_ids debe ser coma separados: 1,2,3")

        categories = db.query(models.Categories).filter(models.Categories.id.in_(ids)).all()
        product.categories = categories
    else:
        product.categories = []

    db.commit()
    db.refresh(product)
    return product

@app.put("/category/{category_id}")
async def update_product(
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
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if name is not None:
        category.name = name
    if description is not None:
        category.description = description
    if image:
        category.image = save_uploaded_file(image)

    db.commit()
    db.refresh(category)
    return category