from setuptools import setup

setup(
    name='dr1ven',
    version='0.0.1',
    install_requires=[
    ],
    packages=[
        'perception.bbox',
        'perception.bbox.yolov3',
        'planning',
        'planning.agents',
        'planning.synthetic',
        'planning.synthetic.entities',
        'state',
        'utils',
        'utils.viewer',
    ],
    package_data={
        'planning.synthetic': [
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
            'test_yolov3=perception.bbox.yolov3.yolov3:main',
        ],
    },
)
