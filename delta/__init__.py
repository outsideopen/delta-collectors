__version__ = "0.0.1"


def main():
    import os
    import sys

    if os.geteuid() == 0:
        from delta.runner import Runner
        from delta.uploader import Uploader

        uploader = Uploader()
        uploader.run()

        runner = Runner()
        runner.run()
    else:
        print("This script needs to be run as root.", file=sys.stderr)
