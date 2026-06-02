import jwt
from functools import wraps
from flask import request, jsonify, current_app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({"error": "Authentication Token is missing!"}), 401
            
        try:
            # Decode token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Authentication Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid Authentication Token!"}), 401
        except Exception as e:
            return jsonify({"error": f"Authentication Token error: {str(e)}"}), 401
            
        return f(*args, **kwargs)
        
    return decorated

def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "API Key is missing!"}), 401
            
        if api_key != current_app.config.get('APP_API_KEY'):
            return jsonify({"error": "Invalid API Key!"}), 403
            
        return f(*args, **kwargs)
        
    return decorated
