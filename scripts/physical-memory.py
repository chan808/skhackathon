"""Read installed RAM metadata without collecting device identity or using WMI."""
import ctypes
import json
import sys
from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    path = ROOT / "reports" / "windows-preflight.json"
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    memory_kib = ctypes.c_ulonglong()
    function = ctypes.WinDLL("kernel32", use_last_error=True).GetPhysicallyInstalledSystemMemory
    function.argtypes = [ctypes.POINTER(ctypes.c_ulonglong)]
    function.restype = ctypes.c_int
    if function(ctypes.byref(memory_kib)):
        document["memory_gib"] = round(memory_kib.value / 1024 / 1024, 2)
        document["memory_method"] = "GetPhysicallyInstalledSystemMemory, installed RAM rather than available free memory"
    else:
        document["inventory_errors"].append("Installed RAM metadata query also unavailable.")
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"memory_gib": document["memory_gib"], "memory_method": document.get("memory_method")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
