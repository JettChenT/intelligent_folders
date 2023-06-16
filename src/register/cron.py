from crontab import CronTab
from pathlib import Path
import os
import sys

def get_command()->str:
    cur_loc = Path(__file__)
    base_loc = cur_loc.parent.parent
    service_loc = base_loc / "service.py"
    interpreter_loc = Path(sys.executable)
    return f"{interpreter_loc} {service_loc}"

def gen_crontab():
    cron_expr = f"@reboot {get_command()}"
    cron = CronTab(user=True)
    job = cron.new(command=get_command())
    job.setall("@reboot")
    cron.write()
    return cron_expr