from pydantic import BaseModel
from typing import List, Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_main: Optional[str] = None
    images_secundary: str
    active: bool

class ProductCreate(ProductBase):
    category_ids: Optional[List[int]] = None

class ProductResponse(ProductBase):
    id: int
