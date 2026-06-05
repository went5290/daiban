# -*- coding: utf-8 -*-

import os
import traceback
from datetime import datetime


def write_error_log() -> None:
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error.log")
    with open(log_path, "a", encoding="utf-8") as file:
        file.write("\n" + "=" * 70 + "\n")
        file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        traceback.print_exc(file=file)


try:
    from reminder_app import main

    main()
except Exception:
    write_error_log()
    raise
