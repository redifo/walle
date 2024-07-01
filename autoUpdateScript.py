import os
import subprocess
import time
from datetime import datetime, timedelta

# Configuration
GIT_REPO = "https://github.com/redifo/walle"
LOCAL_REPO_PATH = "/home/walle/Desktop/repo"
LOG_FILE_PATH = "/home/walle/Desktop/repo/cron_script.log"
SERVER_LOG_FILE_PATH = "/home/walle/Desktop/repo/server_output.log"
CHECK_INTERVAL = 60  # Check every 60 seconds
LOG_ROTATION_INTERVAL = timedelta(days=1)  # Rotate logs daily

# Initialize last rotation time
last_rotation_time = datetime.now()

def log(message):
    with open(LOG_FILE_PATH, "a") as log_file:
        log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def rotate_logs():
    global last_rotation_time
    current_time = datetime.now()
    if current_time - last_rotation_time >= LOG_ROTATION_INTERVAL:
        for file_path in [LOG_FILE_PATH, SERVER_LOG_FILE_PATH]:
            if os.path.exists(file_path):
                os.rename(file_path, f"{file_path}.{current_time.strftime('%Y%m%d%H%M%S')}")
        last_rotation_time = current_time
        log("Log files rotated.")

def update_repo():
    try:
        if not os.path.exists(LOCAL_REPO_PATH):
            log("Local repo path does not exist, cloning the repository.")
            result = subprocess.run(["git", "clone", GIT_REPO, LOCAL_REPO_PATH], capture_output=True, text=True)
            if result.returncode == 0:
                log("Repository cloned successfully.")
                return True  # New code cloned, need to run
            else:
                log(f"Error cloning repository: {result.stderr}")
                return False
        else:
            log("Fetching updates from the repository.")
            result = subprocess.run(["git", "-C", LOCAL_REPO_PATH, "fetch"], capture_output=True, text=True)
            if result.returncode != 0:
                log(f"Error fetching updates: {result.stderr}")
                return False
                
            log("Resetting local changes.")
            result = subprocess.run(["git", "-C", LOCAL_REPO_PATH, "reset", "--hard", "origin/main"], capture_output=True, text=True)
            if result.returncode != 0:
                log(f"Error resetting local changes: {result.stderr}")
                return False

            log("Checking for changes.")
            changes = subprocess.run(["git", "-C", LOCAL_REPO_PATH, "diff", "HEAD", "origin/main"], capture_output=True, text=True)
            if changes.returncode != 0:
                log(f"Error checking for changes: {changes.stderr}")
                return False

            if changes.stdout:
                log("Changes detected, pulling updates.")
                pull_result = subprocess.run(["git", "-C", LOCAL_REPO_PATH, "pull", "--rebase=false"], capture_output=True, text=True)
                if pull_result.returncode == 0:
                    log("Updates pulled successfully.")
                    return True  # New changes pulled, need to run
                else:
                    log(f"Error pulling updates: {pull_result.stderr}")
                    return False
            else:
                log("No changes detected.")
                return False  # No changes
    except Exception as e:
        log(f"Exception in update_repo: {e}")
        return False

def run_code():
    try:
        log("Starting server.py.")
        with open(SERVER_LOG_FILE_PATH, "a") as out_log:
            subprocess.Popen(["python3", os.path.join(LOCAL_REPO_PATH, "server.py")], stdout=out_log, stderr=out_log)
    except Exception as e:
        log(f"Exception in run_code: {e}")

def check_server_running():
    try:
        response = requests.get("http://localhost:5000")
        if response.status_code == 200:
            log("Server is running as expected.")
            return True
        else:
            log("Server is not running as expected.")
            return False
    except requests.ConnectionError:
        log("Server is not running (connection error).")
        return False
    except Exception as e:
        log(f"Exception in check_server_running: {e}")
        return False

if __name__ == "__main__":
    log("Starting update and run script.")
    first_run = True
    while True:
        try:
            rotate_logs()
            if update_repo() or first_run:
                log("Starting or restarting server due to updates or first run.")
                run_code()
                first_run = False

            if not check_server_running():
                log("Server is not running properly, attempting to restart.")
                run_code()
        except Exception as e:
            log(f"Exception in main loop: {e}")
        time.sleep(CHECK_INTERVAL)
