"""
Books router for book management endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Book, User
from sqlalchemy import func
from app.schemas.schemas import BookCreate, BookUpdate, BookResponse, BookDetailResponse, BookStatsResponse
from app.auth.auth import get_current_user

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/stats", response_model=BookStatsResponse)
async def get_book_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about books.
    
    Returns:
        Book statistics (total, available, etc.)
    """
    total_books = db.query(func.count(Book.book_id)).scalar()
    available_books = db.query(func.count(Book.book_id)).filter(Book.status == "可借閱").scalar()
    on_loan_books = db.query(func.count(Book.book_id)).filter(Book.status == "借閱中").scalar()
    donation_books = db.query(func.count(Book.book_id)).filter(Book.book_category == "捐贈").scalar()
    self_bought_books = db.query(func.count(Book.book_id)).filter(Book.book_category == "自購").scalar()
    on_behalf_books = db.query(func.count(Book.book_id)).filter(Book.book_category == "代管").scalar()
    
    return {
        "total_books": total_books,
        "available_books": available_books,
        "on_loan_books": on_loan_books,
        "donation_books": donation_books,
        "self_bought_books": self_bought_books,
        "on_behalf_books": on_behalf_books,
    }   


@router.get("/", response_model=List[BookDetailResponse])
async def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    book_category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of books with optional filtering.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        status: Filter by book status
        book_category: Filter by book category
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of books
    """
    query = db.query(Book)
    
    if status:
        query = query.filter(Book.status == status)
    
    if book_category:
        query = query.filter(Book.book_category == book_category)
    
    books = query.offset(skip).limit(limit).all()
    return books


@router.get("/{book_id}", response_model=BookDetailResponse)
async def get_book(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific book by ID.
    
    Args:
        book_id: Book ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Book object
        
    Raises:
        HTTPException: If book not found
    """
    book = db.query(Book).filter(Book.book_id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    return book


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new book.
    
    Args:
        book_data: Book creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created book object
        
    Raises:
        HTTPException: If book ID already exists
    """
    # Check if book ID already exists
    existing_book = db.query(Book).filter(Book.book_id == book_data.book_id).first()
    
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book with ID {book_data.book_id} already exists"
        )
    
    # Create new book
    new_book = Book(**book_data.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    return new_book


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a book.
    
    Args:
        book_id: Book ID
        book_data: Book update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated book object
        
    Raises:
        HTTPException: If book not found
    """
    book = db.query(Book).filter(Book.book_id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    # Update book fields
    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    
    db.commit()
    db.refresh(book)
    
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a book.
    
    Args:
        book_id: Book ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If book not found
    """
    book = db.query(Book).filter(Book.book_id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    db.delete(book)
    db.commit()
    
    return None
