from setuptools import setup

setup(name='cbpi4-ctrl-ferm',
      version='0.0.1',
      description='CraftBeerPi plugin for PID controlled fermentation',
      author='Mikael Karlsson',
      author_email='rmkarlsson@protnmail.ch',
      url='',
      license='GPLv3',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4-ctrl-ferm': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4-ctrl-ferm'],
     )