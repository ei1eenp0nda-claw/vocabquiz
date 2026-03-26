"""
User model for ProteinHub authentication system.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt

Base = declarative_base()


class User(Base):
    """
    User model for storing user authentication information.
    
    Attributes:
        id (int): Primary key
        username (str): Unique username
        email (str): Unique email address
        password_hash (str): Bcrypt hashed password
        created_at (datetime): Account creation timestamp
        updated_at (datetime): Last update timestamp
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def set_password(self, password: str) -> None:
        """
        Hash and set the user password using bcrypt.
        
        Args:
            password (str): Plain text password to hash
        """
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert user object to dictionary.
        
        Args:
            include_sensitive (bool): If True, include password hash
            
        Returns:
            dict: User data dictionary
        """
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data
    
    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


# Database setup helpers
def init_db(database_url: str = 'sqlite:///proteinhub.db'):
    """
    Initialize the database with all tables.
    
    Args:
        database_url (str): SQLAlchemy database URL
        
    Returns:
        tuple: (engine, Session) - SQLAlchemy engine and session class
    """
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session
