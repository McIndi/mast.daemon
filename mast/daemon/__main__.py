import sys
import platform
import win32serviceutil
from mastd_daemon import MASTd


if "Windows" in platform.system():
    def main():
        win32serviceutil.HandleCommandLine(MASTd)
        sys.exit(0)
        
elif "Linux" in platform.system():
    def main():
        mastd = MASTd("/var/run/mast/mastd.pid")
    
        if len(sys.argv) != 2:
            print "USAGE: python -m mastd.daemon { start | stop | restart | status }"
            sys.exit(1)
    
        if "start" in sys.argv[1]:
            mastd.start()
        elif "stop" in sys.argv[1]:
            mastd.stop()
        elif "restart" in sys.argv[1]:
            mastd.restart()
        elif "status" in sys.argv[1]:
            print mastd.status()
        else:
            print "USAGE: python -m mast.daemon { start | stop | restart | status }"
            sys.exit(1)
    
        sys.exit(0)

if __name__ == "__main__":
    main()
