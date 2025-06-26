import asyncio
import threading
import time

class Timer:
    def __init__(self, interval = 1000, clb = None) -> None:
        if interval > 0:
            self.interval = interval
        else:
            self.interval = 1000
        self.clb = clb
        
        self.isDebug = False
        self.isStopping = False
        self.isStarting = False
        self.isRunning = False
        self.isSingleShot = False
        self.counter = 0
        threading.Thread(target=self.threadLoop, daemon=True).start()
    
    def start(self, interval = -1):
        if interval > 0:
            self.interval = interval
        self.counter = 0
        self.isStopping = False 
        self.isStarting = True 
    
    def stop(self):
        self.isStopping = True         
    
    async def taskLoop(self):
        while self.isRunning and not self.isStopping:
            await asyncio.sleep(self.interval / 1000.0)
            if self.isStopping:
                break
            if self.clb is not None:               
                self.clb()
            elif self.isDebug:
                print(f"[TIMER][DBG] No callback! Interval is: {self.interval} ms, Counter: {self.counter}")
            self.counter = self.counter + 1
            if self.isSingleShot:
                self.isRunning = False
                
    async def startTask(self):
        self.isRunning = True
        self.task = asyncio.create_task(self.taskLoop())
        await self.task
        self.isStopping = False
        self.isRunning = False
    
    def threadLoop(self):
        while True:
            if self.isStarting:
                if not self.isRunning and not self.isStopping:
                     asyncio.run(self.startTask())
                     self.isStarting = False
            time.sleep(0.001)
                     
    
    def setDebug(self, isDebug: bool):
        self.isDebug = isDebug
               
    def getCounter(self):
        return self.counter
    
    def setCallback(self, clb):
        self.clb = clb
        
    def getInterval(self):
        return self.interval
    def setInterval(self, interval):
        self.interval = interval
        
    def getSingleShot(self):
        return self.isSingleShot   
    def setSingleShot(self, isSingleShot):
        self.isSingleShot = isSingleShot
        
    def getRunning(self):
        return self.isRunning
        
        