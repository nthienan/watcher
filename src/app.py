import logging
import logging.handlers
import os
import time
import pyinotify
import functools
from subprocess import Popen, PIPE


def init_logger(cfg):
        logger = logging.getLogger()
        logger.setLevel(cfg.log_level)
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=cfg.log_file,
            maxBytes=1250000,
            backupCount=10)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def run_cmd(*agrs, **keywords):
    try:
        logging.info("detected changes, command is running...")
        logging.debug("cmd: %s" % keywords['cmd'])
        p = Popen(keywords['cmd'], stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        logging.debug("stdout: %s" % stdout)
        logging.debug("stderr: %s" % stderr)
        if stderr:
            raise RuntimeError('an unexpected error occurred: %s' % stderr)
    except Exception as err:
        logging.error("%s" % err)
    else:
        logging.info("command has been run successfully")


class Application:
    def __init__(self, opts, **cfg):
        self.cfg = opts
        self.is_running = False
        init_logger(self.cfg)
        self.wm = pyinotify.WatchManager()
        mask = pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_CLOSE_WRITE | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO
        self.wm.add_watch(self.cfg.watch_dir, mask, rec=True)


    def run(self):
        self.is_running = True
        logging.info("watcher is running...")
        try:
            handler = functools.partial(run_cmd, cmd=self.cfg.cmd)
            self.notifier = pyinotify.Notifier(self.wm)
            self.notifier.loop(callback=handler)
        except pyinotify.NotifierError as err:
            logging.error('%s' % err)

    def stop(self):
        self.is_running = False
        logging.info("watcher is stopping...")
        self.notifier.stop()
        logging.info("watcher stopped")
