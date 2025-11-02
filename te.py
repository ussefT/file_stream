from pathlib import Path

def getFiles():
    current=Path('.')
    files={}
    for file in current.iterdir():
        if Path(file).exists():
            if Path(file).is_dir():
                files['dir']=str(Path(file).absolute().as_posix())+','
            else:
                files['file']=files.get('file','')+str(Path(file).absolute().as_posix())+','
    
    files['file']=files.pop('file').split(',')
    files.get('file').remove('')
    files['dir']=files.pop('dir').split(',')
    files.get('dir').remove('')
    return files
print(getFiles())

