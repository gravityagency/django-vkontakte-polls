from setuptools import setup, find_packages

setup(
    name='django-vkontakte-polls',
    version=__import__('vkontakte_polls').__version__,
    description='Django implementation for vkontakte API Polls',
    long_description=open('README.md').read(),
    author='ramusus',
    author_email='ramusus@gmail.com',
    url='https://github.com/ramusus/django-vkontakte-polls',
    download_url='http://pypi.python.org/pypi/django-vkontakte-polls',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False, # because we're including media that Django needs
    install_requires=[
        'django-vkontakte-api>=0.4.5',
        'django-vkontakte-users>=0.3.2',
        'django-vkontakte-groups>=0.3.0',
        'django-vkontakte-wall>=0.3.10',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
