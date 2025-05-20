from flask import Blueprint, Response, jsonify, make_response, request

from http import HTTPStatus

from flask import Blueprint, Response, jsonify, make_response, request

from http import HTTPStatus

from deminer.controller import commands_controller
from deminer.model.commands import Commands




commands_bp = Blueprint('commands', __name__, url_prefix='/commands')

@commands_bp.get('')
def get_all_commands() -> Response:
    """
    Gets all objects from table
    :return: Response object
    """
    return make_response(jsonify(commands_controller.find_all()), HTTPStatus.OK)

#-------------------------- CREATE --------------------------------
@commands_bp.post('/create')
def registration() -> Response:
    content = request.get_json()
    
    commands = Commands(**content)
    commands_controller.create(commands)
    return make_response("Successfull created", HTTPStatus.CREATED)

#-------------------------- UPDATE --------------------------------
@commands_bp.put('/<int:id>')
def update_commands(id: int) -> Response:
    content = request.get_json()
    commands = Commands(**content)
    commands_controller.update(id, commands)
    return make_response("commands updated", HTTPStatus.OK)

#-------------------------- DELETE --------------------------------
@commands_bp.delete('/<int:id>')
def delete_commands(id: int) -> Response:
    commands_controller.delete(id)
    return make_response("commands deleted", HTTPStatus.OK)