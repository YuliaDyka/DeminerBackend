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

#-------------------------- GET BY ID --------------------------------
@sessions_bp.post('/getById')
def getById() -> Response:
    data = request.get_json()
    id = data['id']
    findSession: Session = Session.query.filter_by(id=id).first()
    print(id)
    print(findSession)


    if findSession:
        return findSession.put_into_dto(), 201
    else:
        return jsonify({'error': 'Could not found item'}), 500

#-------------------------- CREATE --------------------------------
@sessions_bp.post('/create')
def registration() -> Response:
    content = request.get_json()

    dateNow = datetime.now()
    newSession = Session(
        date=dateNow
    )
    commands = content['commands']
    print(commands)
    for cmd in commands:
        command = Commands(
        index=cmd['index'],
        speed=cmd['speed'],
        angle=cmd['angle'],
        duration=cmd.get('duration'),
        distance=cmd.get('distance')
        )
        newSession.commands.append(command)

    session_controller.create(newSession)
    if newSession:
        return newSession.put_into_dto(), 201
    else:
        return jsonify({'error': 'Could not create item'}), 500

#-------------------------- UPDATE --------------------------------
@sessions_bp.put('/<int:id>')
def update_session(id: int) -> Response:
    content = request.get_json()

    print(content)
    session = content['session']
    session_controller.update(id, session)
    return make_response("Session updated", HTTPStatus.OK)

#-------------------------- DELETE --------------------------------
@sessions_bp.delete('/<int:id>')
def delete_session(id: int) -> Response:
    session_controller.delete(id)
    return make_response("Session deleted", HTTPStatus.OK)