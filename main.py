from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session, select
from database.db import engine, get_session
from models.book import Book
from models.category import Category

app = FastAPI(title="Library Management API")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"message": "Library Management API"}

# === Book Endpoints ===

@app.post("/books/", response_model=Book)
def create_book(book: Book, session: Session = Depends(get_session)):
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@app.get("/books/", response_model=list[Book])
def list_books(available: bool | None = None, session: Session = Depends(get_session)):
    query = select(Book)
    if available is not None:
        query = query.where(Book.is_available == available)
    return session.exec(query).all()

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_update: Book, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.title = book_update.title
    book.author = book_update.author
    book.isbn = book_update.isbn
    book.is_available = book_update.is_available
    book.category_id = book_update.category_id
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

# === Category Endpoints ===

@app.post("/categories/", response_model=Category)
def create_category(category: Category, session: Session = Depends(get_session)):
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@app.get("/categories/", response_model=list[Category])
def list_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()

@app.get("/categories/{category_id}", response_model=Category)
def get_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
# === Exercise 2: Search Endpoint ===

@app.get("/books/search/", response_model=list[Book])
def search_books(
    author: str | None = None,
    title: str | None = None,
    session: Session = Depends(get_session),
):
    query = select(Book)
    if author:
        query = query.where(Book.author.ilike(f"%{author}%"))
    if title:
        query = query.where(Book.title.ilike(f"%{title}%"))
    return session.exec(query).all()


# === Exercise 3: Patch Endpoint ===

from typing import Optional as OptionalType

class BookUpdate(SQLModel):
    title: OptionalType[str] = None
    author: OptionalType[str] = None
    isbn: OptionalType[str] = None
    is_available: OptionalType[bool] = None
    category_id: OptionalType[int] = None

@app.patch("/books/{book_id}", response_model=Book)
def patch_book(book_id: int, book_update: BookUpdate, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book