import sys
import os
from pathlib import Path

# Handle bundled executable paths
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys._MEIPASS)
    SCRIPT_DIR = Path(sys.executable).parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent
    SCRIPT_DIR = BASE_DIR



from fastapi import FastAPI
from routers.app import router as templates
from routers.api import router as api
from auth.authentication import router as auth
from fastapi.staticfiles import StaticFiles
from middleware.rate_limits import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
import argparse
from contextlib import closing
import socket
import re
import uvicorn
import subprocess
import platform
from typing import Dict,List,Optional

# init fastapi
app = FastAPI()

# init static files
app.mount("/static",StaticFiles(directory="static"),name="static")


# limiter for request user
app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)


# auth
app.include_router(auth)

# template
app.include_router(templates,prefix='')

# json
app.include_router(api)

def check_exist_IP_Port(host:str,port:int)->bool:
    """Check if port is available."""
    with closing(socket.socket(socket.AF_INET,socket.SOCK_STREAM)) as socke:
        return socke.connect_ex((host,port)) !=0
    
def find_free_port(start_port=8000,max_port=9000):
    """Check if free port btw start and max port return it."""
    for port in range(start_port,max_port):
        with closing(socket.socket(socket.AF_INET,socket.SOCK_STREAM)) as socke:
            try:
                socke.bind(("",port))
                socke.close()
                return port
            except OSError:
                continue
    return RuntimeError(f"No free ports found in range {start_port} - {max_port}")
                

def check_host(ip:str)->bool:
    """Check if ip is valid in IPV4."""
    pattern = r"^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    return bool(re.match(pattern, ip))

def get_local_ip()->str:
    """Get the primary"""
    
    try:
        sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8",80))
        local_ip=sock.getsockname()[0]
        sock.close()
        return local_ip
    except : 
        return "127.0.0.1"

def find_networl_intefaces()->Dict[str,List[str]]:
    """Find network intefraces and their IPs."""
    os_name=platform.system()
    interfaces={"wifi":[],"ethernet":[],"all":[]}
    
    try:
        if os_name=="Windows":
            result=subprocess.run(
                ["ipconfig","/all"],
                capture_output=True,
                text=True
            )
            lines=result.stdout.split("\n")
            current_adapter=None
            
            for line in lines:
                if "Wireless" in line or "Wi-Fi" in line:
                    current_adapter="wifi"
                elif "Ethernet" in line:
                    current_adapter="ethernet"
                    
                if "IPv4 Address" in line or "IP Address" in line:
                    parts=line.split(":")
                    if len(parts) > 1:
                            ip=parts[1].strip().split("(")[0].strip()
                            
                            if current_adapter:
                                interfaces[current_adapter].append(ip)
                            interfaces["all"].append(ip)
        else:
            try:
                result=subprocess.run(
                    ["ip","addr","show"],
                    capture_output=True,
                    text=True
                )
                lines = result.stdout.split('\n')
                current_iface = None
                
                for line in lines:
                    # Detect interface name
                    if ': ' in line and '@' not in line:
                        parts = line.split(': ')
                        if len(parts) >= 2:
                            iface = parts[1].split('@')[0]
                            if 'wl' in iface or 'wlan' in iface:
                                current_iface = 'wifi'
                            elif 'eth' in iface or 'en' in iface:
                                current_iface = 'ethernet'
                            else:
                                current_iface = None
                    
                    # Extract IP addresses
                    if 'inet ' in line and '127.0.0.1' not in line:
                        ip = line.split('inet ')[1].split('/')[0]
                        if current_iface:
                            interfaces[current_iface].append(ip)
                        interfaces['all'].append(ip)
            
            except FileNotFoundError:
                # Fallback to ifconfig
                result = subprocess.run(
                    ['ifconfig'], 
                    capture_output=True, 
                    text=True
                )
                
                import re
                # Extract all IPv4 addresses
                ips = re.findall(r'inet\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
                interfaces['all'] = [ip for ip in ips if ip != '127.0.0.1']
    
    except Exception as e:
        print(f"Error getting interfaces: {e}")
        # Fallback: just get primary IP
        interfaces['all'] = [get_local_ip()]
    
    return interfaces



parser=argparse.ArgumentParser(description="App local host can share file (down/upload) files on System.")


parser.add_argument("--port","-p",type=int,default=None,help="Choose Port (choose port not active) status with : netstat")

parser.add_argument("--local","-l",type=str,default=None,help="Choose IP (must ip exist your os) win: ipconfig \n linux: ip a")


args=parser.parse_args()

# if __name__=="__main__":
    
#     if args.local is not None:
#         ip=args.local
#         if check_host(ip):
#             port=args.port
#             if port is not None:
#                 if args.port in range(0,65536):
#                         if check_exist_IP_Port(ip,port):
#                             print("Loading . . . ")
#                             uvicorn.run(app,host=ip,port=port)
#                         else:
#                             print("IP not exist in OS or port is uses")
#                 else:
#                     print("Port  Out of range must between 0, 65535 ")
#             else:
#                 print("Port  Out of range must between 0, 65535 number")
#         else:
#             print("IP must like this 192.168.1.1")
#     else:
#         interfaces=find_networl_intefaces()
#         port=find_free_port(8001,9000)
#         print(port)
#         uvicorn.run(app,host=interfaces["wifi"][0],port=port)

if __name__=="__main__":
    
    if args.local is not None:
        # Manual IP configuration
        ip = args.local
        if check_host(ip):
            port = args.port if args.port is not None else 8000
            
            if port in range(0, 65536):
                if check_exist_IP_Port(ip, port):
                    print(f"🚀 Starting server at http://{ip}:{port}")
                    uvicorn.run(app, host=ip, port=port)
                else:
                    print(f"❌ Error: IP '{ip}' not available or port {port} already in use")
            else:
                print(f"❌ Error: Port {port} out of range (must be 0-65535)")
        else:
            print(f"❌ Error: Invalid IP format '{ip}' (expected format: 192.168.1.1)")
    else:
        # Auto-detect network configuration
        try:
            interfaces = find_networl_intefaces()
            
            # Display all available network interfaces
            print("\n" + "="*50)
            print("📡 Available Network Interfaces:")
            print("="*50)
            
            all_ips = []
            for interface_name, ips in interfaces.items():
                if ips:
                    print(f"  {interface_name.upper():12} : {', '.join(ips)}")
                    all_ips.extend([(ip, interface_name) for ip in ips])
            
            if not all_ips:
                print("  ⚠ No network interfaces detected")
            
            print("="*50 + "\n")
            
            # Select IP with priority: WiFi > Ethernet > Localhost > Fallback
            selected_ip = None
            interface_type = None
            
            if "wifi" in interfaces and interfaces["wifi"]:
                selected_ip = interfaces["wifi"][0]
                interface_type = "WiFi"
            elif "ethernet" in interfaces and interfaces["ethernet"]:
                selected_ip = interfaces["ethernet"][0]
                interface_type = "Ethernet"
            elif "localhost" in interfaces and interfaces["localhost"]:
                selected_ip = interfaces["localhost"][0]
                interface_type = "Localhost"
            else:
                selected_ip = "127.0.0.1"
                interface_type = "Fallback"
                print("⚠  Warning: No network interfaces found, using fallback\n")
            
            # Find available port
            port = find_free_port(8001, 9000)
            
            if port is None:
                print("❌ Error: No free port available in range 8001-9000")
                print("💡 Tip: Try specifying a port manually with --port")
                exit(1)
            
            # Display server info
            print(f"✓ Interface Type : {interface_type}")
            print(f"✓ Server IP      : {selected_ip}")
            print(f"✓ Server Port    : {port}")
            print(f"\n🚀 Starting server at http://{selected_ip}:{port}")
            
            if interface_type == "WiFi":
                print(f"📱 Access from other devices: http://{selected_ip}:{port}\n")
            
            uvicorn.run(app, host=selected_ip, port=port)
            
        except Exception as e:
            print(f"❌ Fatal Error: {str(e)}")
            print("💡 Try running with manual configuration: --local 127.0.0.1 --port 8000")
            exit(1)