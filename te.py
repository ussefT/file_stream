import stat
import string
from datetime import datetime
from os import name
from pathlib import Path


def getDisk():
    """
    Get local disk
    """
    # Windows
    path = []
    if name == 'nt':
        for drive in string.ascii_uppercase:
            if Path(f"{drive}:/").exists():
                path.append(f"{drive}:/")

        return path
    # Linux
    else:
        return [Path('/')]


def getTimeFile(path: Path):
    """
    Get time D M Day_number h:m:s Y
    """
    __dateFile = Path(path).stat().st_mtime
    dateFile = datetime.fromtimestamp(__dateFile)
    return dateFile.ctime()


def getSize(path: Path):
    """
    Get size of file
    """
    byte = getIntsize(path)
    size_st = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    counter = 0
    while byte >= 1024 and counter < len(size_st) - 1:
        byte = byte / 1024
        counter += 1
    return f"{byte:.2f}{size_st[counter]}"

def getIntsize(path:Path):
    return  Path(path).stat().st_size

def getPermissionFile(path: Path):
    path_perm = Path(path).stat()
    is_readable = bool(path_perm.st_mode & stat.S_IRUSR)
    is_writable = bool(path_perm.st_mode & stat.S_IWUSR)
    is_executable = bool(path_perm.st_mode & stat.S_IXUSR)

    return {'r': is_readable, 'w': is_writable, 'e': is_executable}


def getExt(path: Path):
    path_ext = Path(path).suffix
    ext = {'py': '🐍'}
def fileExists(path: Path):
    return Path(path).exists()

def isFile(path:str):
    return Path(path).is_file()

def getFiles(path: str):
    if getPermissionFile(path).get('r') and fileExists(path):
        
        current = Path(path)
        files = {'dir': [], 'files': []}

        for file in current.iterdir():
                if Path(file).is_dir():
                    # files['dir'] = files.get('dir', []) + [Path(file).absolute().as_posix()]
                    files['dir'] = files.get('dir', []) + [
                        {'path': Path(file).absolute().as_posix(), 'size': getSize(file), 'time_mod': getTimeFile(file),
                        'perm': getPermissionFile(file)}]
                else:
                    # files['file'] = files.get('file', []) + [Path(file).absolute().as_posix()]
                    files['files'] = files.get('files', []) + [
                        {'path': Path(file).absolute().as_posix(), 'size': getSize(file), 'time_mod': getTimeFile(file),
                        'perm': getPermissionFile(file)}]

        yield files
    return {}
