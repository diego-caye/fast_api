from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from database import Base
from sqlalchemy.orm import relationship

class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=False)
    image_main = Column(Text, index=False, nullable=True)
    images_secundary = Column(Text, index=False, nullable=True)
    active = Column(Boolean, index=True, nullable=False)

    categories = relationship(
        "Categories",
        secondary="categories_products",
        back_populates="products"
    )


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    image = Column(Text, nullable=True)

    products = relationship(
        "Products",
        secondary="categories_products",
        back_populates="categories"
    )

class Categories_Products(Base):
    __tablename__ = 'categories_products'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(Integer, unique=True)
    hashed_password = Column(String)