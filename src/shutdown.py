import asyncio
import asyncssh
import logger
import sys
import json

class Shutdown:
    def __init__(self):
        self.__tasks = []
        self.__log = logger.getLogger(self.__class__.__name__)

        config = json.load(open("./config.json"))

        for host in config["hosts"]:
            self.__tasks.append(asyncio.ensure_future(self.__execute_script(host, config["shutdown"])))

    async def __execute_script(self, host, scripts):
        try:
            async with asyncssh.connect(host["ip_address"], username=host["user"], password=host["password"]) as conn:
                for script in scripts:
                    if script["root"]:
                        script["script"] = "sudo -S -p '' {}".format(script["script"])
                        async with conn.create_process(script["script"]) as process:
                            process.stdin.write(host["password"] + '\n')
                            result = await process.stdout.readline()
                    else:
                        result = await conn.run(script["script"], check=True)
                    self.__log.info(result)

        except asyncio.CancelledError:
            self.__log.info("Task cancel for host {}".format(host))
        except:
            self.__log.info(sys.exc_info()[0])

if __name__ == "__main__":
    sh = Shutdown()
    

    
