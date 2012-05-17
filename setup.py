from setuptools import setup, find_packages

tests_require = [
    'Django>=1.2,<1.5',
    'nose',
    'django-nose',
]
install_requires = []

setup(
    name='django-refinery',
    version='0.1',
    description='Django-refinery is a reusable Django application for allowing users to filter queryset dynamically.',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    license='BSD',
    author='Jacob Radford',
    author_email='nkryptic@gmail.com',
    url='http://github.com/nkryptic/django-refinery',
    packages=find_packages(exclude=["example_project", "tests"]),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='runtests.runtests',
    include_package_data=True,
)

