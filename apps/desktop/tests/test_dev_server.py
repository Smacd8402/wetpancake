import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


def test_desktop_dev_serves_start_call_page():
    repo_root = Path(__file__).resolve().parents[3]
    process = subprocess.Popen(
        ["npm.cmd", "--workspace", "apps/desktop", "run", "dev"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        time.sleep(2)
        with urllib.request.urlopen("http://127.0.0.1:5173", timeout=2) as response:
            html = response.read().decode("utf-8")
        assert "Start Call" in html
    except urllib.error.URLError as exc:
        raise AssertionError("Desktop dev server is not reachable on 127.0.0.1:5173") from exc
    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
