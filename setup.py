import setuptools

setuptools.setup(
    name="raspidevkit",
    description="Easily control devices with Raspberry Pi",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    version="0.0.2",
    url="https://github.com/raspidevkit/raspidevkit",
    author="DailyLollipops",
    author_email="clarencemadrigal84@gmail.com",
    packages=setuptools.find_namespace_packages(),
    include_package_data=True,
    install_requires=['fake-rpi', 
                      'pyserial', 
                      'setuptools', 
                      'smbus2',
                      'wheel']
)
