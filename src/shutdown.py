import asyncio
import asyncssh
import logging
import sys
import json

from copy import deepcopy

class Shutdown:
    def __init__(self):
        self.__tasks = []
        self.__log = logging.getLogger(self.__class__.__name__)

    def start(self):
        config = json.load(open("./config.json"))

        self.__log.info("Running shutdown script")

        for host in config["hosts"]:
            host_config = deepcopy(config["_default"]["hosts"])
            host_config.update(host)

            self.__tasks.append(asyncio.ensure_future(self.__execute_script(host_config)))

    async def __execute_script(self, host):
        try:
            conn_params = {
                "host": host["ip_address"], 
                "username" : host["user"], 
                "password" : host["password"],
                "known_hosts" : None
            }

            with (await asyncssh.connect(**conn_params)) as conn:
                for script in host["shutdown"]:

                    if script["root"]:
                        script["script"] = "sudo -S -p '' {}".format(script["script"])
                    
                    output = []
                    
                    with (await conn.create_process(script["script"])) as process:
                        process.stdin.write(host["password"] + '\n')
                        
                        output.append(await process.stderr.read())
                        output.append(await process.stdout.read())

                    self.__log.info("\n".join(output))

        except asyncssh.misc.DisconnectError:
            self.__log.info("Host {} disconnect".format(host)) 
        except asyncio.CancelledError:
            self.__log.info("Task cancel for host {}".format(host))
        except:
            self.__log.info(sys.exc_info())

    def shutdown(self):
        for task in self.__tasks:
            task.cancel()

if __name__ == "__main__":
    log_format = "%(asctime)s %(levelname)-8s %(processName)-10s %(name)-10s %(message)s"
    logging.basicConfig(format=log_format, level=logging.DEBUG)

    loop = asyncio.get_event_loop()

    sh = Shutdown()
    try:
        sh.start()
        loop.run_forever()
    except:
        pass

    sh.shutdown()

    loop.close()


    

    
