import subprocess
import time


def exec_command(cmd, timeout=None, ignore_error=False, retry_count=1, retry_delay=0):
    while retry_count > 0:
        res = subprocess.run(cmd, shell=True, timeout=timeout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res.stdout = res.stdout.decode('utf-8')
        res.stderr = res.stderr.decode('utf-8')
        retry_count -= 1
        if res.returncode != 0 and ignore_error is False:
            if retry_count == 0:
                raise SystemError(res.returncode, res.stderr)
            else:
                time.sleep(retry_delay)
        else:
            return res
