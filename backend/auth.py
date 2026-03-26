"""
Authentication module for ProteinHub.
Handles user registration, login, JWT token management, and authentication decorators.
"""
import re
import jwt
import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Blueprint, request, jsonify, current_app, g

# Import User model
from models.user import User

# Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'proteinhub-dev-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_HOURS = 24
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ==================== Validation Functions ====================

def validate_email(email: str) -> bool:
    """
    Validate email format using regex.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email format is valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    return True, ""


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format.
    
    Args:
        username (str): Username to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 80:
        return False, "Username must not exceed 80 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""


# ==================== JWT Functions ====================

def create_access_token(user_id: int) -> str:
    """
    Create a JWT access token for a user.
    
    Args:
        user_id (int): User's database ID
        
    Returns:
        str: Encoded JWT access token
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        'user_id': user_id,
        'type': 'access',
        'exp': expire,
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """
    Create a JWT refresh token for a user.
    
    Args:
        user_id (int): User's database ID
        
    Returns:
        str: Encoded JWT refresh token
    """
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': expire,
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str, expected_type: str = 'access') -> dict | None:
    """
    Decode and validate a JWT token.
    
    Args:
        token (str): JWT token to decode
        expected_type (str): Expected token type ('access' or 'refresh')
        
    Returns:
        dict | None: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get('type') != expected_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def extract_token_from_header() -> str | None:
    """
    Extract Bearer token from Authorization header.
    
    Returns:
        str | None: Token string or None if not found/invalid format
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    return parts[1]


# ==================== Decorators ====================

def require_auth(f):
    """
    Decorator to protect routes that require authentication.
    
    Extracts Bearer token from Authorization header, validates it,
    and sets g.current_user with the authenticated user.
    
    Returns:
        401 if no token provided or token is invalid/expired
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = extract_token_from_header()
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'message': 'Missing or invalid Authorization header. Use: Bearer <token>'
            }), 401
        
        payload = decode_token(token, expected_type='access')
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Invalid token',
                'message': 'Token is expired or invalid'
            }), 401
        
        # Get user from database
        Session = current_app.config.get('db_session')
        if not Session:
            return jsonify({
                'success': False,
                'error': 'Server error',
                'message': 'Database session not available'
            }), 500
        
        session = Session()
        try:
            user = session.query(User).filter_by(id=payload['user_id']).first()
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found',
                    'message': 'User associated with this token no longer exists'
                }), 401
            
            g.current_user = user
            return f(*args, **kwargs)
        finally:
            session.close()
    
    return decorated_function


# ==================== Route Handlers ====================

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Handle user registration.
    
    Request Body:
        - username (str): Unique username (3-80 chars, alphanumeric + underscore)
        - email (str): Valid email address
        - password (str): Password (min 8 chars)
    
    Returns:
        201: {"success": true, "user_id": int, "message": str}
        400: Validation error
        409: Username or email already exists
        500: Database error
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': 'Request body must be valid JSON'
        }), 400
    
    # Extract fields
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Validate required fields
    if not all([username, email, password]):
        return jsonify({
            'success': False,
            'error': 'Missing fields',
            'message': 'username, email, and password are required'
        }), 400
    
    # Validate username
    valid, error_msg = validate_username(username)
    if not valid:
        return jsonify({
            'success': False,
            'error': 'Invalid username',
            'message': error_msg
        }), 400
    
    # Validate email
    if not validate_email(email):
        return jsonify({
            'success': False,
            'error': 'Invalid email',
            'message': 'Please provide a valid email address'
        }), 400
    
    # Validate password
    valid, error_msg = validate_password_strength(password)
    if not valid:
        return jsonify({
            'success': False,
            'error': 'Weak password',
            'message': error_msg
        }), 400
    
    # Get database session
    Session = current_app.config.get('db_session')
    if not Session:
        return jsonify({
            'success': False,
            'error': 'Server error',
            'message': 'Database session not available'
        }), 500
    
    session = Session()
    try:
        # Check for existing username
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                return jsonify({
                    'success': False,
                    'error': 'Duplicate username',
                    'message': 'This username is already taken'
                }), 409
            else:
                return jsonify({
                    'success': False,
                    'error': 'Duplicate email',
                    'message': 'This email is already registered'
                }), 409
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        session.add(new_user)
        session.commit()
        
        return jsonify({
            'success': True,
            'user_id': new_user.id,
            'message': 'User registered successfully'
        }), 201
        
    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': 'Failed to create user account'
        }), 500
    finally:
        session.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Handle user login.
    
    Request Body:
        - email (str): User's email address
        - password (str): User's password
    
    Returns:
        200: {"success": true, "access_token": str, "refresh_token": str}
        400: Missing fields
        401: Invalid credentials
        500: Database error
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Invalid request',
            'message': 'Request body must be valid JSON'
        }), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({
            'success': False,
            'error': 'Missing fields',
            'message': 'email and password are required'
        }), 400
    
    # Get database session
    Session = current_app.config.get('db_session')
    if not Session:
        return jsonify({
            'success': False,
            'error': 'Server error',
            'message': 'Database session not available'
        }), 500
    
    session = Session()
    try:
        # Find user by email
        user = session.query(User).filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'error': 'Invalid credentials',
                'message': 'Email or password is incorrect'
            }), 401
        
        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': ACCESS_TOKEN_EXPIRE_HOURS * 3600
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Server error',
            'message': 'Login failed due to server error'
        }), 500
    finally:
        session.close()


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    Get current authenticated user's information.
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
        200: {"success": true, "user": {...}}
        401: Not authenticated (handled by @require_auth)
    """
    user = g.current_user
    return jsonify({
        'success': True,
        'user': user.to_dict(include_sensitive=False)
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh access token using refresh token.
    
    Request Body:
        - refresh_token (str): Valid refresh token
    
    Returns:
        200: {"success": true, "access_token": str}
        400: Missing refresh token
        401: Invalid refresh token
    """
    data = request.get_json()
    
    if not data or not data.get('refresh_token'):
        return jsonify({
            'success': False,
            'error': 'Missing token',
            'message': 'refresh_token is required'
        }), 400
    
    payload = decode_token(data['refresh_token'], expected_type='refresh')
    
    if not payload:
        return jsonify({
            'success': False,
            'error': 'Invalid token',
            'message': 'Refresh token is expired or invalid'
        }), 401
    
    # Generate new access token
    new_access_token = create_access_token(payload['user_id'])
    
    return jsonify({
        'success': True,
        'access_token': new_access_token,
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRE_HOURS * 3600
    }), 200


def init_auth(app, db_session):
    """
    Initialize authentication blueprint with the Flask app.
    
    Args:
        app: Flask application instance
        db_session: SQLAlchemy session class
    """
    app.config['db_session'] = db_session
    app.register_blueprint(auth_bp)
