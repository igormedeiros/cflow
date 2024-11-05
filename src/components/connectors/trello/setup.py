from setuptools import setup, find_packages

setup(
    name='trello',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-dotenv',
    ],
    entry_points={
        'core.connectors': [
            'trello = trello:TrelloConnector',
        ],
    },
    description='A Trello Connector for the core framework',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/trello_connector',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)