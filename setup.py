from setuptools import setup

setup(
    name='dr1ven',
    version='0.0.1',
    install_requires=[
    ],
    packages=[
        'state',
    ],
    package_data={
        'state': [
            'static',
        ],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'state_viewer=state.viewer:main',
        ],
    },
)
