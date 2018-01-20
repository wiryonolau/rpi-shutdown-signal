import asyncio
import logging
import sys

from gpiozero import Button

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
        except:
            self.__log.info(sys.exc_info())
            raise

    async def __watch_state(self):
        new_state = self.__btn.value

        if self.__current_state != new_state:
            self.__log.info("State change {} > {}".format(self.__current_state, new_state))

            if self.__current_state is True and new_state is False:
                await self.__prepare_for_shutdown()
            elif self.__current_state is False and new_state is True:
                await self.__prepare_to_start()

            self.__current_state = new_state

    async def __prepare_for_shutdown(self, timeout=10):
        while self.__stop is False:
            self.__log.info("Shutdown countdown {}".format(timeout))
            await asyncio.sleep(1)

            if self.__btn.value is True:
                self.__log.info("Cancel shutdown")
                break

            if timeout == 0:
                self.__log.info("Shutting down")
                break
            timeout -= 1

    async def __prepare_to_start(self):
        self.__log.info("Turn on")

    def start(self):
        self.__tasks = [
            asyncio.ensure_future(self.__state_monitor())
        ]

    def shutdown(self):
        self.__stop = True
        self.__btn.close()
