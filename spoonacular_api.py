import requests
import json
import pdb

meal_vocab = {
    'breakfast' : 'breakfast',
    'morning meal' : 'breakfast',
    'brunch' : 'brunch',
    'lunch' : 'lunch',
    'noon meal' : 'lunch',
    'enening snack' : 'snack',
    'snack' : 'snack',
    'evening meal' : 'dinner',
    'night meal' : 'dinner',
    'dinner' : 'dinner',
    'supper' : 'dinner',
}

class Recipe:
    def_instruction = 'So, it looks this recipe is rather intuitive! So just be creative!'
    def_total_time = 45
    def_cost = 100.0
    flags = ['vegetarian', 'vegan', 'glutenFree', 'dairyFree', 'ketogenic' ]
    def __init__( self, _idx=None, _name='', _img_url='', _ingredients=list(), _missing=list(), _time=(0, 0, 0), _instructions='',\
                _servings=1, _meal_type=set(), _cost=50.0, _flags_dict=dict()
        ):
        self.idx = _idx
        self.name = _name
        self.img_url = _img_url
        self.ingredients = _ingredients
        self.missing = _missing
        self.servings = _servings
        self.cost = _cost
        self.meal_type = _meal_type
        self.instructions = _instructions
        self.time = _time #(readyInMinutes, #prepTime, cookingTime)
        self.flags_dict = _flags_dict

    def __str__(self):
        return 'Name: {}\nImage URL: {}\nMeal type: {}\nIngredients: {}\nMissing: {}\nServings:{}\nTime required: {} minutes\nInstructions:\n{}'.format( self.name, self.img_url, \
                ', '.join([ str(x) for x in self.meal_type ]), ', '.join([ str(x) for x in self.ingredients ]), \
                 ', '.join([ str(x) for x in self.missing ]), self.servings, sum(self.time), self.instructions )

class Ingredient:
    def __init__(self, _idx=None, _name='', _quantity=0.0, _units=None, _metric_quantity=0.0, _metric_units=None):
        self.idx = _idx
        self.name = _name
        self.quantity = _quantity
        self.units = _units
        # self.metric_quantity = _metric_quantity
        # self.metric_units = _metric_units

    def __str__(self):
        if(self.units and self.quantity):
            return '{} {} of {}'.format( self.quantity, self.units,  self.name ) # + '|' + str(self.idx)
        elif(self.quantity > 0):
            return '{} {}'.format(self.quantity, self.name)
        else:
            return self.name

    def __hash__(self):
        return self.idx

    def __eq__(self, other):
        return self.idx==other.idx

class Equipment:
    def __init__(self, _idx=None, _name=''):
        self.idx = _idx
        self.name = _name

    def __str__(self):
        return self.name # + '|' + str(self.idx)

    def __hash__(self):
        return self.idx

    def __eq__(self, other):
        return self.idx==other.idx

class SpoonacularAPI:
    addr='https://spoonacular-recipe-food-nutrition-v1.p.mashape.com'
    header={
            "X-Mashape-Key": "O8Xwsw9oTemshfMVzGMyqgiOzNZwp1uVBcOjsnJDuVrFfJXW8T",
            "Accept": "application/json"
        }
    def __init__(self, _ingredient_names_list=[], _num_recipes=15):
        self.ingredient_names_list = _ingredient_names_list
        self.num_recipes = _num_recipes
        self.recipes = []

        self.get_recipe_from_ingredients()
        self.update_recipe_data()

    # Find recipes using ingredients
    # Creates Recipe objects using IDs
    # For each recipe, update ingredients, missing ingredients, 
    def get_recipe_from_ingredients(self):
        query_str = "{}/recipes/findByIngredients?fillIngredients=true&ingredients={}&limitLicense=false&number={}&ranking=2".format( SpoonacularAPI.addr, '%2C'.join( self.ingredient_names_list ), self.num_recipes )
        req_response = requests.get(query_str, headers=SpoonacularAPI.header)
        
        req_response = json.loads(req_response.text)
        if(not req_response):
            return

        for trecipe_data in req_response:

            missing = []
            for ttmissing in trecipe_data.get('missedIngredients', []):
                missing.append( Ingredient( _idx=ttmissing['id'], _name=ttmissing['name'], _quantity=ttmissing['amount'], _units=ttmissing['unitShort'] ) )

            used_ingredients = []
            for ttingredient in trecipe_data.get('usedIngredients', []):
                used_ingredients.append( Ingredient( _idx=ttingredient['id'], _name=ttingredient['name'], _quantity=ttingredient['amount'], _units=ttingredient['unitShort'] ) )

            trecipe = Recipe(_idx=trecipe_data['id'], _name=trecipe_data['title'], _img_url=trecipe_data['image'], _ingredients=used_ingredients+missing, _missing=missing )
            self.recipes.append( trecipe )

    # For each "candidate" recipe, add instructions and time data
    def update_recipe_data(self):
        recipe_idxs = '%2C'.join([ str(trecipe.idx) for trecipe in self.recipes ])
        query_str = "{}/recipes/informationBulk?ids={}&includeNutrition=false".format( SpoonacularAPI.addr, recipe_idxs )
        req_response = requests.get(query_str, headers=SpoonacularAPI.header)
        
        req_response = json.loads(req_response.text)
        if(not req_response):
            return

        for tidx, trecipe in enumerate(self.recipes):
            trecipe_data = req_response[tidx]
            trecipe.instructions = trecipe_data.get('instructions', Recipe.def_instruction)
            trecipe.time = tuple([ int(trecipe_data.get('readyInMinutes',0)), int(trecipe_data.get('preparationMinutes',0)), int(trecipe_data.get('cookingMinutes',0)) ])
            trecipe.servings = int(trecipe_data.get('servings', 1))
            trecipe.meal_type = set([ meal_vocab.get(tmeal, 'lunch') for tmeal in trecipe_data.get('dishTypes', ['lunch']) ])
            trecipe.price = float(trecipe_data.get('pricePerServing', Recipe.def_cost))

    def recipes_by_time(self, time_limit=Recipe.def_total_time, recipe_list=None):
        if not recipe_list:
            recipe_list = self.recipes

        return sorted( [ rec  for rec in recipe_list if sum(rec.time) <= time_limit ], key=lambda rec: sum(rec.time), reverse=False )

    def recipes_by_meal_type(self, tmeal_type, recipe_list=None):
        if not recipe_list:
            recipe_list = self.recipes
            
        if(isinstance(tmeal_type, list)):
            tmeal_type = set(tmeal_type)
        elif(isinstance(tmeal_type, str )):
            tmeal_type = set([ tmeal_type ])
        return [ rec  for rec in recipe_list if rec.meal_type.intersection(tmeal_type) ]

    def recipes_by_cost(self, cost_limit=Recipe.def_cost, recipe_list=None):
        if not recipe_list:
            recipe_list = self.recipes

        return sorted( [ rec  for rec in recipe_list if rec.cost <= cost_limit ], key=lambda rec: sum(rec.price), reverse=False )

def main():
    spoon = SpoonacularAPI(['eggs', 'milk', 'flour'])

    tlist = spoon.recipes_by_meal_type('breakfast')
    for trecipe in spoon.recipes_by_time(time_limit=25, recipe_list=tlist):
        print('\n\n')
        print(trecipe)
        print('\n\n')

if __name__ == '__main__':
    main()