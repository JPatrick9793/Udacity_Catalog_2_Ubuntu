# Udacity_Catalog_2
**Part of the Udacity Fullstack Nanodegree program. Credit goes to Udacity for certain code segments and methods derived therein.

<em>Welcome to the Catalog website!</em>

Using this repository, you can access a client-side website which allows you to create categories, and items for those categories. Categories and assocated Items have CRUD functionality (they can be Created, Read, Updated, and Destroyed). This site uses google OAuth2.0 as a third party authenticator, so you must either create or possess a google account in order to register as a user for this site.

<b>::::SETTING UP::::</b>

The site should be run using the following configuration:
<ul>
<li>python (V 2.7.12) <a href="https://www.python.org/downloads/">Download</a></li>
<li><a href="http://flask.pocoo.org/docs/0.12/">Flask</a> (V 0.9)</li>
<li><a href="http://docs.sqlalchemy.org/en/rel_1_1/">SQLAlchemy</a> (V1.1.13)</li>
</ul>

Flask and sqlalchemy can be downloaded using the pip command from the python terminal:

$  pip install -Iv Flask==0.9
<br>
$  pip install -Iv sqlalchemy==1.1.13

**Note: you may need to install certain packages seperately. If you are having trouble running the program, try entering the following commands in the terminal:

$  pip install flask packaging oauth2client redis passlib flask-httpauth
<br>
$  pip install sqlalchemy flask-sqlalchemy psycopg2 bleach requests

<b>::::TO RUN THE PROGRAM::::</b>
<ol>
<li>Open the terminal and navigate to the catalog_2 folder</li>
<li>Enter the following command in the prompt line:<br>$  python server.py</li>
<li>Open your browser and visit the following url:<br>http://localhost:8000/</li>
<li>Sign in using a google account (Create one if necessary)</li>
<li>Enjoy!</li>
</ol>

