from setuptools import find_packages, setup

package_name = 'xros_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='spk',
    maintainer_email='spk@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            #'rudder_control = vessel_control.rudder_control:main',
            #'rudder_client = vessel_control.rudder_client:main'
            #'rudder_control = vessel_control.rudder_control:main',
            #'motor_control = vessel_control.motor_control:main'
            'vessel_control = xros_control.vessel_control:main',
            'mode_node = xros_control.mode:main',
            'manual_operation_node = xros_control.manual_operation_mode:main',
        ],
    },
)
