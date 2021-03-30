import subprocess
from sys import platform
from os import system


class Shell:
    @staticmethod
    def kill(program_name: str):
        if platform == "win32":
            system(f"taskkill -f -im {program_name}")
        elif platform == "linux":
            pid = subprocess.getoutput(f"pgrep {program_name}")
            if len(pid):
                subprocess.call(f"pkill {pid}")
        else:
            raise Exception( f"Kill command for platform: {platform} not implemented")

    @staticmethod
    def raw(shell_command: str):
        print(shell_command)
        system(shell_command)

    @staticmethod
    def run(program_path: str, *args):
        if platform == "win32":
            system(f'start "{program_path}" "{" ".join(list(args))}"')
        elif platform == "linux":
            system(f'{program_path} "{" ".join(list(args))}"')
        else:
            raise NotImplemented(f"run command for platform: {platform} not implemented")
