from setuptools import find_packages, setup

version = {}
with open("delta/__version__.py") as fp:
    exec(fp.read(), version)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="delta",
    version=version["version"],
    author="Outside Open",
    author_email="developers@outsideopen.com",
    packages=find_packages(),
    scripts=["bin/delta"],
    url="https://github.com/outsideopen/delta-collectors",
    license="GPL",
    description="Delta Collectors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "colorlog",
        "persistQueue",
        "python3-nmap",
        "requests",
    ],
    platforms=["linux"],
)
