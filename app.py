import random
import database

from spoonacular_api import SpoonacularAPI

from flask import Flask
from flask_assistant import Assistant, ask, tell, build_item


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
    keep_items = 3
    recipes = []
    for i in range(3):
        inventory = list(database.generate_test_inventory().keys())
        random.shuffle(inventory)
        spoon = SpoonacularAPI(inventory[:keep_items])
        recipes.append(spoon.recipes[0])

    synonyms = [['one', 'number one', 'first option'],
                ['two', 'number two', 'second option'],
                ['three', 'number three', 'third option']]

    speech = "I found {} recipes for you: ".format(len(recipes))
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
                              img_url="http://example.com/image1.png",
                              description=dec,
                              synonyms=synonyms[i])
    return recipes_list


@assistant.action("select", mapping={"option1": "sys.number", "options2": "sys.cardinal", "option3": "sys.ordinal"})
def select_recipe(option1, option2, option3):
    if option1 is not None:
        option = option1
    elif option2 is not None:
        option = option2
    else:
        option = option3
    speech = "Okay, here's how you make it "
    instruction = ""
    for i, inst in enumerate(recipes[int(option)-1].instructions):
        instruction += "{}: {}".format(i, inst)
    speech += instruction
    print(speech)
    return tell(speech)


if __name__ == '__main__':
    app.run()
