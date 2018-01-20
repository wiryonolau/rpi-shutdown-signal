import logging
import asyncio
import argparse
import sys

from watchdog import WatchDog

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", default=False)

    args = parser.parse_args()

    log_format = "%(asctime)s %(levelname)-8s %(processName)-10s %(name)-10s %(message)s"
    if args.verbose:
        logging.basicConfig(format=log_format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=log_format, level=logging.INFO)

    log = logging.getLogger()

    loop = asyncio.get_event_loop()

    server = WatchDog()

    try:
        log.info("Start all service")
        server.start()
        loop.run_forever()
    except:
        log.info(sys.exc_info())

    loop.run_until_complete(asyncio.wait([shutdown(server)]))

    loop.close()

    if loop.is_closed():
        loop.stop()

async def shutdown(srv):
    if asyncio.iscoroutinefunction(getattr(srv, "shutdown")):
        await srv.shutdown()
    else:
        srv.shutdown()

    asyncio.sleep(1)

    for task in srv.get_task():
        task.cancel()

if __name__ == "__main__":
    main()

