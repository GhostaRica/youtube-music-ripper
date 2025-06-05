import os
import subprocess
import sys

REPO_URL = "https://github.com/GhostaRica/youtube-music-ripper.git"
CLONE_DIR = "repo"
COMMIT_FILE = "last_commit.txt"

# Clone or pull repo
if os.path.exists(CLONE_DIR):
    print("🔁 Pulling latest changes...")
    subprocess.run(["git", "-C", CLONE_DIR, "pull"], check=True)
else:
    print("⬇️ Cloning repository...")
    subprocess.run(["git", "clone", REPO_URL, CLONE_DIR], check=True)

# Save the latest commit to a txt file
result = subprocess.run(
    ["git", "-C", CLONE_DIR, "rev-parse", "HEAD"],
    capture_output=True,
    text=True,
    check=True
)
latest_commit = result.stdout.strip()
with open(COMMIT_FILE, "w") as f:
    f.write(latest_commit)
print(f"✅ Latest commit saved: {latest_commit}")

# Forward all CLI arguments to the inner script
script_path = os.path.join(CLONE_DIR, "main.py")
args = [sys.executable, script_path] + sys.argv[1:]
print(f"🚀 Running: {' '.join(args)}")
subprocess.run(args, check=True)
