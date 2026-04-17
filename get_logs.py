import os
import urllib.request
import zipfile
import subprocess
import sys

TOOLS_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
ZIP_PATH = "platform-tools.zip"
ADB_PATH = os.path.join("platform-tools", "adb.exe")

def main():
    print("--------------------------------------------------")
    print("  Downloading Android Debug Bridge (ADB)...")
    print("--------------------------------------------------")
    if not os.path.exists(ADB_PATH):
        urllib.request.urlretrieve(TOOLS_URL, ZIP_PATH)
        print("  Extracting ADB...")
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(".")
        os.remove(ZIP_PATH)
        print("  ADB Downloaded to platform-tools/adb.exe")
    else:
        print("  ADB already exists locally.")

    print("\n--------------------------------------------------")
    print("  Starting ADB server...")
    subprocess.run([ADB_PATH, "start-server"])

    print("\n  WAITING FOR DEVICE...")
    print("  -> Please ensure your phone is PLUGGED IN via USB.")
    print("  -> Ensure 'USB DEBUGGING' is turned ON in Developer Options.")
    print("  -> Authorize the PC if a prompt appears on your phone.")
    subprocess.run([ADB_PATH, "wait-for-device"])

    print("\n  Device found! Clearing old system logs...")
    subprocess.run([ADB_PATH, "logcat", "-c"])

    print("\n==================================================")
    print("  ACTION REQUIRED:")
    print("  Please launch the Ball Sort APK on your phone NOW!")
    print("  Waiting 15 seconds to capture the crash event...")
    print("==================================================")
    
    import time
    time.sleep(15)

    print("\n  Capturing logcat to logs/crash_log.txt...")
    os.makedirs("logs", exist_ok=True)
    with open(os.path.join("logs", "crash_log.txt"), "w", encoding="utf-8", errors="ignore") as f:
        subprocess.run([ADB_PATH, "logcat", "-d"], stdout=f)
        
    print("\n  DONE! The logs have been dumped to 'logs/crash_log.txt'.")
    print("  Please provide the contents of logs/crash_log.txt to your assistant.")
    
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Failed to pull logs: {e}")
    finally:
        input("\nPress Enter to exit...")
