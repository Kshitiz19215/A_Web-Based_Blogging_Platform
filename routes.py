from flask import Flask, request, jsonify
from app.models.user import User
from app.models.posts import Post
from app.models.role import Role
from app.models.posts import Comment
from app.database import db
from app.auth.jwt_helper import encode_token , decode_token      
from app.models.category import Category   
from sqlalchemy import or_  

REGULAR_USER_ROLE_ID = 1

def register_user():
    if request.method == 'POST':
        username = request.json.get('username')
        email = request.json.get('email')
        password = request.json.get('password')
        role_name = request.json.get('role', 'User')
        first_name = request.json.get('first_name')
        last_name = request.json.get('last_name')
        bio = request.json.get('bio')
        profile_picture = request.json.get('profile_picture')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'Email already exists'})

        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return jsonify({'message': f"Role '{role_name}' does not exist. Please provide a valid role."}), 400

        new_user = User(username=username, email=email, password=password, role_id=role.id,
                        first_name=first_name, last_name=last_name, bio=bio, profile_picture=profile_picture)

        try:
            db.session.add(new_user)
            db.session.commit()
            token = encode_token(new_user.id)
            if role_name == 'Editor':
                return jsonify({'message': 'Editor registered successfully', 'token': token})
            elif role_name == 'User':
                return jsonify({'message': 'User registered successfully', 'token': token})
            elif role_name == 'Admin':
                return jsonify({'message': 'Admin registered successfully', 'token': token})
            else:
                return jsonify({'message': 'User registered successfully with an unknown role', 'token': token})

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Failed to register user.'}), 500

    
def login_user():
    if request.method == 'POST':
        email = request.json.get('email')
        password = request.json.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            token = encode_token(user.id)
            role = user.role.name 
            return jsonify({'message': 'Login successful', 'token': token, 'role': role})
        else:
            return jsonify({'message': 'Invalid credentials'})

def create_post():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        if payload:
            title = request.json.get('title')
            content = request.json.get('content')
            author = request.json.get('author')
            category_id = request.json.get('category_id')

            if not Category.query.filter_by(id=category_id).first():
                return jsonify({'message': 'Invalid category_id'})
            
            new_post = Post(title=title, content=content, author=author, category_id=category_id)
            db.session.add(new_post)
            db.session.commit()

            return jsonify({'message': 'Post created successfully'})
        else:
            return jsonify({'message': 'Invalid or expired token'})
    else:
        return jsonify({'message': 'Missing token'})

def get_all_posts():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        if payload:
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=10, type=int)

            posts = Post.query.paginate(page=page, per_page=per_page, error_out=False)
            post_list = []

            for post in posts.items:
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'author': post.author,
                    'category_id': post.category_id,
                    'comments': [{'id': comment.id, 'content': comment.content, 'author': comment.author, 'created_at': comment.created_at} for comment in post.comments]
                }
                post_list.append(post_data)

            return jsonify({
                'posts': post_list,
                'total_pages': posts.pages,
                'current_page': posts.page,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            })
        else:
            return jsonify({'message': 'Invalid or expired token'})
    else:
        return jsonify({'message': 'Missing token'})
   
def get_post(post_id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        if payload:
            post = Post.query.get(post_id)
            if post:
                post_data = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'author': post.author,
                    'category_id' : post.category_id,
                    'comments': []
                }
                
                for comment in post.comments:
                    comment_data = {
                        'id': comment.id,
                        'content': comment.content,
                        'author': comment.author,
                        'created_at': comment.created_at
                    }
                    post_data['comments'].append(comment_data)

                return jsonify(post_data)
            else:
                return jsonify({'message': 'Post not found'})

def update_post(post_id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        if payload:
            post = Post.query.get(post_id)
            if post:
                if request.method == 'PUT':
                    title = request.json.get('title')
                    content = request.json.get('content')
                    author = request.json.get('author')
                    category_id = request.json.get('category_id')

                    post.title = title
                    post.content = content
                    post.author = author
                    post.category_id = category_id

                    db.session.commit()

                    return jsonify({'message': 'Post updated successfully'})
                else:
                    return jsonify({'message': 'Invalid request method'})
            else:
                return jsonify({'message': 'Post not found'})
        else:
            return jsonify({'message': 'Invalid or expired token'})
    else:
        return jsonify({'message': 'Missing token'})


def delete_post(post_id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        if payload:
            post = Post.query.get(post_id)

            if post:
                if request.method == 'DELETE':
                    db.session.delete(post)
                    db.session.commit()

                    return jsonify({'message': 'Post deleted successfully'})
                else:
                    return jsonify({'message': 'Invalid request method'})
            else:
                return jsonify({'message': 'Post not found'})
        else:
            return jsonify({'message': 'Invalid or expired token'})
    else:
        return jsonify({'message': 'Missing token'})
    
def add_comment(post_id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        if payload and 'user_id' in payload:
            user_id = payload['user_id']
            user = User.query.get(user_id)

            if user:
                post = Post.query.get(post_id)
                if post:
                    content = request.json.get('content')
                    new_comment = Comment(content=content, author=user.username, post_id=post_id)
                    db.session.add(new_comment)
                    db.session.commit()
                    return jsonify({'message': 'Comment added successfully'})
                else:
                    return jsonify({'message': 'Post not found'}), 404
            else:
                return jsonify({'message': 'User not found'}), 404
        else:
            return jsonify({'message': 'Invalid or expired token'}), 401
    else:
        return jsonify({'message': 'Missing token'}), 401
    
def update_comment(post_id, comment_id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        if payload and 'user_id' in payload:
            user_id = payload['user_id']
            user = User.query.get(user_id)
            if user:
                post = Post.query.get(post_id)
                if post:
                    comment = Comment.query.get(comment_id)
                    if comment:
                        if comment.post_id == post.id:
                            if user.username == comment.author:
                                content = request.json.get('content')
                                comment.content = content
                                db.session.commit()
                                return jsonify({'message': 'Comment updated successfully'})
                            else:
                                return jsonify({'message': 'You are not the author of this comment'}), 403
                        else:
                            return jsonify({'message': 'Comment does not belong to this post'}), 400
                    else:
                        return jsonify({'message': 'Comment not found'}), 404
                else:
                    return jsonify({'message': 'Post not found'}), 404
            else:
                return jsonify({'message': 'User not found'}), 404
        else:
            return jsonify({'message': 'Invalid or expired token'}), 401
    else:
        return jsonify({'message': 'Missing token'}), 401

def create_category():
    if request.method == 'POST':
        name = request.json.get('name')
        description = request.json.get('description')
        new_category = Category(name=name, description=description)
        db.session.add(new_category)
        db.session.commit()

        return jsonify({'message': 'Category created successfully'})


def get_all_category():
    categories = Category.query.all()
    category_list = []

    for category in categories:
        category_data = {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'created_at': category.created_at
        }
        category_list.append(category_data)

    return jsonify({'categories': category_list})


def get_category(category_id):
    category = Category.query.get(category_id)

    if category:
        category_data = {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'created_at': category.created_at
        }
        return jsonify(category_data)
    else:
        return jsonify({'message': 'Category not found'})
    
def update_category(category_id):
    category = Category.query.get(category_id)

    if category:
        if request.method == 'PUT':
            name = request.json.get('name')
            description = request.json.get('description')

            category.name = name
            category.description = description

            db.session.commit()

            return jsonify({'message': 'Category updated successfully'})
    else:
        return jsonify({'message': 'Category not found'})
    
def delete_category(category_id):

    category = Category.query.get(category_id)

    if not category:
        return jsonify({'message': 'Category not found'}), 404

    try:

        uncategorized_category = Category.query.filter_by(name='uncategorized').first()

        if not uncategorized_category:

            uncategorized_category = Category(name='uncategorized')
            db.session.add(uncategorized_category)
            db.session.commit()


        posts_to_update = Post.query.filter_by(category_id=category_id).all()

        for post in posts_to_update:

            post.category_id = uncategorized_category.id

        db.session.delete(category)

        db.session.commit()

        return jsonify({'message': 'Category deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete category', 'error': str(e)}), 500
    
def user_profile(user_id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        if payload and 'user_id' in payload:
            if int(payload['user_id']) == user_id:
                user = User.query.get(user_id)
                if user:
                    return jsonify({
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'bio': user.bio,
                        'profile_picture': user.profile_picture
                    })
                else:
                    return jsonify({'message': 'User not found'}), 404
            else:
                return jsonify({'message': 'You are not authorized to view this profile'}), 403
        else:
            return jsonify({'message': 'Invalid or expired token'}), 401
    else:
        return jsonify({'message': 'Missing token'}), 401
    
def update_user_profile(user_id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        if payload and 'user_id' in payload:
            if int(payload['user_id']) == user_id:
                user = User.query.get(user_id)
                if user:
                    data = request.json
                    user.first_name = data.get('first_name', user.first_name)
                    user.last_name = data.get('last_name', user.last_name)
                    user.bio = data.get('bio', user.bio)
                    user.profile_picture = data.get('profile_picture', user.profile_picture)

                    db.session.commit()

                    return jsonify({'message': 'Profile updated successfully'})
                else:
                    return jsonify({'message': 'User not found'}), 404
            else:
                return jsonify({'message': 'You are not authorized to view this profile'}), 403
        else:
            return jsonify({'message': 'Invalid or expired token'}), 401
    else:
        return jsonify({'message': 'Missing token'}), 401       

def search_posts():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        if payload:
            keyword = request.args.get('q')

            if keyword:
                search_results = Post.query.filter(or_(Post.title.ilike(f'%{keyword}%'), Post.content.ilike(f'%{keyword}%'))).all()
                if search_results:
                    post_list = []
                    for post in search_results:
                        post_data={
                            'id' : post.id ,
                            'title' : post.title,
                            'content' : post.content,
                            'author' : post.author,
                            'category_id' : post.category_id
                        }
                        post_list.append(post_data)
                    return jsonify({'results': post_list})
                else:
                    return jsonify({'message': 'No matching posts found'})
            else:
                return jsonify({'message': 'Missing keyword'}), 400
        else:
            return jsonify({'message': 'Invalid or expired token'}), 401
    else:
        return jsonify({'message': 'Missing token'}), 401