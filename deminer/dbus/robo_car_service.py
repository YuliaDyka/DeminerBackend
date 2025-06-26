from pydbus import SessionBus
from gi.repository import GLib # type: ignore
from typing import Protocol
import threading
from deminer.dbus.custom_timer import Timer

class DBusSignalEmitter(Protocol):
    def _emit(self, name: str, *args): ...

class RoboCarService(DBusSignalEmitter):
    """
    <node>
        <interface name='com.yulia.RoboCarService'>
            <method name='updateMoveStatus'>
                <arg type='s' name='msg' direction='in'/>
                <arg type='b' name='reply' direction='out'/>
            </method>
        </interface>
    </node>
    """
    SERVICE_PATH = "com.yulia.RoboCarService"
    
    def _emit(self, name: str, *args) -> None: ...  # noqa: D401, pass
    
    def updateMoveStatus(self, msg):
        print(f"[D-BUS] Update move status called: {msg}")
        return True

class RoboCar:
    SERVICE_PATH = "com.yulia.RoboCarSocketService"
    SERVICE_OBJECT = "/com/yulia/RoboCarSocketService"
    
    EXECUTE_COMMAND = "ExecuteCommand"
    STOP_COMMAND = "StopCurrentCommand"
    SET_CAMERA_POS = "UpdateCameraPosition"
    
    SIGNAL_CONNECTION_STATUS = "ConnectionStatusChanged"
    SIGNAL_BUSY_STATUS = "BusyStatusChanged"
    
    loop = GLib.MainLoop()
    bus = SessionBus()
    
    def __init__(self) -> None:
        self.isDbusStarted = False    
        self.isConnected = False
        self.isBusy = False
        
        self.isCameraMove = False
        self.cameraMoveDir = "none"
        self.lastCameraPositionH = 0.0
        self.lastCameraPositionV = 0.0
        self.cameraPositionH = 0.0
        self.cameraPositionV = 0.0
        self.cameraPositionDelta = 2
        
        self.cameraMoveTimer = Timer(100, self.onCameraMoveTriggered)            
    
    def startDBus(self, connectionStatusChangedClb):
        self.connectionStatusChangedClb = connectionStatusChangedClb
        threading.Thread(target=self.startService, daemon=True).start()
        threading.Thread(target=self.subscribeSocketSignalls, daemon=True).start()
        self.isDbusStarted = True
        self.cameraMoveTimer.start()
    
    def runCommand(self, speed, turn, duration, onFinishClb):
        if self.isBusy:
            print("[D-BUS][RUN_CMD] Error to run cmd! RoboCar is busy!")
            return False
        self.socketService = self.bus.get(self.SERVICE_PATH)
        runCmd = getattr(self.socketService, self.EXECUTE_COMMAND)
        result = runCmd(speed, turn, duration)
        if result:
            print("[D-BUS][RUN_CMD] Command ran successfully!")
            self.isBusy = True
            self.onCmdFinished = onFinishClb
        else:
            print("[D-BUS][RUN_CMD] Error to run cmd!")
        return result
    
    def stopCurrentCommand(self):
        self.socketService = self.bus.get(self.SERVICE_PATH)
        stopCmd = getattr(self.socketService, self.STOP_COMMAND)
        result = stopCmd()
        if result:
            print("[D-BUS][STOP_CMD] Current command stopped successfully!")
            self.isBusy = False
        else:
            print("[D-BUS][RUN_CMD] Error to stop current command!")
        return result
    
    def cameraMove(self, action, dir):
        if action == "pressed":
            self.isCameraMove = True
            self.cameraMoveDir = dir
        elif action == "released":
            self.isCameraMove = False
            self.cameraMoveDir = "none"
        elif action == "reset":
            self.isCameraMove = False
            self.cameraPositionH = 0
            self.cameraPositionV = 0
            self.updateCameraPosition()
        else:
            print("[D-BUS][CAMERA_MOVE] Wrong action!")
    
    def onCameraMoveTriggered(self):
        if not self.isCameraMove:
            return
        
        match self.cameraMoveDir:
            case "left":
                if self.cameraPositionH < 89:
                    self.lastCameraPositionH = self.cameraPositionH
                    self.cameraPositionH += self.cameraPositionDelta
            case "right":
                if self.cameraPositionH > -89:
                    self.lastCameraPositionH = self.cameraPositionH
                    self.cameraPositionH -= self.cameraPositionDelta
            case "up":
                if self.cameraPositionV < 89:
                    self.lastCameraPositionV = self.cameraPositionV
                    self.cameraPositionV += self.cameraPositionDelta
            case "down":
                if self.cameraPositionV > -89:
                    self.lastCameraPositionV = self.cameraPositionV
                    self.cameraPositionV -= self.cameraPositionDelta
            case _:
                return
            
        self.updateCameraPosition()
    
    def updateCameraPosition(self):
        self.socketService = self.bus.get(self.SERVICE_PATH)
        runCmd = getattr(self.socketService, self.SET_CAMERA_POS)
        result = runCmd(self.cameraPositionH, self.cameraPositionV)
        if result:
            print("[D-BUS][SET_CAMERA_POS] Camera position successfully updated!")
        else:
            print("[D-BUS][SET_CAMERA_POS] Error to update camera position!")
            self.cameraPositionH = self.lastCameraPositionH
            self.cameraPositionV = self.lastCameraPositionV
        return result
    
    def startService(self):
        self.bus.publish(RoboCarService.SERVICE_PATH, RoboCarService())
        self.loop.run()
    
    def onConnectionStatusChanged(self, isConnected):
        print(f"[D-BUS][CONN_STATUS_CHANGED] Connection status changed: {isConnected}")
        if isConnected != self.isConnected and hasattr(self, 'connectionStatusChangedClb'):
            self.connectionStatusChangedClb(isConnected)
        self.isConnected = isConnected
        
    def onCommandBusyChanged(self, isBusy):
        print(f"[D-BUS][CMD_STATUS_CHANGED] Command busy status changed: {isBusy}")
        if self.isBusy and not isBusy and hasattr(self, 'onCmdFinished'):
            self.isBusy = False
            self.onCmdFinished()             
        self.isBusy = isBusy
    
    def subscribeSocketSignalls(self):
        try:
            self.socketService = self.bus.get(self.SERVICE_PATH)
            self.bus.con.signal_subscribe(
                sender=self.SERVICE_PATH,
                interface_name=self.SERVICE_PATH,
                member=self.SIGNAL_CONNECTION_STATUS,
                object_path=self.SERVICE_OBJECT,
                arg0=None,
                flags=0,
                callback=lambda *a: self.onConnectionStatusChanged(*a[-1])
            )
            self.bus.con.signal_subscribe(
                sender=self.SERVICE_PATH,
                interface_name=self.SERVICE_PATH,
                member=self.SIGNAL_BUSY_STATUS,
                object_path=self.SERVICE_OBJECT,
                arg0=None,
                flags=0,
                callback=lambda *a: self.onCommandBusyChanged(*a[-1])
            )
            print(f"[D-BUS] Successfully subscribed to Socket signalls!")
        except Exception as e:
            print(f"[D-BUS] Error subscribe to Socket signalls: {e}")
            