from flask import Flask , jsonify , request
from app.database import init_db , db
from app.routes import register_user, login_user, get_all_posts, create_post, get_post, update_post, delete_post , create_category , get_all_category , get_category , update_category , delete_category, user_profile , update_user_profile , search_posts , add_comment , update_comment
from app.auth.jwt_helper import decode_token
from app.models.category import Category
from functools import wraps  
from app.models.user import User
from sqlalchemy.orm import joinedload

app = Flask(__name__)

init_db(app)

app.route('/register', methods=['POST'])(register_user)
app.route('/login', methods=['POST'])(login_user)   
app.route('/posts', methods=['GET'])(get_all_posts)
app.route('/posts/create', methods=['POST'])(create_post)
app.route('/posts/<int:post_id>', methods=['GET'])(get_post)
app.route('/posts/<int:post_id>/update', methods=['PUT'])(update_post)
app.route('/posts/<int:post_id>/delete', methods=['DELETE'])(delete_post)
app.route('/create_categories', methods=['POST'])(create_category)
app.route('/categories', methods=['GET'])(get_all_category)
app.route('/specific_categories/<int:category_id>', methods=['GET'])(get_category)
app.route('/update_categories/<int:category_id>', methods=['PUT'])(update_category)
app.route('/delete_categories/<int:category_id>', methods=['DELETE'])(delete_category)
app.route('/profile/<int:user_id>', methods=['GET'])(user_profile)
app.route('/profile/update/<int:user_id>', methods=['POST'])(update_user_profile)
app.route('/posts/search', methods = ['GET'])(search_posts)
app.route('/posts/comments/<int:post_id>', methods=['POST'])(add_comment)
app.route('/posts/comments/update/<int:post_id>/<int:comment_id>', methods=['PUT'])(update_comment)

def check_user_role(required_role):
    def decorator(func):
        @wraps(func)    
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if auth_header:
                token = auth_header.split(' ')[1]
                payload = decode_token(token)
                if payload and 'user_id' in payload:
                    user_id = payload['user_id']
                    with db.session() as session:
                        user = session.query(User).get(user_id)
                    if user:
                        if user.role.name == required_role:
                            return func(*args, **kwargs)
                        elif required_role == 'Admin':
                            return jsonify({'message': "Unauthorized access. Admin role required."}), 403
                        else:
                            return jsonify({'message': "Unauthorized access."}), 403
                    else:
                        return jsonify({'message': "User not found."}), 404
                else:
                    return jsonify({'message': "Invalid or expired token."}), 401
            else:
                return jsonify({'message': "Missing token."}), 401
        return wrapper
    return decorator


@app.route('/admin_only_route', methods =['GET'])
@check_user_role('Admin')

def admin_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = request.headers.get('user_id')
        user = db.session.query(User).get(user_id)
        
        if user and user.role.name == 'Admin':
            return f(user, *args, **kwargs)
        else:
            return jsonify({'message': 'Unauthorized'}), 401

    return wrapper


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'qwerty'
    app.run()