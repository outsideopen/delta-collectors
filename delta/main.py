from delta.runner import Runner
from delta.uploader import Uploader


def run():
    uploader = Uploader()
    uploader.run()

    runner = Runner()
    runner.run()
