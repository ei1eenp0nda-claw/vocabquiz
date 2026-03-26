"""
ProteinHub Database Models
SQLAlchemy ORM models for the academic note sharing platform.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey,
    UniqueConstraint, Index, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import bcrypt

Base = declarative_base()


class User(Base):
    """User model for authentication and profile."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    avatar_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    notes = relationship("Note", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str) -> None:
        """Hash and set password."""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Note(Base):
    """Note model for academic content."""
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # JSON array as string
    cover_image = Column(String(255), nullable=True)
    view_count = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default='published', nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="notes")
    likes = relationship("Like", back_populates="note", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="note", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="note", cascade="all, delete-orphan")
    
    def to_dict(self, include_author=False) -> dict:
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'tags': self.tags,
            'cover_image': self.cover_image,
            'view_count': self.view_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'likes_count': len(self.likes) if self.likes else 0,
            'favorites_count': len(self.favorites) if self.favorites else 0,
            'comments_count': len(self.comments) if self.comments else 0
        }
        if include_author and self.author:
            data['author'] = self.author.to_dict()
        return data


class Like(Base):
    """Like model for note likes."""
    __tablename__ = 'likes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    note_id = Column(Integer, ForeignKey('notes.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'note_id', name='unique_user_note_like'),
    )
    
    # Relationships
    user = relationship("User", back_populates="likes")
    note = relationship("Note", back_populates="likes")


class Favorite(Base):
    """Favorite model for saved notes."""
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    note_id = Column(Integer, ForeignKey('notes.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'note_id', name='unique_user_note_favorite'),
    )
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    note = relationship("Note", back_populates="favorites")


class Comment(Base):
    """Comment model for note comments."""
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    note_id = Column(Integer, ForeignKey('notes.id', ondelete='CASCADE'), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey('comments.id', ondelete='CASCADE'), nullable=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="comments")
    note = relationship("Note", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id])
    
    def to_dict(self, include_user=False) -> dict:
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'note_id': self.note_id,
            'parent_id': self.parent_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_user and self.user:
            data['user'] = self.user.to_dict()
        return data


class Follow(Base):
    """Follow model for user following."""
    __tablename__ = 'follows'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    followed_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),
    )


# Database initialization
def init_db(database_url: str = 'postgresql://user:pass@localhost/proteinhub'):
    """Initialize database with all tables."""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session


if __name__ == '__main__':
    # Test database creation
    print("Creating database tables...")
    engine, Session = init_db('sqlite:///test_proteinhub.db')
    print("✅ Database tables created successfully!")
