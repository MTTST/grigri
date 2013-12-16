from distutils.core import setup

setup(
    name='grigri',
    version='0.02a',
    description='Extra tools and utilities for doing data analysis with numpy, pandas, etc.',
    url='http://github.com/jephdo/grigri/',
    author='Jeph Do',
    author_email='jephdo@gmail.com',
    packages=[
        'grigri', 
        'grigri.dates', 
        'grigri.io',
    ],
    # install_requires=[
    #     'numpy>=1.7.1',
    #     'pandas>=0.12.0',
    #     'ujson>=1.33',
    #     'python-dateutil>=2.2'
    # ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)