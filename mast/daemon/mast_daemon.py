import os
from mast.logging import logger, logged
from time import sleep
import pkg_resources
import platform


mast_home = os.environ["MAST_HOME"]


if "Windows" in platform.system():
    import win32serviceutil
    import servicemanager
    import win32service
    import win32event
    import socket

    class MASTd(win32serviceutil.ServiceFramework):
        _svc_name_ = "mastd"
        _svc_display_name_ = "mastd"

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self,args)
            self.stop_event = win32event.CreateEvent(None,0,0,None)
            socket.setdefaulttimeout(60)
            self.stop_requested = False
    
        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.stop_event)
            self.stop_requested = True

        def SvcDoRun(self):
            self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_,'')
            )
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.run()

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
                while not self.stop_requested:
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

elif "Linux" in platform.system():
    from daemon import Daemon
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

