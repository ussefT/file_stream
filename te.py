
from pathlib import Path

def getFiles(path:str):
    current=Path(path)
    files={'dir':[],'files':[]}
    for file in current.iterdir():
        if Path(file).exists():
            if Path(file).is_dir():
                files['dir']=files.get('dir',[])+[Path(file).absolute().as_posix()]
            else:
                files['file']=files.get('file',[])+[Path(file).absolute().as_posix()]

    yield files

# print([i for i in getFiles('/home')])
# getFiles('/home')