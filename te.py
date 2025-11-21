from pathlib import Path
from os import name
import string
from datetime import datetime

def getDisk():
    """
    Get local disk
    """
    # Windows
    path=[]
    if name=='nt':
        for drive in string.ascii_uppercase:
            if Path(f"{drive}:/").exists():
                path.append(f"{drive}:/")

        return path
    # Linux
    else:
        return [Path('/')]

def gettimeFile(path:Path):
    """
    Get time D M Day_number h:m:s Y
    """
    __dateFile=Path(path).stat().st_mtime
    dateFile=datetime.fromtimestamp(__dateFile)
    return dateFile.ctime()

def getSize(path:Path):
    """
    Get size of file
    """
    byte=Path(path).stat().st_size
    size_st=['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    counter=0
    while byte>=1024 and counter<len(size_st)-1:
        byte=byte/1024
        counter+=1
    return f"{byte:.2f}{size_st[counter]}"

def getFiles(path: str):
    current = Path(path)
    files = {'dir': [], 'files': []}
    for file in current.iterdir():
        if Path(file).exists():
            if Path(file).is_dir():
                files['dir'] = files.get('dir', []) + [Path(file).absolute().as_posix()]

            else:
                files['file'] = files.get('file', []) + [Path(file).absolute().as_posix()]

    yield files
