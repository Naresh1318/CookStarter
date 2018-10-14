import random
import database

from spoonacular_api import SpoonacularAPI

from flask import Flask
from flask_assistant import Assistant, ask, tell


app = Flask(__name__)
assistant = Assistant(app, route='/')


@assistant.action("greet")
def greet():
    return ask("Supp yooo")


@assistant.action("startCooking", mapping={"duration": "sys.duration", "people": "sys.cardinal"})
def start_cooking(duration, people, meal_type):
    # Pick the top three recipes for the ingredients list
    keep_items = 3
    recipes = []
    for i in range(3):
        inventory = list(database.generate_test_inventory().keys())
        random.shuffle(inventory)
        spoon = SpoonacularAPI(inventory[:keep_items])
        recipes.append(spoon.recipes[0])

    speech = "I found {} recipes for you: ".format(len(recipes))
    for rec in recipes:
        speech += rec.name + ", "

    speech = speech[:-2]

    return tell("Yoooo, " + speech)


if __name__ == '__main__':
    app.run()
