from setuptools import setup, find_packages

setup(
    name="fluxr",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "colorama>=0.4.6",
        "pydantic>=2.0.0",
        "loguru>=0.7.0",
        "openai>=1.0.0",
        "python-telegram-bot>=20.0",
        "openpyxl>=3.1.0"
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A modular hyperautomation framework inspired by CrewAI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fluxr",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)