import requests
import json


class Recipe:
    def __init__(self, _idx=None, _name='', _ingredients=set(), _equipment=set(), _instructions=[]):
        self.idx = _idx
        self.name = _name
        self.ingredients = _ingredients
        self.equipment = _equipment
        self.instructions = _instructions

    def get_instructions(self):
        return tuple(self.instructions)

    def get_equipment(self):
        return tuple(self.equipment)

    def get_ingredients(self):
        return tuple(self.ingredients)

    def __str__(self):
        return 'Name: {}\nIngredients: {}\nEquipment: {}\nInstructions:\n - {}'.format(self.name, \
                                                                                       ', '.join([str(x) for x in
                                                                                                  self.ingredients]),
                                                                                       ', '.join([str(x) for x in
                                                                                                  self.equipment]),
                                                                                       '\n - '.join(self.instructions))


class Ingredient:
    def __init__(self, _idx=None, _name=''):
        self.idx = _idx
        self.name = _name

    def __str__(self):
        return self.name  # + '|' + str(self.idx)

    def __hash__(self):
        return self.idx

    def __eq__(self, other):
        return self.idx == other.idx


class Equipment:
    def __init__(self, _idx=None, _name=''):
        self.idx = _idx
        self.name = _name

    def __str__(self):
        return self.name  # + '|' + str(self.idx)

    def __hash__(self):
        return self.idx

    def __eq__(self, other):
        return self.idx == other.idx


class SpoonacularAPI:
    addr = 'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com'
    header = {
        "X-Mashape-Key": "MfUQVvnAoUmshdYVYOjWPeP2db45p1IHVodjsnpLYMPqeE5gfW",
        "Accept": "application/json"
    }

    def __init__(self, _ingredient_names_list=[], _num_recipes=5):
        self.ingredient_names_list = _ingredient_names_list
        self.num_recipes = _num_recipes
        self.recipes = []

        self.get_recipe_idx_from_ingredients()
        self.update_recipe_data()

    # Find recipes using ingredients
    # Creates Recipe objects using IDs
    def get_recipe_idx_from_ingredients(self):
        query_str = "{}/recipes/findByIngredients?fillIngredients=false&ingredients={}" \
                    "&limitLicense=false&number={}&ranking=1".format(
            SpoonacularAPI.addr, '%2C'.join(self.ingredient_names_list), self.num_recipes)
        req_response = requests.get(query_str, headers=SpoonacularAPI.header)

        req_response = json.loads(req_response.text)
        self.recipes = [Recipe(_idx=int(trecipe['id']), _name=trecipe['title']) for trecipe in req_response]

    # For each "candidate" recipe, add instructions, ingredients and equipment
    def update_recipe_data(self):
        for trecipe in self.recipes:
            query_str = "{}/recipes/{}/analyzedInstructions?stepBreakdown=true".format(SpoonacularAPI.addr, trecipe.idx)
            req_response = requests.get(query_str, headers=SpoonacularAPI.header)

            req_response = json.loads(req_response.text)
            if req_response:
                req_response = req_response[0]
                trecipe.instructions = tuple([tstep['step'] for tstep in req_response['steps']])

                for tstep in req_response['steps']:
                    if 'ingredients' in tstep:
                        for ttingredient in tstep['ingredients']:
                            trecipe.ingredients.update(
                                {Ingredient(_idx=int(ttingredient['id']), _name=ttingredient['name'])})
                    if 'equipment' in tstep:
                        for ttequipment in tstep['equipment']:
                            trecipe.equipment.update(
                                {Equipment(_idx=int(ttequipment['id']), _name=ttequipment['name'])})

    # TODO: find the best match among returned ingredients
    # Dummy function for now
    def match_ingredient_data(self, ingredient_name):
        return self.ingredient_name_search(ingredient_name)[0]

    def ingredient_name_search(self, ingredient_name):
        query_str = "{}/food/ingredients/autocomplete?metaInformation=false&number=10&query={}".format(
            SpoonacularAPI.addr, ingredient_name)
        req_response = requests.get(query_str, headers=SpoonacularAPI.header)
        return [trecord['name'] for trecord in json.loads(req_response.text)]


def main():
    spoon = SpoonacularAPI(['eggs', 'milk', 'flour'])

    for trecipe in spoon.recipes:
        print('\n\n')
        print(trecipe)
        print('\n\n')


if __name__ == '__main__':
    main()
