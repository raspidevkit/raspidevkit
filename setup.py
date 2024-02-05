import setuptools

setuptools.setup(
    name="raspidevkit",
    description="Easily control devices with Raspberry Pi",
    version="0.0.1",
    url="https://github.com/raspidevkit/raspidevkit",
    author="DailyLollipops",
    author_email="clarencemadrigal84@gmail.com",
    package_dir={"raspidevkit": "raspidevkit"},
    packages=setuptools.find_namespace_packages(where="src"),
    include_package_data=True,
    install_requires=['fake-rpi', 
                      'pyserial', 
                      'setuptools', 
                      'smbus2'
                      'wheel']
)
