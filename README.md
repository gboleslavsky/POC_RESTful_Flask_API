a small POC demo of a RESTful API using Flask, Flask-RESTful and Flask-HttpAuth
no DB but includes basic security and data validation

To run:


1. './setup.sh'


2. 'python flask_restful_demo_cookbook.py'
that starts the server, once started, curl is to be used for testing like so:

to get some vegan recipes,
'curl  -u test:pw -i http://localhost:5000/cookbook/v1.0/recipes/vegan'

to get a specific recipe,
'curl  -u test:pw -i http://localhost:5000/cookbook/v1.0/recipes/1'

to get all recipes,
'curl  -u test:pw -i http://localhost:5000/cookbook/v1.0/recipes'


to add a new recipe:
'curl -d "cuisine=American&ingredients=fingerling+potatoes&steps=1.+Wash+the+potatoes.+2%2C+C_name=fingerling+potatoes" -u test:pw -i http://localhost:5000/cookbook/v1.0/recipes'



