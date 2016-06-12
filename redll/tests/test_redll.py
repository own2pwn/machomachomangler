import sys
import os.path
import subprocess
import shutil

import pytest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))

def run_exe(path, *, expect_success=True):
    if hasattr(path, "strpath"):
        path = path.strpath
    path = os.path.abspath(path)
    if os.name == "nt":
        runner = []
    else:
        runner = ["wine"]
    ran = subprocess.run(runner + [path])
    if expect_success:
        assert ran.returncode == 0
    else:
        assert ran.returncode != 0

def test_redll_end_to_end(tmpdir, monkeypatch):
    monkeypatch.setenv("WINEPREFIX", tmpdir.join("wineprefix").strpath)
    for arch in ["i686", "x86_64"]:
        print("Testing", arch)
        archdir = tmpdir.join(arch)
        shutil.copytree(os.path.join(TEST_DIR, "sample-dll", arch),
                        archdir.strpath)

        # To start with, everything works
        run_exe(archdir.join("main.exe"))

        # Then we rename the .dll, and it stops working
        archdir.join("sample-dll.dll").rename(
            archdir.join("renamed-sample-dll.dll"))
        run_exe(archdir.join("main.exe"), expect_success=False)

        # Then we run redll, and it works again
        subprocess.run([sys.executable, "-m", "redll",
                        archdir.join("main.exe").strpath,
                        archdir.join("patched-main.exe").strpath,
                        "sample-dll.dll", "renamed-sample-dll.dll"],
                       check=True)

        run_exe(archdir.join("patched-main.exe"))