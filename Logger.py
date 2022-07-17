#!/usr/bin/python
# -*- coding: utf-8 -*

import logging
import time
import colorlog

log_colors_config = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red',
}

formatter = colorlog.ColoredFormatter(
    '%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]- %(message)s', log_colors=log_colors_config)  # 日志输出格式


global_fh = logging.FileHandler(time.strftime(
    "logs/%Y_%m_%d_%H_%M_%S.log", time.localtime()), mode='w', encoding='utf-8')
global_fh.setLevel(logging.DEBUG)
global_fh.setFormatter(formatter)



class Logger:
    INFO=logging.INFO
    WARNING=logging.WARNING
    ERROR=logging.ERROR
    DEBUG=logging.DEBUG
    
    def __init__(self, module_name, log_level=logging.INFO):
        self.logger = logging.getLogger(module_name)
        self.sh = colorlog.StreamHandler()
        self.sh.setFormatter(formatter)
        self.sh.setLevel(log_level)

        self.logger.addHandler(self.sh)
        self.logger.addHandler(global_fh)
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(module_name+" logger initialized")
        self.logger.propagate = False

    def warning(self, text):
        self.logger.warning(text)

    def info(self, text):
        self.logger.info(text)

    def error(self, text):
        self.logger.error(text)

    def debug(self, text):
        self.logger.debug(text)


if __name__ == "__main__":
    class demo_logger(Logger):
        def __init__(self):
            Logger.__init__(self, "demo", Logger.INFO)

        def demo(self):
            self.warning("warning test %d" % (1))
            self.debug("debug test %d" % (1))
    demo = demo_logger()
    demo.demo()
