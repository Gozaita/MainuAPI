from distutils.core import setup

setup(name='mainU',
      version='1.0',
      description='@description',
      author='@authors',
      author_email='dev@mainu.eus',
      url='https://www.mainu.eus/',
      install_requires=[
            "requests",
            "sqlalchemy",
            "mysqlclient",
            "flask",
            "simplejson",
            "google-auth",
            "Flask-HTTPAuth",
            "flask_httpauth",
      ],
     )