from pathlib import Path
from .file import File
from .filters import age_filter
from .helpers import assert_type
import os
import time
import yaml

from dateutil.relativedelta import relativedelta

from . import config

class Rule:
    def __init__(self, conf):
        self.config(conf)

    def from_yaml(path):
        conf = config.from_file(path, 'yaml')
        return Rule(conf)
    
    def config(self, conf):
        self.folders = conf.get('folders')
        self.interval = conf.get('interval', 60)
        self.actions = conf.get('actions')
        self.filter = conf.get('filter')
    
    def action(self, file):
        """ Here is the code that defines what to do with the file."""
        for action in self.actions:
            action(file)
    
    def run(self):
        while True:
            for folder in self.folders:
                for item in folder.iterdir():
                    if item.is_file():
                        file = File.from_pathlib(item)
                        if self.filter(file):
                            self.action(file)
            time.sleep(self.interval*60)