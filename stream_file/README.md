# Stream storage

- You can download, upload, stream video or image without install extra app on mobile or PC.
- Work any OS

## Install
For Windows:
after install python. check installed:
```cmd
python --help
```
In folder:

```cmd
python -m venv venv
```

after that active 
```cmd
cd venv\Script\
activate
```

For Linux:
Debian base
```bash
sudo apt install python3-venv -y
```

Redhat base
```bash
sudo dnf install python3-venv
```

Create environment:
```bash
python3 -m venv venv
```
for active:
```bash
source venv/bin/activate
```

Install requirements.txt
```bash
pip install -r requirements.txt
```

## Use
Run on local ip address wifi:
```bash
ifconfig
```

```bash
fastapi dev play.py --localhost 192.168.56.113 --port 8000
```

```text
192.168.56.113:8000
```