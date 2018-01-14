import time
from logging import getLogger
logger = getLogger(__name__)

class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self
    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start


import os, shutil
import random,time

class My_File_Lock:
    def __init__(self,file):
        self.file=file
        self.lockFile=file+".lck"
        self.islocked=False
        self.lockcount=0
        pass

    def __enter__(self, ):
        self.acquire()
        return self

    def __exit__(self ,type, value, traceback ):
        self.release()

    def checkLocked(self,file=None):
        if file==None:
            file=self.file
        lockFile=file+".lck"

        return os.path.exists(lockFile)

    def acquire(self, waitTime=0):
        if self.islocked :

            self.lockcount+=1
            logger.debug(f"{self.lockcount} existing lock on {self.file}")
            return
        #acquires a lock
        while os.path.exists(self.lockFile):
            time.sleep(random.random()+random.randint(0,5))
        self._create_lock_file()
    def release(self):
        self._remove_lock_file()

    def _remove_lock_file(self):
        if self.lockcount>1:
            self.lockcount-=1
            #logger.debug(f"acquiring lock on {self.file}")
            logger.debug(f"{self.lockcount} locks remain")
        else:
            try:
                os.remove(self.lockFile)
                logger.debug(f"lock removed {self.lockFile}")
            except FileNotFoundError:
                logger.debug(f"LOCK FILE NOT FOUND {self.lockFile}")
            self.islocked = False
            self.lockcount -= 1

    def _create_lock_file(self):
        logger.debug(f"creating lock {self.lockFile}")
        open(self.lockFile, 'a').close()
        self.islocked=True
        self.lockcount += 1


