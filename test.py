import requests

addr='https://spoonacular-recipe-food-nutrition-v1.p.mashape.com'
header={
        "X-Mashape-Key": "O8Xwsw9oTemshfMVzGMyqgiOzNZwp1uVBcOjsnJDuVrFfJXW8T",
        "Accept": "application/json"
    }

# Bulk query - Recipe data
# idx = ['556470', '47950', '534573']
# query_str = "{}/recipes/informationBulk?ids={}&includeNutrition=false".format( addr, '%2C'.join(idx) )


# Search recipes by ingredients
ingredient_names_list = ['bread', 'flour', 'sugar', 'eggs', 'apples']
num_recipes = 10
query_str = "{}/recipes/findByIngredients?fillIngredients=true&ingredients={}&limitLicense=false&number={}&ranking=2".format( addr, '%2C'.join( ingredient_names_list ), num_recipes )

print(query_str, '\n\n')

req_response = requests.get(query_str, headers=header)

print(req_response.text)