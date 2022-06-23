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
    parents: bool = False
    
    def __call__(self, file):
        name = file.path.name
        old_pat = re.compile(self.old_pat)
        name = old_pat.sub(self.new_pat, name)
        old_path = file.path
        # Techincally, we can combine the moving and renaming in this step. If the new name is an absolute path, then we'll move it absolutely. Else, we add the path to the parent directory.
        new_path = Path(name)
        if not new_path.is_absolute():
                new_path = file.path.parent / new_path
        fn = (lambda x: copy_file(file.path, x)) if self.copy else file.path.replace
        if not self.overwrite and new_path.exists():
                error(f'A file already exists at "{new_path}". Skipping renaming of "{old_path}".')
                return
        # Create parent directory if allowed to
        if self.parents:
            new_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            file.path = fn(new_path)
        except Exception as e:
            error(f"An error occured while renaming file `{old_path}`: {e}")
        else:
            verb = "Copied" if self.copy else "Renamed"
            info(f"{verb} file: {old_path} -> {new_path}.")

@dataclass
class move(Action):
    destination: Path
    copy: bool = False
    overwrite: bool = False
    parents: bool = False

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
        # Create parent directory if allowed to
        if self.parents:
            destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            file.path = fn(destination)
        except Exception as e:
            error(f"An error occured while moving file `{old_path}`: {e}")
        else:
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
