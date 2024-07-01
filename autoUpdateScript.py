import os
import subprocess
import time

# Configuration
GIT_REPO = "https://github.com/redifo/walle"
LOCAL_REPO_PATH = "/home/walle/Desktop/repo"
CHECK_INTERVAL = 60  # Check every 60 seconds

def log(message):
    with open("/home/walle/Desktop/repo/cron_script.log", "a") as log_file:
        log_file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

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
        with open("/home/walle/Desktop/repo/server_output.log", "a") as out_log:
            subprocess.Popen(["python3", os.path.join(LOCAL_REPO_PATH, "server.py")], stdout=out_log, stderr=out_log)
    except Exception as e:
        log(f"Exception in run_code: {e}")


if __name__ == "__main__":
    log("Starting update and run script.")
    first_run = True
    while True:
        try:
            if update_repo():
                log("Updates detected, running code.")
                run_code()
            elif first_run:
                log("First run, starting server.py.")
                run_code()
                first_run = False
        except Exception as e:
            log(f"Exception in main loop: {e}")
        time.sleep(CHECK_INTERVAL)
