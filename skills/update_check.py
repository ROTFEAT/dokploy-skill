"""
dokploy-skill version check — compare local VERSION against GitHub.

Usage:
    python skills/update_check.py          # report only
    python skills/update_check.py --update # also run git pull --ff-only
"""
import os
import subprocess
import sys
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_FILE = os.path.join(SCRIPT_DIR, "VERSION")


def local_version() -> str:
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE) as f:
            return f.read().strip()
    return "unknown"


def remote_version() -> str | None:
    try:
        r = subprocess.run(
            ["git", "-C", SCRIPT_DIR, "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode != 0:
            return None
        url = r.stdout.strip()
        if "github.com" not in url:
            return None
        if url.startswith("https://"):
            slug = url.replace("https://github.com/", "").replace(".git", "")
        elif "git@github.com:" in url:
            slug = url.replace("git@github.com:", "").replace(".git", "")
        else:
            return None
        owner_repo = "/".join(slug.split("/")[:2])
        # Try main first, fall back to master.
        for branch in ("main", "master"):
            api = f"https://raw.githubusercontent.com/{owner_repo}/{branch}/VERSION"
            try:
                with urllib.request.urlopen(api, timeout=5) as resp:
                    return resp.read().decode().strip()
            except urllib.error.HTTPError:
                continue
    except Exception:
        pass
    return None


def tup(v: str) -> tuple:
    try:
        return tuple(int(x) for x in v.split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def pull() -> tuple[bool, str]:
    r = subprocess.run(
        ["git", "-C", SCRIPT_DIR, "pull", "--ff-only"],
        capture_output=True, text=True, timeout=30,
    )
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def main() -> None:
    local = local_version()
    remote = remote_version()
    do_update = "--update" in sys.argv

    if remote is None:
        print(f"dokploy-skill v{local}")
        return

    if tup(remote) > tup(local):
        print(f"dokploy-skill v{local} → v{remote} update available")
        if do_update:
            ok, msg = pull()
            print(f"  {'✓ updated to v' + remote if ok else '✗ pull failed'}")
            if msg:
                print(f"  {msg}")
        else:
            print(f"  cd {SCRIPT_DIR} && git pull")
            print("  or:  python skills/update_check.py --update")
    else:
        print(f"dokploy-skill v{local} (latest)")


if __name__ == "__main__":
    main()
