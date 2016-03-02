import subprocess
import os
import win32con
from . import Basic, sargeWrapper

def expandVariables(*strs):
    retStrs = []

    for s in strs:
        retStr = s
        items = os.environ.items()
        for k, v in list(items):
            retStr = retStr.replace('%'+k+'%', v)
        retStrs.append(retStr)

    return tuple(retStrs)

_CMD_MODE_MAP = {
    "run": sargeWrapper.run,
    "capture_stdout": sargeWrapper.capture_stdout,
    "capture_stderr": sargeWrapper.capture_stderr,
    "capture_both": sargeWrapper.capture_both,

}
_CMD_KWDS_MAP = {
    "PIPE": subprocess.PIPE,
}

@Basic.fwKeyWordMap(_CMD_KWDS_MAP, ["run_mode", "win_mode"])
def runShellCmd(cmd, run_mode="capture_both", win_mode="hide", **kwds):
    # startupinfo = subprocess.STARTUPINFO()
    # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    runner = _CMD_MODE_MAP[run_mode]
    startupinfo = None
    if win_mode == "hide":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = win32con.SW_HIDE

    out = runner(cmd, startupinfo=startupinfo, **kwds)
    return (out.returncode,
            out.encoding,
            out.stdoutText if out.stdoutText is not None else "!!can't get stdout",
            out.stderrText if out.stderrText is not None else "!!can't get stderr")


