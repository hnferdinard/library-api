from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.category import Category

class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: str
    isbn: str = Field(unique=True)
    is_available: bool = Field(default=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    category: Optional["Category"] = Relationship(back_populates="books")