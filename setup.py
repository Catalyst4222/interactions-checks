import re

from setuptools import setup

with open("interactions/ext/checks/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="interactions-checks",
    version=version,
    description="Add in check decorators for discord-py-interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Catalyst4222/interactions-checks",
    author="Catalyst4",
    author_email="catalyst4222@gmail.com",
    license="MIT",
    packages=["interactions.ext.checks"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["discord-py-interactions>=4.0.0"],
)
