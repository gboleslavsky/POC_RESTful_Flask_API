#!flask/bin/python
from flask import Flask, jsonify, abort, make_response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth

####################################### global reusable functions, static data and constants
flask_demo = Flask(__name__)
api = Api(flask_demo)
auth = HTTPBasicAuth()


all_recipes = [
    {
        'unique_id': 1,
        'dish_name': 'Macaroni and Cheese',
        'cuisine': 'American',
        'ingredients': 'any small size pasta, cheese that melts well',
        'steps': '1. Cook the pasta 2. Shred the cheese 3. Mixed cooked pasta and shredded cheese ' +
                 '4. Heat on a stove till cheese is melted or microwave for 2 minutes',
        'is_vegan': False
    },
    {
        'unique_id': 2,
        'dish_name': 'Korean Carrots',
        'cuisine': 'Korean',
        'ingredients': 'carrots, sesame oil, rice vinegar, fresh garlic, coriander seeds, cayenne pepper',
        'steps': '1. Shred the carrots 2. Mix with the rest of the ingredients '
                 '3. Leave in the refrigerator for 1 hour',
        'is_vegan': True
    },
    {
        'unique_id': 3,
        'dish_name': 'Tuscan Bean Salad',
        'cuisine': 'Italian',
        'ingredients': 'cooked white beans (Canelloni or any other), chopped green onion, balsamic vinegar, olive oil',
        'steps': '1. Mix all ingredients 2. Let the dish sit in rerigerator for 1 hour',
        'is_vegan': True
    },
]

recipe_fields = {
    'dish_name': fields.String,
    'cuisine': fields.String,
    'ingredients': fields.String,
    'steps': fields.String,
    'is_vegan': fields.Boolean,
    'uri': fields.Url('recipe')  # Flask-RESTful dead simple way to construct a HATEOAS link
}


def recipe_validator():
    request_parser = reqparse.RequestParser()
    # define fields for the parser so it can validate them
    request_parser.add_argument('dish_name',
                                type=str,
                                required=True,
                                help='Please provide the name of the dish')
    request_parser.add_argument('cuisine',
                                type=str,
                                default="")
    request_parser.add_argument('ingredients',
                                type=str,
                                required=True,
                                help='Please provide the list of ingredients')
    request_parser.add_argument('steps',
                                type=str,
                                required=True,
                                help='Please provide the steps for preparing the recipe')
    request_parser.add_argument('is_vegan',
                                type=bool,
                                required=False,
                                help='Please provide the steps for preparing the recipe')
    return request_parser


####################################### utilities
# security  callbacks
@auth.get_password
def password(username):
    # in a real app, either hit a directory server or a DB with encrypted pws
    passwords = {
        'gregory': 'boleslavsky',
        'test': 'pw'
    }
    return passwords.get(username, None)


@auth.error_handler
def wrong_credentials():
    return make_response(jsonify({'message': 'Wrong username or password'}),
                         403)  # 401 makes browsers pop an auth dialog


# reusable functions
def matching_recipes(field_name, field_value):
    return [recipe for recipe in all_recipes if recipe[field_name] == field_value]


def recipe_with_unique_id(unique_id):
    recipes = matching_recipes(field_name='unique_id', field_value=unique_id)
    if recipes:
        return recipes[0]


def change_recipe_fields(recipe, field_names_and_new_values):
    for field_name, new_value in field_names_and_new_values.items():
        if new_value:
            recipe[field_name] = new_value
    return recipe  # for convenience and to facilitate fluent or compositonal style


def json_recipes(recipes):
    return {'recipes': [marshal(recipe, recipe_fields) for recipe in recipes]}


def json_recipe(recipe):
    return {'recipe': marshal(recipe, recipe_fields)}


####################################### request handlers
class ItalianRecipes(Resource):
    """
    Italian food is very popular and deserves its own URL
    """
    decorators = [auth.login_required]  # just decorating with @auth.login_required does not work anymore

    def __init__(self):
        super(ItalianRecipes, self).__init__()

    def get(self):
        recipes = matching_recipes(field_name='cuisine', field_value='Italian')
        if not recipes:
            abort(404)
        return json_recipes(recipes)


class VeganRecipes(Resource):
    """
    Vegan food is getting popular and deserves its own URL
    """
    decorators = [auth.login_required]  # just decorating with @auth.login_required does not work anymore

    def __init__(self):
        super(VeganRecipes, self).__init__()

    def get(self):
        recipes = matching_recipes(field_name='is_vegan', field_value=True)
        if not recipes:
            abort(404)
        return json_recipes(recipes)


class SpecificRecipeAPI(Resource):
    decorators = [auth.login_required]  # just decorating with @auth.login_required does not work anymore

    def __init__(self):
        self.request_parser = recipe_validator()
        super(SpecificRecipeAPI, self).__init__()

    def get(self, unique_id):
        recipe = recipe_with_unique_id(unique_id)
        if not recipe:
            abort(404)
        return json_recipe(recipe)

    def put(self, unique_id):
        recipe = recipe_with_unique_id(unique_id)
        if not recipe:
            abort(404)
        fields_to_change = self.request_parser.parse_args()
        recipe = change_recipe_fields(recipe, fields_to_change)
        return json_recipe(recipe)

    def delete(self, unique_id):
        recipe_to_remove = recipe_with_unique_id(unique_id)
        if not recipe_to_remove:
            abort(404)
        all_recipes.remove(recipe_to_remove)
        return {'result': True}


class AllRestfulRecipesAPI(Resource):
    decorators = [auth.login_required]  # just decorating with @auth.login_required does not work anymore

    def __init__(self):
        self.request_parser = recipe_validator()
        super(AllRestfulRecipesAPI, self).__init__()

    def get(self):
        return json_recipes(all_recipes)

    def unique_id(self):
        if not all_recipes:
            return 1
        else:
            return all_recipes[-1]['unique_id'] + 1  # one more than the largest unique_id, which is
            # always found in the last recipe

    def post(self):

        args = self.request_parser.parse_args()  # parses and validates
        recipe = {
            'unique_id': self.unique_id(),
            'dish_name': args['dish_name'],
            'cuisine': args['cuisine'],
            'ingredients': args['ingredients'],
            'steps': args['steps'],
            'is_vegan': args['is_vegan']
        }
        all_recipes.append(recipe)
        return json_recipe(recipe), 201


api.add_resource(ItalianRecipes, '/cookbook/v1.0/recipes/italian', endpoint='italian_recipes')
api.add_resource(VeganRecipes, '/cookbook/v1.0/recipes/vegan', endpoint='vegan_recipes')
api.add_resource(SpecificRecipeAPI, '/cookbook/v1.0/recipes/<int:unique_id>', endpoint='recipe')
api.add_resource(AllRestfulRecipesAPI, '/cookbook/v1.0/recipes', endpoint='recipes')

if __name__ == '__main__':
    flask_demo.run()
