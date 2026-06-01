from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'vessel_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', 'vessel_control', 'launch'),
            glob(os.path.join('launch', '*.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='spk',
    maintainer_email='spk@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            #'rudder_control = vessel_control.rudder_control:main',
            #'rudder_client = vessel_control.rudder_client:main'
            #'rudder_control = vessel_control.rudder_control:main',
            #'motor_control = vessel_control.motor_control:main'
            'vessel_control = vessel_control.serial_vessel_control:main',
        ],
    },
)
