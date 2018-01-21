import asyncio
import logging
import sys
import time

from gpiozero import Button
from shutdown import Shutdown

class WatchDog:
    def __init__(self):
        self.__loop = asyncio.get_event_loop()
        self.__log = logging.getLogger(self.__class__.__name__)
        self.__stop = False
        self.__tasks = []
    
    def get_task(self):
        return self.__tasks

    async def __state_monitor(self):
        self.__log.info("Start Monitor state")
        try:
            self.__btn = Button(4)
            self.__current_state = self.__btn.value
            while self.__stop is False:
                await self.__watch_state()
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            self.__log.info("Cancelled")
        except:
            self.__log.info(sys.exc_info()[0])
        finally:
            self.__btn.close()

    async def __watch_state(self):
        new_state = self.__btn.value

        if self.__current_state != new_state:
            self.__log.info("State change {} > {}".format(self.__current_state, new_state))

            if self.__current_state is True and new_state is False:
                self.__tasks["shutdown"] = asyncio.ensure_future(self.__prepare_for_shutdown())
            elif self.__current_state is False and new_state is True:
                if "shutdown" in self.__tasks:
                    self.__tasks["shutdown"].cancel()
                self.__tasks["start"] = asyncio.ensure_future(self.__prepare_to_start())

            self.__current_state = new_state

    async def __prepare_for_shutdown(self, timeout=10):
        try:
            while self.__stop is False:
                self.__log.info("Shutdown countdown {}".format(timeout))
                await asyncio.sleep(1)

                if timeout == 0:
                    self.__log.info("Shutting down")
                    sh = Shutdown()
                    sh.start()
                    break
                timeout -= 1
        except asyncio.CancelledError:
            self.__log.info("Shutdown Cancelled")

    async def __prepare_to_start(self):
        self.__log.info("Turn on")

    def start(self):
        self.__tasks = {
            "state_monitor" : asyncio.ensure_future(self.__state_monitor())
        }

    def shutdown(self):
        self.__stop = True
        
        for key, task in self.__tasks.items():
            task.cancel()
    
        time.sleep(1)

