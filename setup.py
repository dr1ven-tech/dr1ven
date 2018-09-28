from setuptools import setup

setup(
    name='dr1ven',
    version='0.0.1',
    install_requires=[
    ],
    packages=[
        'state',
        'scenarios',
        'motion.synthetic',
    ],
    package_data={
        'state': [
            'static',
        ],
        'motion.synthetic': [
            'maps',
            'scenarios',
        ]
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'state_viewer=state.viewer:main',
            'run_scenario=scenarios.scenario:run',
        ],
    },
)
