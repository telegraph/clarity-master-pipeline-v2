from setuptools import setup, find_packages
from clarityPublisherJob import version

setup(
    name='clarityPublisherJob',
    version=version.__version__,
    description='clarityPublisherJob',
    author='Data Platform team',
    author_email='data.platform@telegraph.co.uk',
    url='https://www.telegraph.co.uk/',
    packages=find_packages(exclude=["doc*", "tests*"]),
    include_package_data=True,
    package_data={
        'clarityPublisherJob': [
            'config/*',
            'schema/*'
            'queries/*'
        ]
    },
    install_requires=[
        'PyYAML==5.1',
        'tmg-etl-library==1.2.4',
        'click'
    ],
    entry_points='''
       [console_scripts]
      clarityPublisherJob=clarityPublisherJob.pipeline:run
     query-debug=clarityPublisherJob.query_debug:query_debug
     ''',
    test_suite="tests"
)
