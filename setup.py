from distutils.core import setup
setup(
  name = 'MediPlot',
  packages = ['MediPlot'],
  version = '0.1',
  license='MIT',
  description = 'A matplotlib based library for anatomical plots',
  author = 'Thomas Konstantinovsky',
  author_email = 'thomaskon90@gmail.com',
  url = 'https://github.com/MuteJester/MediPlot',
  download_url = 'https://github.com/MuteJester/MediPlot/archive/v_0.1.tar.gz',    # I explain this later on
  keywords = ['datascience', 'data visualization', 'matplotlib'],
  install_requires=[
          'matplotlib',
          'numpy',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
  ],
)
