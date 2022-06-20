from dataclasses import dataclass
from pathlib import Path
import re
import shutil

from .file import File

def info(s):
    '''When I implement logging, this will write to the log itself. For now, it prints to console.'''
    print(f'INFO : {s}')

def error(s):
    '''When I implement logging, this will write to the log itself. For now, it prints to console.'''
    print(f'ERROR: {s}')

def copy_file(file, destination):
    shutil.copy(file, destination)

class Action:
    pass

@dataclass
class rename(Action):
    old_pat: str
    new_pat: str
    copy: bool = False
    overwrite: bool = False
    
    def __call__(self, file):
        name = file.path.name
        old_pat = re.compile(self.old_pat)
        name = old_pat.sub(self.new_pat, name)
        old_path = file.path
        new_path = file.path.parent / Path(name)
        fn = (lambda x: copy_file(file.path, x)) if self.copy else file.path.replace
        if not self.overwrite and new_path.exists():
                error(f'A file already exists at "{new_path}". Skipping renaming of "{old_path}".')
                return
        file.path = fn(new_path)
        verb = "Copied" if self.copy else "Renamed"
        info(f"{verb} file: {old_path} -> {new_path}.")

@dataclass
class move(Action):
    destination: Path
    copy: bool = False
    overwrite: bool = False

    def __call__(self, file):
        destination = Path(self.destination)
        if not destination.is_absolute():
            destination = file.path.parent / destination
        assert destination.is_dir()
        destination /= file.path.name
        old_path = file.path
        fn = (lambda x: copy_file(file.path, x)) if self.copy else file.path.replace
        if not self.overwrite and destination.exists():
                error(f'A file already exists at "{destination}". Skipping relocation of "{file.path.name}".')
                return
        file.path = fn(destination)
        verb = "Copied" if self.copy else "Moved"
        info(f"{verb} file: {old_path} -> {destination}.")

class delete:
    def __call__(self, file):
        file.path.unlink()
        info(f'Deleted file "{file.path}".')

@dataclass
class command(Action):
    command_str: str

    def __call__(self, file):
        values = {
            'file': str(file.path.resolve())
        }
        for key, item in vars(file).items():
            values['file.'+key] = str(item)
        
        # Make sure the command doesn't contain any attributes that are undefined
        pat = re.compile(r'\$\{(file[^\}]*)\}')
        keys = set(pat.findall(self.command_str))
        if set(keys) - values.keys():
            raise AttributeError(f'Unknown attribute(s) {set(keys) - values.keys()}')

        # Make the command replacement
        command = self.command_str
        for key, item in values.items():
            sub = re.compile(r'\$\{\s*' + key.replace('.', r'\.') + r'\s*\}')
            command = sub.sub(item, command)
        print(command)
