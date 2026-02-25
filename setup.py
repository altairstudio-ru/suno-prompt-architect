from setuptools import setup, find_packages
setup(
    name="suno-prompt-architect",
    version="1.0.0",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={
        "console_scripts": [
            "suno-prompt=cli:app",
        ],
    },
)
