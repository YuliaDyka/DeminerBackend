from flask import Blueprint, Response, jsonify, make_response, request

from http import HTTPStatus

from deminer.controller import user_controller
from deminer.model import User
# from project.schemas.user_schema import RegistrationSchema, UserResponseSchema, UserPatchSchema, LoginSchema



user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.get('')
def get_all_users() -> Response:
    """
    Gets all objects from table
    :return: Response object
    """
    return make_response(jsonify(user_controller.find_all()), HTTPStatus.OK)


@user_bp.post('/login')
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user: User = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        return make_response("Login successful", HTTPStatus.OK)
    else:
        return make_response("Invalid credentials", HTTPStatus.UNAUTHORIZED)


#-------------------------- REGISTER --------------------------------
@user_bp.post('/register')
def registration() -> Response:
    content = request.get_json()
    
    if User.query.filter_by(name=content['name']).first():
        return make_response('User with this name already exists', HTTPStatus.CONFLICT)
    if User.query.filter_by(email=content['email']).first():
        return make_response('User with this email already exists', HTTPStatus.CONFLICT)
    
    user = User(**content)
    user_controller.create(user)
    return make_response("Successfull registration", HTTPStatus.CREATED)


#-------------------------- UPDATE --------------------------------
@user_bp.put('/<int:id>')
def update_user(id: int) -> Response:
    content = request.get_json()
    user = User(**content)
    user_controller.update(id, user)
    return make_response("User updated", HTTPStatus.OK)


#-------------------------- PATCH --------------------------------
@user_bp.patch('/<int:id>')
def patch_user(id: int) -> Response:
    content = request.get_json()
    user_controller.patch(id, content)
    return make_response("User updated", HTTPStatus.OK)


#-------------------------- DELETE --------------------------------
@user_bp.delete('/<int:id>')
def delete_user(id: int) -> Response:
    user_controller.delete(id)
    return make_response("User deleted", HTTPStatus.OK)