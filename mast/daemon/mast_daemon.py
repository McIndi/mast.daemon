import os
from mast.logging import logger, logged
from time import sleep
import pkg_resources
from daemon import Daemon

mast_home = os.environ["MAST_HOME"]

class MASTd(Daemon):

    @logged("mast.daemon")
    def get_plugins(self):
        logger.debug("Attempting to retrieve list of plugins")
        self.named_objects = {}
        for ep in pkg_resources.iter_entry_points(group='mastd_plugin'):
            logger.debug("found plugin: {}".format(ep.name))
            try:
                self.named_objects.update({ep.name: ep.load()})
            except:
                logger.exception("An unhandled exception occurred during execution.")
                pass
        logger.info("Collected plugins {}".format(str(self.named_objects.keys())))

    @logged("mast.daemon")
    def run(self):
        os.chdir(mast_home)
        try:
            logger.info("Attempting to start mastd")
            if not hasattr(self, "named_objects"):
                logger.debug("Plugins not known, discovering...")
                self.get_plugins()
            threads = {}
            logger.debug("Entering main loop")
            while True:
                for key, value in self.named_objects.items():
                    logger.debug("{}".format(str(threads)))
                    if key in threads.keys():
                        if threads[key].isAlive():
                            logger.debug("Plugin {} loaded and running".format(key))
                            continue
                        else:
                            logger.debug("Plugin {} found, but dead, attempting to restart".format(key))
                            try:
                                threads[key] = value()
                                threads[key].start()
                                logger.debug("Plugin {} started".format(key))
                                continue
                            except:
                                logger.exception("An unhandled exception occurred during execution.")
                                continue
                    else:
                        logger.info("Plugin {} not found. Attempting to start.".format(key))
                        try:
                            threads[key] = value()
                            threads[key].start()
                            continue
                        except:
                            logger.exception("An unhandled exception occurred during execution.")
                            continue
                        logger.info("Plugin {} started".format(key))
                        continue
                logger.debug("mastd sleeping for 60 seconds.")
                sleep(60)
        except:
            logger.exception("An uhhandled exception occurred during execution")
            raise

    @logged("mast.daemon")
    def status(self):
        return "NOT IMPLEMENTED!"

