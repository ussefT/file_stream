import stat
import string
from datetime import datetime
from os import name
from pathlib import Path


def getDisk()->list:
    """
    Get local disk
    """
    # Windows
    path = []
    if name == 'nt':
        for drive in string.ascii_uppercase:
            if Path(f"{drive}:/").exists():
                path.append(f"{drive}:")

        return path
    # Linux
    else:
        return [Path('/')]


def getTimeFile(path: Path)->str:
    """
    Return human-readable modified time.
    """
    return datetime.fromtimestamp(Path(path).stat().st_mtime).ctime()


def getSize(path: Path)->str:
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

def getIntsize(path:Path)->int:
    """Get item size path return byte"""
    return  Path(path).stat().st_size

def getPermissionFile(path: Path)->dict:
    """Get permission mod return dict"""
    path_perm = Path(path).stat().st_mode
    is_readable = bool(path_perm & stat.S_IRUSR)
    is_writable = bool(path_perm & stat.S_IWUSR)
    is_executable = bool(path_perm & stat.S_IXUSR)

    return {'r': is_readable, 'w': is_writable, 'e': is_executable}


def getExt(path: Path)->str:
    """Get suffix from path"""
    path_ext = Path(path).suffix
    return path_ext
    

def fileExists(path: Path)->bool:
    """Check path exist or not"""
    return Path(path).exists()

def isFile(path:str)->bool:
    """Check path is file or not"""
    return Path(path).is_file()

def fileName(path:Path)->str:
    """Get filename from path"""
    return Path(path).name

def getFiles(path: str='.'):
    """Get files and dir in path return dict {dir:[{'path':str,'size':int,'time_mod':str,'perm':dict}]}"""
    if getPermissionFile(path).get('r') and fileExists(path):
        
        current = Path(path)
        files = {'dir': [], 'files': []}

        for file in current.iterdir():
                if Path(file).is_dir():
                    # files['dir'] = files.get('dir', []) + [Path(file).absolute().as_posix()]
                    files['dir'] = files.get('dir', []) + [
                        {'path': Path(file).absolute().as_posix(),
                        'size': getSize(file),
                        'time_mod': getTimeFile(file),
                        'perm': getPermissionFile(file)}
                        ]
                else:
                    # files['file'] = files.get('file', []) + [Path(file).absolute().as_posix()]
                    files['files'] = files.get('files', []) + [
                        {'path': Path(file).absolute().as_posix(), 'size': getSize(file), 'time_mod': getTimeFile(file),
                        'perm': getPermissionFile(file)}]

        yield files
    return {}