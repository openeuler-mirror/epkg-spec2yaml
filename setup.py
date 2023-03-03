from setuptools import setup, find_packages
from openEulerTransition.configure.__version__ import VERSION

setup(
    name="openEulerTransition",
    version=VERSION,
    packages=find_packages(),
    description="...",
    license="GPL-2.0",
    author="",
    entry_points={
        "console_scripts": [
            'openEulerTransition = openEulerTransitionMain:main'
        ]
    },
    include_package_data=True,
    install_requires=[
        'PyYAML>=3.0,<6',
        'requests>=2.22.0',
        'Cheetah3==3.2.6.post2',
        'logger==1.4',
        'Flask==2.1.2',
        'Flask-Cors==3.0.10',
        'Flask-Pydantic==0.9.0',
        'Flask-RESTful==0.3.9',
        'Flask-Script==2.0.6',
        'kconfiglib==14.1.0',
        'iniconfig==1.1.1',
        'configobj==5.0.6',
    ],
    data_files=[
        ("", ["openEulerTransition/../openEulerTransitionMain.py"]),
    ],
)
