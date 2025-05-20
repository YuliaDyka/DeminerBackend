import datetime
from datetime import datetime 
from flask import Blueprint, Response, jsonify, make_response, request

from http import HTTPStatus

from deminer.controller import session_controller
from deminer.model.commands import Commands
from deminer.model.session import Session




sessions_bp = Blueprint('sessions', __name__, url_prefix='/sessions')

@sessions_bp.get('')
def get_all_sessions() -> Response:
    """
    Gets all objects from table
    :return: Response object
    """
    return make_response(jsonify(session_controller.find_all()), HTTPStatus.OK)

#-------------------------- CREATE --------------------------------
@sessions_bp.post('/create')
def registration() -> Response:
    content = request.get_json()


    d1 = datetime.now()
    session = Session(
        date=d1
    )
    commands = content['commands']
    for cmd in commands:
        command = Commands(
        index=cmd['index'],
        speed=cmd['speed'],
        angle=cmd['angle'],
        duration=cmd.get('duration'),
        distance=cmd.get('distance')
        )
        session.commands.append(command)

    session_controller.create(session)
    return make_response("Successfull created", HTTPStatus.CREATED)

#-------------------------- UPDATE --------------------------------
@sessions_bp.put('/<int:id>')
def update_session(id: int) -> Response:
    content = request.get_json()
    session = Session(**content)
    session_controller.update(id, session)
    return make_response("Session updated", HTTPStatus.OK)

#-------------------------- DELETE --------------------------------
@sessions_bp.delete('/<int:id>')
def delete_session(id: int) -> Response:
    session_controller.delete(id)
    return make_response("Session deleted", HTTPStatus.OK)