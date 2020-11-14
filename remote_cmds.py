import subprocess
import sys

import time

remote = sys.argv[1]
use_builtin = bool(sys.argv[2])

# startup commands. Use to check configuration
once_builtin_cmds = [
    """docker inspect scraper_container | grep ".txt" """,

]


def exec_cmd(r, cmd):
    _ = subprocess.call(["vagrant", "ssh", r, "-c", cmd])

if remote == "all":
    remote = [
        "scraperserver1",
        "scraperserver2",
        "scraperserver3",
        "scraperserver4",
        "scraperserver5",
        "scraperserver6",
        "scraperserver7",
    ]

if use_builtin:
    for r in remote:
        for c in once_builtin_cmds:
            exec_cmd(r, c)

while True:
    if type(remote) == str:
        exec_cmd(remote, input())
    else:
        if not use_builtin:
            print()
            print("Enter command:")
            user_input = input()
            for r in remote:
                print()
                print("Remote", r)
                exec_cmd(r, user_input)
        else:
            for r in remote:
                print()
                print("Remote", r)

                # used to continiously check state of running services
                continue_builtin_cmds = [
                    """ docker ps -a """, 
                    f"""ls -lah /vagrant/output/{r.replace("scraperserver", "")}/"""
                ]

                for c in continue_builtin_cmds:
                    exec_cmd(r, c)

            sleep_time = 60
            print()
            print(f"Sleeping for {sleep_time} before repeating...")
            time.sleep(sleep_time)
            print()
