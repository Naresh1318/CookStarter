import database
import numpy as np

from spoonacular_api import SpoonacularAPI

from flask import Flask
from flask_assistant import Assistant, ask, tell


app = Flask(__name__)
assistant = Assistant(app, route='/')

global recipes


@assistant.action("greet")
def greet():
    return ask("Supp yooo")


@assistant.action("startCooking", mapping={"duration": "sys.duration", "people": "sys.cardinal"})
def start_cooking(duration, people, meal_type):
    # Pick the top three recipes for the ingredients list
    global recipes
    keep_recipes = 3
    inventory = list(database.generate_test_inventory().keys())
    spoon = SpoonacularAPI(inventory, _num_recipes=15)
    recipes = spoon.recipes[:keep_recipes]

    synonyms = [['one', 'number one', 'first option'],
                ['two', 'number two', 'second option'],
                ['three', 'number three', 'third option']]

    speech = "Here's what I found {} based on your groceries: ".format(len(recipes))
    for res in recipes:
        speech += res.name

    speech += " Please choose one by telling me the index."

    resp = ask(speech)
    recipes_list = resp.build_list("Recipes")
    for i, rec in enumerate(recipes):
        dec = ""
        for item in list(rec.ingredients):
            dec += str(item) + ","
        recipes_list.add_item(title=rec.name,
                              key=rec.name,
                              img_url=rec.img_url,
                              description=dec,
                              synonyms=synonyms[i])
    return recipes_list


@assistant.action("select", mapping={"option1": "sys.number", "options2": "sys.cardinal", "option3": "sys.ordinal"})
def select_recipe(option1, option2, option3, food):
    print(food)
    if food != "":
        option = food
    elif option1 is not None:
        option = option1
    elif option2 is not None:
        option = option2
    else:
        option = option3

    score = {rec: 0 for rec in recipes}
    for word in food.split(" "):
        for rec in recipes:
            rec_name = set(word.lower() for word in rec.name.split(" "))
            if word.lower() in rec_name:
                score[rec] += 1

    food_chosen = np.argmax(list(score.values()))

    speech = "Okay, here's how you make it. "
    if food == "":
        speech += recipes[int(option)-1].instructions
    else:
        speech += recipes[food_chosen].instructions

    print(recipes[food_chosen].name)
    print(speech)

    return tell(speech)


if __name__ == '__main__':
    app.run()
