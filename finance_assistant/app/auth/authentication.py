from flask import request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
import jwt
from datetime import datetime, timedelta
from ..models.user import User, db

class AuthenticationManager:
    """Handles user authentication with MFA support"""
    
    def __init__(self):
        self.mfa_required = True
    
    def register_user(self, email, password, first_name, last_name):
        """Register a new user with multi-factor authentication"""
        try:
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                return {'success': False, 'message': 'User already exists'}
            
            # Create new user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Generate MFA token (simplified - in production, use actual MFA service)
            mfa_token = self._generate_mfa_token(user.id)
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'mfa_token': mfa_token,
                'user_id': user.id
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
    
    def login_user(self, email, password, mfa_token=None):
        """Authenticate user with email, password and MFA"""
        try:
            user = User.query.filter_by(email=email).first()
            
            if not user or not user.check_password(password):
                return {'success': False, 'message': 'Invalid credentials'}
            
            if not user.is_active:
                return {'success': False, 'message': 'Account deactivated'}
            
            # Verify MFA token (simplified)
            if self.mfa_required and not self._verify_mfa_token(user.id, mfa_token):
                return {'success': False, 'message': 'Invalid MFA token'}
            
            # Log user in
            login_user(user)
            
            # Generate JWT token for API access
            auth_token = self._generate_auth_token(user.id)
            
            return {
                'success': True,
                'message': 'Login successful',
                'auth_token': auth_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _generate_mfa_token(self, user_id):
        """Generate MFA token (simplified implementation)"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(minutes=10)
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    def _verify_mfa_token(self, user_id, token):
        """Verify MFA token (simplified implementation)"""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload.get('user_id') == user_id
        except:
            return False
    
    def _generate_auth_token(self, user_id):
        """Generate JWT authentication token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')