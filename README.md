# 🚀 Stream Storage

🌐[Persian](https://github.com/ussefT/file_stream/blob/main/fa.md)

- 📥 Download, 📤 upload, and 🎬 stream videos or 🖼️ images without installing any extra application on your mobile device or computer.
- 💻 Works on any operating system (Windows, Linux, macOS).

---

## 🛠️ Installation

### 🪟 Windows

First, install Python and verify that it is installed correctly:

```cmd
python --help
```

Create a virtual environment inside the project folder:

```cmd
python -m venv venv
```

Then activate it:

```cmd
cd venv\Scripts\
activate
```


---

### 🐧 Linux

#### Debian / Ubuntu

```bash
sudo apt install python3-venv -y
```

#### Red Hat / Fedora

```bash
sudo dnf install python3-venv
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

---

### 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚡ Easy Usage

Automatically start the server on the current Wi-Fi interface.

📱 Make sure your phone and computer are connected to the same Wi-Fi network.

```bash
python main.py
```

Example output:

```text
==================================================
📡 Available Network Interfaces:
==================================================
  WIFI         : 192.168.43.119
  ETHERNET     : 192.168.56.1, 172.22.224.1
  ALL          : 192.168.56.1, 192.168.43.119, 172.22.224.1
==================================================

✓ Interface Type : WiFi
✓ Server IP      : 192.168.43.119
✓ Server Port    : 8001

🚀 Starting server at:
http://192.168.43.119:8001
```

---

### 🎯 Custom IP Address and Port

```bash
python main.py -l 192.168.56.1 -p 8000
```

---

## 🔧 Advanced Usage

Find your local IP address:

```bash
ifconfig
```

Start the server on a specific IP address and port:

```bash
fastapi dev main.py --localhost 192.168.56.113 --port 8000
```

Access the server using:

```text
192.168.56.113:8000
```

---

## ✨ Features & Notes

- 📱 Access the server directly from your mobile browser.
- 🎥 Stream video files without downloading them first.
- 📂 Upload and download files easily.
- 🌐 All devices connected to the same local network can access the server (subject to firewall rules).
- ⚡ Lightweight and simple to set up.
- 🔒 Runs entirely within your local network by default.
