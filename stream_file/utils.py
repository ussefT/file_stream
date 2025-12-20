import stat
import string
from datetime import datetime
from os import name, access, R_OK, W_OK, X_OK
from pathlib import Path
from typing import Generator
import random
import mimetypes

def random_char(n)->str:
    """
    Generate character random
    """
    return ''.join(random.choice(string.ascii_letters+string.digits+string.punctuation) for _ in range(n))

def random_digit(n)->str:
    """
    Generate digits randim
    """
    return ''.join(random.choice(string.digits)for _ in range(n))

def getDisk()->list[Path]:
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


def getTimeFile(path: Path|str)->str:
    """
    Return human-readable modified time.
    """
    try:
        return datetime.fromtimestamp(Path(path).stat().st_mtime).ctime()
    except (PermissionError, OSError, ValueError):
        return ""


def getSize(path: Path|str)->str:
    """
    Get size of file
    """
    byte = getIntsize(path)
    size_st = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    counter = 0
    while byte >= 1024 and counter < len(size_st) - 1:
        byte = byte / 1024
        counter += 1
    return f"{byte:.2f} {size_st[counter]}"

def getIntsize(path:Path|str)->int:
    """
    Size of path
    """
    try:
        return Path(path).stat().st_size
    except (PermissionError, OSError, ValueError):
        return 0

def getPermissionFile(path: Path|str):
    """
    Permission of path
    """
    perms = {'r': False, 'w': False, 'e': False}

    try:
        path_obj = Path(path)

        if not path_obj.exists():
            return perms

        if name == 'nt':
            path_str = str(path_obj)
            perms['r'] = access(path_str, R_OK)
            perms['w'] = access(path_str, W_OK)
            perms['e'] = access(path_str, X_OK)
            return perms

        path_stat = path_obj.stat().st_mode
        perms['r'] = bool(path_stat & stat.S_IRUSR)
        perms['w'] = bool(path_stat & stat.S_IWUSR)
        perms['e'] = bool(path_stat & stat.S_IXUSR)

    except (PermissionError, OSError, ValueError):
        return perms

    return perms

def getMtimeTs(path: Path | str) -> int:
    try:
        return int(Path(path).stat().st_mtime)
    except (PermissionError, OSError, ValueError):
        return 0

def getMime(path: Path | str) -> str:
    try:
        mime, _ = mimetypes.guess_type(str(path))
        return mime or "application/octet-stream"
    except Exception:
        return "application/octet-stream"

def getExtStr(path: Path | str) -> str:
    try:
        return Path(path).suffix.lstrip(".").lower()
    except Exception:
        return ""
    

def fileExists(path: Path|str):
    """
    Check exist file
    """
    return Path(path).exists()

def isFile(path:str|str):
    """
    Check path is file
    """
    return Path(path).is_file()

def fileName(path:Path|str):
    """
    Get filename path
    """
    return Path(path).name

def get_folder_size_bytes(path:Path|str)->int:
    total=0
    try:
        for root in path.rglob("*"):
            try:
                if root.is_file():
                    total+=root.stat().st_size
            except Exception:
                continue
    except Exception:
        pass
    
    return total

def getFiles(path: Path|str='.')->Generator[dict,None,None]:
        """
        Yield directory content (dirs + files) with meta 
        """
        
        path=Path(path)
        files = {'dir': [], 'files': []}

        try:
            if not path.exists():
                yield files
                return
        except (PermissionError, OSError, ValueError):
            yield files
            return
        
        if not getPermissionFile(path).get("r",False):
            yield files
            return

        try:
            iterator = path.iterdir()
        except (PermissionError, OSError, ValueError):
            yield files
            return

        while True:
            try:
                item = next(iterator)
            except StopIteration:
                break
            except (PermissionError, OSError, ValueError):
                break

            try:
                perm = getPermissionFile(item)
                size_b = getIntsize(item)
                meta = {
                    "path": item.absolute().as_posix(),  
                    "name": item.name,                     
                    "size_b": size_b,                     
                    "size_h": getSize(item),           
                    "mtime_ts": getMtimeTs(item),        
                    "time_mod": getTimeFile(item),         
                    "mime": getMime(item),                
                    "ext": getExtStr(item),               
                    "perm": perm,
                }

                if item.is_dir():
                    listable = True
                    try:
                        it = item.iterdir()
                        try:
                            next(it)
                        except StopIteration:
                            pass
                    except (PermissionError, OSError, ValueError):
                        listable = False
                    meta["listable"] = listable
                    files["dir"].append(meta)
                else:
                    files["files"].append(meta)
            except (PermissionError, OSError, ValueError):
                continue

        yield files