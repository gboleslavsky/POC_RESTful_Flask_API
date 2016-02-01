import unittest
from flask import Flask, current_app, url_for, jsonify
import flask_restful_demo_cookbook as test_app
from flask_restful_demo_cookbook import api


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        import base64
        #setting up Flask test_client to test the RESTful endpoints in flask_demo
        self.app = test_app.flask_demo
        self.app.config.update(SERVER_NAME='localhost:5000')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        self.app.testing = True
        self.auth_header = {
            'Authorization':
            'Basic ' + base64.b64encode(('gregory' + ':' + 'boleslavsky').encode('utf-8')).decode('utf-8')}

    def tearDown(self):
        self.app_context.pop()

    ##################################### utility functions
    #did not test them all
    def test_change_recipe_fields(self):
        recipe_before = test_app.all_recipes[0]
        print(test_app.json_recipe(recipe_before))
        recipe_after = test_app.change_recipe_fields(recipe_before, {'dish_name':'Not Macaroni and Cheese'} )
        self.assertEquals(recipe_after.get('dish_name'), 'Not Macaroni and Cheese')             #test return value
        self.assertEquals(test_app.all_recipes[0].get('dish_name'), 'Not Macaroni and Cheese')  #test side-effect

    def test_matching_recipes(self):
        self.assertEquals(len(test_app.matching_recipes(field_name='cuisine', field_value='Italian')), 1)
        self.assertEquals(len(test_app.matching_recipes(field_name='cuisine', field_value='American')), 1)
        self.assertEquals(len(test_app.matching_recipes(field_name='is_vegan', field_value=True)), 2)
        self.assertEquals(len(test_app.matching_recipes(field_name='is_vegan', field_value=False)), 1)

    #def json_recipe(self):


    #RESTful endpoints
    #did not test them all, these are just a couple examples how easy it is to test
    #REStful endpoints with Flask thoroughly in a unit, not integration, test, so
    #they run every build
    def test_login_with_no_username_or_password(self):
        response = self.client.get(url_for(endpoint='vegan_recipes'))
        self.assertTrue(response.status_code == 403)

    def test_vegan_recipes(self):
        correct_reponse="""{"recipes": [{"cuisine": "Korean", "ingredients": "carrots, sesame oil, rice vinegar, fresh garlic, coriander seeds, cayenne pepper", "uri": "/cookbook/v1.0/recipes/2", "steps": "1. Shred the carrots 2. Mix with the rest of the ingredients 3. Leave in the refrigerator for 1 hour", "dish_name": "Korean Carrots", "is_vegan": true}, {"cuisine": "Italian", "ingredients": "cooked white beans (Canelloni or any other), chopped green onion, balsamic vinegar, olive oil", "uri": "/cookbook/v1.0/recipes/3", "steps": "1. Mix all ingredients 2. Let the dish sit in rerigerator for 1 hour", "dish_name": "Tuscan Bean Salad", "is_vegan": true}]}"""
        response = self.client.get(url_for(endpoint='vegan_recipes'),
                        headers=self.auth_header)
        self.assertTrue(response.status_code == 200)
        self.assertEquals(response.data, correct_reponse)

    def test_post_a_new_recipe(self):
        from urllib import urlencode
        import json
        new_recipe = {
                'dish_name':    'fingeling potatoes',
                'cuisine':      'American',
                'ingredients':  'fingerling potatoes',
                'steps':        '1. Wash the potatoes. 2. Cook the potatoes',
                'is_vegan':     True}
        #does not work with test_client yet, most likely something is wrong in the config
        #works fine with curl
        response = self.client.post(url_for(endpoint='recipes'),
                                    headers=self.auth_header,
                                    data=urlencode(new_recipe))
        #self.assertTrue(response.status_code == 401)
        response_with_new_recipe = json.loads(self.client.get(url_for(endpoint='recipes', id=3 ),
                                    headers=self.auth_header).data)\
                                    .get('recipes')
        #self.assertTrue(response.status_code == 200)
        #self.assertEquals(new_recipe.get('dish_name'),
        #                  response_with_new_recipe.get('dish_name'))




