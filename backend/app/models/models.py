"""
SQLAlchemy database models for the library management system.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'user')", name="check_user_role"),
    )


class Teacher(Base):
    """Teacher model - represents borrowers."""
    __tablename__ = "teachers"
    
    teacher_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    classroom = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="teacher")



class Location(Base):
    """Location model for storage locations."""
    __tablename__ = "locations"
    
    location_id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    books = relationship("Book", back_populates="storage_location")


class Book(Base):
    """Book model - the main inventory."""
    __tablename__ = "books"
    
    book_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    book_category = Column(String(50), nullable=False)
    book_category_label = Column(String(50), nullable=False)
    storage_location_id = Column(Integer, ForeignKey("locations.location_id", ondelete="SET NULL"))
    status = Column(String(20), default="可借閱", nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    storage_location = relationship("Location", back_populates="books")
    transactions = relationship("Transaction", back_populates="book")
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('可借閱', '不可借閱', '遺失', '非管理中')", 
            name="check_book_status"
        ),
    )


class Transaction(Base):
    """Transaction model for borrow/return records."""
    __tablename__ = "transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(String(50), ForeignKey("books.book_id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id", ondelete="CASCADE"), nullable=False)
    action = Column(String(10), nullable=False)
    transaction_date = Column(Date, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
    
    # Relationships
    book = relationship("Book", back_populates="transactions")
    teacher = relationship("Teacher", back_populates="transactions")
    
    __table_args__ = (
        CheckConstraint("action IN ('借閱', '歸還')", name="check_transaction_action"),
    )
