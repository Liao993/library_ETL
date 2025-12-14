"""
Transactions router for borrow/return management.
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.models import Transaction, Book, User
from app.schemas.schemas import TransactionCreate, TransactionResponse, TransactionDetailResponse
from app.auth.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=List[TransactionDetailResponse])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    book_id: Optional[str] = None,
    teacher_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of transactions with optional filtering.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        book_id: Filter by book ID
        teacher_id: Filter by teacher ID
        action: Filter by action (borrow/return)
        start_date: Filter by start date
        end_date: Filter by end date
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of transactions
    """
    query = db.query(Transaction)
    
    if book_id:
        query = query.filter(Transaction.book_id == book_id)
    
    if teacher_id:
        query = query.filter(Transaction.teacher_id == teacher_id)
    
    if action:
        query = query.filter(Transaction.action == action)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    
    transactions = query.order_by(desc(Transaction.timestamp)).offset(skip).limit(limit).all()
    return transactions


@router.get("/{transaction_id}", response_model=TransactionDetailResponse)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific transaction by ID.
    
    Args:
        transaction_id: Transaction ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Transaction object
        
    Raises:
        HTTPException: If transaction not found
    """
    transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found"
        )
    
    return transaction


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new transaction and update book status.
    
    Args:
        transaction_data: Transaction creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created transaction object
        
    Raises:
        HTTPException: If book not found or invalid action
    """
    # Check if book exists
    book = db.query(Book).filter(Book.book_id == transaction_data.book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {transaction_data.book_id} not found"
        )
    
    # Validate action based on current book status
    if transaction_data.action == "借閱":
        if book.status != "可借閱":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book is currently {book.status} and cannot be borrowed"
            )
        new_status = "借閱中"
    
    elif transaction_data.action == "歸還":
        if book.status != "借閱中":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book is currently {book.status} and cannot be returned"
            )
        new_status = "可借閱"
    
    # Create transaction
    new_transaction = Transaction(**transaction_data.model_dump())
    db.add(new_transaction)
    
    # Update book status
    book.status = new_status
    
    db.commit()
    db.refresh(new_transaction)
    
    return new_transaction
