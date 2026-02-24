"""
Minimal cross-platform system information module.
Returns a single dict with all hardware + OS info.

Usage:
    from system_info import get_system_info
    info = get_system_info()
"""

import platform
import socket
import os
import getpass
import struct
from datetime import datetime, timezone

import psutil

try:
    import cpuinfo as _cpuinfo
except ImportError:
    _cpuinfo = None


def _safe(func):
    """Catch any exception, return error string instead of crashing."""
    def wrapper(*a, **kw):
        try:
            return func(*a, **kw)
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}
    return wrapper


def _h(b):
    """Bytes to human-readable string."""
    for u in ("B", "KB", "MB", "GB", "TB"):
        if abs(b) < 1024:
            return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} PB"


def _cmd(cmd, shell=False):
    """Run a command, return stdout or None."""
    import subprocess
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=10, shell=shell)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None



@_safe
def _os_info():
    uname = platform.uname()
    boot = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)

    info = {
        "platform":         uname.system,
        "release":          uname.release,
        "version":          uname.version,
        "architecture":     uname.machine,
        "hostname":         socket.gethostname(),
        "fqdn":             socket.getfqdn(),
        "username":         getpass.getuser(),
        "boot_time_utc":    boot.isoformat(),
        "uptime_seconds":   int((now - boot).total_seconds()),
        "python_version":   platform.python_version(),
        "pointer_bits":     struct.calcsize("P") * 8,
    }

    OS = uname.system
    if OS == "Linux":
        try:
            with open("/etc/os-release") as f:
                d = {}
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        d[k] = v.strip('"')
                info["distro"] = d
        except FileNotFoundError:
            pass

    elif OS == "Windows":
        info["edition"] = platform.win32_edition() if hasattr(platform, "win32_edition") else None
        info["win32_ver"] = platform.win32_ver()

    elif OS == "Darwin":
        info["mac_ver"] = platform.mac_ver()

    return info


@_safe
def _cpu_info():
    freq = psutil.cpu_freq()
    info = {
        "physical_cores":  psutil.cpu_count(logical=False),
        "logical_cores":   psutil.cpu_count(logical=True),
        "frequency_mhz": {
            "current": freq.current if freq else None,
            "min":     freq.min if freq else None,
            "max":     freq.max if freq else None,
        },
        "usage_percent":     psutil.cpu_percent(interval=1),
        "per_core_percent":  psutil.cpu_percent(interval=0.3, percpu=True),
        "times":             psutil.cpu_times()._asdict(),
        "stats":             psutil.cpu_stats()._asdict(),
    }

    try:
        info["load_avg"] = dict(zip(("1m", "5m", "15m"), os.getloadavg()))
    except (OSError, AttributeError):
        info["load_avg"] = None

    if _cpuinfo:
        ci = _cpuinfo.get_cpu_info()
        info["brand"]    = ci.get("brand_raw")
        info["vendor"]   = ci.get("vendor_id_raw")
        info["arch"]     = ci.get("arch")
        info["bits"]     = ci.get("bits")
        info["l2_cache"] = ci.get("l2_cache_size")
        info["l3_cache"] = ci.get("l3_cache_size")
        info["flags"]    = ci.get("flags", [])

    return info


@_safe
def _memory_info():
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()
    return {
        "ram": {
            "total":     vm.total,   "total_h":     _h(vm.total),
            "available": vm.available,"available_h": _h(vm.available),
            "used":      vm.used,    "used_h":      _h(vm.used),
            "percent":   vm.percent,
        },
        "swap": {
            "total":   sw.total,  "total_h":  _h(sw.total),
            "used":    sw.used,   "used_h":   _h(sw.used),
            "free":    sw.free,   "free_h":   _h(sw.free),
            "percent": sw.percent,
        },
    }


@_safe
def _disk_info():
    parts = []
    for p in psutil.disk_partitions(all=False):
        entry = {
            "device": p.device, "mount": p.mountpoint,
            "fstype": p.fstype, "opts": p.opts,
        }
        try:
            u = psutil.disk_usage(p.mountpoint)
            entry["total"]   = u.total
            entry["total_h"] = _h(u.total)
            entry["used_h"]  = _h(u.used)
            entry["free_h"]  = _h(u.free)
            entry["percent"] = u.percent
        except (PermissionError, OSError):
            pass
        parts.append(entry)

    io = psutil.disk_io_counters()
    return {
        "partitions": parts,
        "io": io._asdict() if io else None,
    }


@_safe
def _network_info():
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    io = psutil.net_io_counters(pernic=True)

    ifaces = {}
    for name, alist in addrs.items():
        iface = {
            "addresses": [
                {"family": str(a.family), "address": a.address,
                 "netmask": a.netmask, "broadcast": a.broadcast}
                for a in alist
            ],
        }
        if name in stats:
            s = stats[name]
            iface["up"]       = s.isup
            iface["speed_mb"] = s.speed
            iface["mtu"]      = s.mtu
        if name in io:
            c = io[name]
            iface["bytes_sent"] = c.bytes_sent
            iface["bytes_recv"] = c.bytes_recv
        ifaces[name] = iface

    return {"interfaces": ifaces}


@_safe
def _gpu_info():
    gpus = []

    # nvidia-smi
    out = _cmd([
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total,memory.used,"
        "utilization.gpu,temperature.gpu",
        "--format=csv,noheader,nounits",
    ])
    if out:
        for line in out.splitlines():
            p = [x.strip() for x in line.split(",")]
            if len(p) >= 6:
                gpus.append({
                    "name": p[0], "driver": p[1],
                    "mem_total_mb": p[2], "mem_used_mb": p[3],
                    "util_%": p[4], "temp_c": p[5],
                })

    # Windows WMI fallback
    if not gpus and platform.system() == "Windows":
        try:
            import wmi
            for g in wmi.WMI().Win32_VideoController():
                gpus.append({
                    "name":    g.Name,
                    "ram":     _h(int(g.AdapterRAM)) if g.AdapterRAM else None,
                    "driver":  g.DriverVersion,
                    "status":  g.Status,
                })
        except Exception:
            pass

    # macOS fallback
    if not gpus and platform.system() == "Darwin":
        sp = _cmd(["system_profiler", "SPDisplaysDataType"])
        if sp:
            gpus.append({"raw": sp})

    return gpus


@_safe
def _battery_info():
    b = psutil.sensors_battery()
    if b is None:
        return {"present": False}
    return {
        "present":  True,
        "percent":  b.percent,
        "plugged":  b.power_plugged,
        "secs_left": b.secsleft if b.secsleft != psutil.POWER_TIME_UNLIMITED else None,
    }


@_safe
def _sensors_info():
    data = {}
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            data["temperatures"] = {
                name: [{"label": s.label, "current": s.current,
                        "high": s.high, "critical": s.critical}
                       for s in entries]
                for name, entries in temps.items()
            }
    except AttributeError:
        pass
    try:
        fans = psutil.sensors_fans()
        if fans:
            data["fans"] = {
                name: [{"label": f.label, "rpm": f.current} for f in entries]
                for name, entries in fans.items()
            }
    except AttributeError:
        pass
    return data


@_safe
def _users_info():
    return [
        {"name": u.name, "terminal": u.terminal,
         "host": u.host, "pid": u.pid,
         "started": datetime.fromtimestamp(u.started, tz=timezone.utc).isoformat()}
        for u in psutil.users()
    ]



def get_system_info() -> dict:
    """Collect all system info and return as a single dict."""
    return {
        "os":       _os_info(),
        "cpu":      _cpu_info(),
        "memory":   _memory_info(),
        "disks":    _disk_info(),
        "network":  _network_info(),
        "gpu":      _gpu_info(),
        "battery":  _battery_info(),
        "sensors":  _sensors_info(),
        "users":    _users_info(),
    }


def to_json(indent=2) -> str:
    """Convenience: return info as a JSON string."""
    import json
    return json.dumps(get_system_info(), indent=indent, default=str,
                      ensure_ascii=False)


# Run standalone for quick test
if __name__ == "__main__":
    print(to_json())