import datetime
from datetime import datetime 
from flask import Blueprint, Response, jsonify, make_response, request

from http import HTTPStatus

from deminer.controller import session_controller
from deminer.model.commands import Commands
from deminer.model.session import Session
from deminer.dbus.robo_car_service import RoboCar


roboCar = RoboCar()

class ActiveSession:
    isConnected = False
    isActive = False
    sessionID = 0
    cmdPosition = 0
    commands: list = []
    
    @staticmethod
    def onConnectionStatusChanged(isConnected: bool):
        if not isConnected and sA.isConnected:
            sA.isActive = False
        sA.isConnected = isConnected
    
    @staticmethod
    def onCmdFinished():
        if sA.isLastCmd():
            sA.stop()
        else:
            sA.cmdPosition += 1
            sA.runNextCmd()
    
    @staticmethod
    def runNextCmd():
        if sA.isActive:
            cmd = sA.commands[sA.cmdPosition]
            roboCar.runCommand(cmd['speed'], cmd['angle'], cmd['duration'], sA.onCmdFinished) 
    
    @staticmethod
    def stop():
        sA.isActive = False
        roboCar.stopCurrentCommand()
        
    @staticmethod
    def reset():
        sA.cmdPosition = 0
        sA.commands = []
        
    @staticmethod
    def activeCmd():
        return sA.commands[sA.cmdPosition]

    @staticmethod
    def size():
        return len(sA.commands)
    
    @staticmethod
    def activeCmdIndex() -> int:
        return sA.commands[sA.cmdPosition]['index']
    
    @staticmethod
    def isLastCmd() -> bool:
        return sA.cmdPosition == sA.size() - 1
    
    @staticmethod
    def print():
        print(f"====== Active session ID: {sA.sessionID} =======")
        for i in range(sA.size() - 1):
            cmd = sA.commands[i]    
            print(f"--> #{i}\tIndex: {cmd['index']}\tSpeed: {cmd['speed']}\tAngle: {cmd['angle']}\tDuration: {cmd['duration']}")
    
    

sA = ActiveSession
roboCar.startDBus(sA.onConnectionStatusChanged)

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
    commands = content['commands']
    nameSession = content['nameSession']
    
    newSession = Session(
        date=dateNow,
        name=nameSession
    )
   
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
    session = content['session']
    session_controller.update(id, session)
    return make_response("Session updated", HTTPStatus.OK)

#-------------------------- DELETE --------------------------------
@sessions_bp.delete('/<int:id>')
def delete_session(id: int) -> Response:
    session_controller.delete(id)
    return make_response("Session deleted", HTTPStatus.OK)

#-------------------------- active-session-id --------------------------------
@sessions_bp.post('/active-session-id')
def activeSessionID() -> Response:
    sA.sessionID = request.get_json()['id']     
    sA.isActive = sA.sessionID != 0
    
    if sA.isActive:
        sA.reset()
        session = session_controller.find_by_id(sA.sessionID)
        sA.commands = session['commands'] # type: ignore
        sA.runNextCmd()
    else:
        sA.stop()   

    return make_response("Successful send", HTTPStatus.OK)

#-------------------------- check-connection --------------------------------
@sessions_bp.post('/check-connection')
def checkConnection() -> Response:
    result = roboCar.isConnected #sA.isConnected
    return jsonify({'connection': result})
 
#-------------------------- get-active-cmd --------------------------------    
@sessions_bp.post('/get-active-cmd')
def getActiveCmd() -> Response:        
    return jsonify({'index': sA.activeCmdIndex(), 'isSessionActive': sA.isActive})

#-------------------------- camera-position --------------------------------    
@sessions_bp.post('/camera-position')
def cameraPosition() -> Response:
    action = request.get_json()['action']
    dir = request.get_json()['dir']
    print(f"==> Camera move <== Action: {action}, Direction: {dir}")
    roboCar.cameraMove(action, dir)
    return make_response("Successful send", HTTPStatus.OK)