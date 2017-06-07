# Zach's Catalog Project

## Description
For project 4 we needed to make a basic Item Catalog with CRUD functionality. It also included Google Oauth login.  I utilized the Flask framework with SQLAlchemy and PostgreSQL.  In addition, we need to configure an AWS server manually to deploy this application. From the command line I setup SSH, configured the firewall, updated apps, installed apache, and converted the application from Sqlite to PSQL.

I've since taken down the AWS server that hosted this application.

## IP address
NO LONGER ACTIVE:
- IP address for this project is 52.54.182.182
- Alternatively the hostname for the project is ec2-52-54-182-182.compute-1.amazonaws.com

## SSH 
- As mentioned in the Rubric and notes, this can be reached by the user account specified by the Udacity team.
- Port of SSH is setup to 2200

## Software
There was a lot of software installed to setup this project, both for the server and for the specific application here is a list.

### Server:
- Type "apt list --installed" once logged on the server.

Basic List:
- Python 2 and 3
- Apache2
- PostgreSQL
- Pip
- Git
- Virtual ENV

For application:
- bleach==2.0.0
- blinker==1.3
- chardet==2.3.0
- click==6.7
- cloud-init==0.7.9
- command-not-found==0.3
- configobj==5.0.6
- cryptography==1.2.3
- Flask==0.12.2
- Flask-HTTPAuth==3.2.2
- Flask-SQLAlchemy==2.2
- html5lib==0.999999999
- httplib2==0.10.3
- idna==2.0
- itsdangerous==0.24
- Jinja2==2.8
- jsonpatch==1.10
- jsonpointer==1.9
- language-selector==0.1
- MarkupSafe==0.23
- oauth2client==4.1.0
- oauthlib==1.0.3
- packaging==16.8
- passlib==1.7.1
- prettytable==0.7.2
- psycopg2==2.7.1
- pyasn1==0.1.9
- pyasn1-modules==0.0.8
- pycurl==7.43.0
- pygobject==3.20.0
- PyJWT==1.3.0
- pyparsing==2.2.0
- pyserial==3.0.1
- python-apt==1.1.0b1
- python-debian==0.1.27
- python-systemd==231
- PyYAML==3.11
- redis==2.10.5
- requests==2.9.1
- rsa==3.4.2
- six==1.10.0
- SQLAlchemy==1.1.10
- ssh-import-id==5.5
- ufw==0.35
- unattended-upgrades==0.1
- urllib3==1.13.1
- webencodings==0.5.1
- Werkzeug==0.12.2

## Third Party Resources

To complete this project I relied primarily on trial and error, but somewhat on good documentation provided around the web.  Here are the main resources.

- Setting up a flask app on AWS: https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps

- Switching from sqlite to PSQL: http://docs.sqlalchemy.org/en/latest/dialects/postgresql.html

- Fixing Origin_mismatch with Google Oauth: https://discussions.udacity.com/t/almost-there-origin-mismatch/27217

