from setuptools import setup

setup(
    name='dr1ven',
    version='0.0.1',
    install_requires=[
    ],
    packages=[
        'motion.synthetic',
        'utils.viewer',
    ],
    package_data={
        'motion.synthetic': [
            'maps',
            'scenarios',
        ],
        'utils.viewer': [
            'templates',
            'static',
        ],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'run_scenario=utils.scenario:run',
            'viewer=utils.viewer.viewer:main',
        ],
    },
)
