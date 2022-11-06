import os
from setuptools import setup

# if you are not using vagrant, just delete os.link directly,
# The hard link only saves a little disk space, so you should not care
if os.environ.get('USER', '') == 'vagrant':
    del os.link

try:
    with open('README.txt') as file:
        long_description = file.read()
except Exception:
    long_description = "Dot notation object."

setup(name='dotobject',
      version='1.3.1',
      description='Dot notation object',
      url='https://github.com/seperman/dotobject',
      download_url='https://github.com/seperman/dotobject/tarball/master',
      author='Seperman',
      author_email='sep@zepworks.com',
      license='MIT',
      packages=['dot'],
      zip_safe=False,
      long_description=long_description,
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Topic :: Software Development",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License"
      ],
      )
