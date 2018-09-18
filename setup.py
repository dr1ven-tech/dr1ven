from setuptools import setup

setup(
    name='dr1ven',
    version='0.0.1',
    install_requires=[
    ],
    packages=[
        'symbolic',
    ],
    package_data={
        'symbolic': [
            'static',
        ],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'symbolic_viewer=symbolic.viewer:main',
        ],
    },
)
