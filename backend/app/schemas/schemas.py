"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, Literal


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=6)
    role: Literal["admin", "user"] = "user"


class UserResponse(UserBase):
    """Schema for user response."""
    user_id: int
    role: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Teacher Schemas
# ============================================================================

class TeacherBase(BaseModel):
    """Base teacher schema."""
    name: str = Field(..., min_length=1, max_length=100)
    classroom: Optional[str] = Field(None, max_length=50)


class TeacherCreate(TeacherBase):
    """Schema for creating a new teacher."""
    pass


class TeacherUpdate(BaseModel):
    """Schema for updating a teacher."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    classroom: Optional[str] = Field(None, max_length=50)


class TeacherResponse(TeacherBase):
    """Schema for teacher response."""
    teacher_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Location Schemas
# ============================================================================

class LocationBase(BaseModel):
    """Base location schema."""
    location_name: str = Field(..., min_length=1, max_length=100)


class LocationCreate(LocationBase):
    """Schema for creating a new location."""
    pass


class LocationUpdate(BaseModel):
    """Schema for updating a location."""
    location_name: Optional[str] = Field(None, min_length=1, max_length=100)


class LocationResponse(LocationBase):
    """Schema for location response."""
    location_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Book Schemas
# ============================================================================

class BookBase(BaseModel):
    """Base book schema."""
    name: str = Field(..., min_length=1, max_length=255)
    book_category: str = Field(..., min_length=1, max_length=50)
    book_category_label: str = Field(..., min_length=1, max_length=50)
    storage_location_id: Optional[int] = None


class BookCreate(BookBase):
    """Schema for creating a new book."""
    book_id: str = Field(..., min_length=1, max_length=50)


class BookUpdate(BaseModel):
    """Schema for updating a book."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    book_category: Optional[str] = Field(None, min_length=1, max_length=50)
    book_category_label: Optional[str] = Field(None, min_length=1, max_length=50)
    storage_location_id: Optional[int] = None
    status: Optional[Literal["Available", "On Loan", "Lost", "Archived"]] = None


class BookResponse(BookBase):
    """Schema for book response."""
    book_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BookDetailResponse(BookResponse):
    """Schema for detailed book response with relationships."""
    storage_location: Optional[LocationResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Transaction Schemas
# ============================================================================

class TransactionBase(BaseModel):
    """Base transaction schema."""
    book_id: str = Field(..., min_length=1, max_length=50)
    teacher_id: int
    action: Literal["borrow", "return"]
    transaction_date: date
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""
    pass


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""
    transaction_id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TransactionDetailResponse(TransactionResponse):
    """Schema for detailed transaction response with relationships."""
    book: Optional[BookResponse] = None
    teacher: Optional[TeacherResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Authentication Schemas
# ============================================================================

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str
