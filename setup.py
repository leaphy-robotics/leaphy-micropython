import setuptools


setuptools.setup(name='leaphy-extensions-rp2040',
                 version='1.0.0',
                 description='Python Package Boilerplate',
                 long_description=open('README.md').read().strip(),
                 author='Leaphy Robotics',
                 author_email='koen@leaphy.nl',
                 url='',
                 install_requires=["machine"],
                 license='MIT License',
                 zip_safe=False,
                 keywords='micropython package',
                 classifiers=['Packages', 'MicroPython'])