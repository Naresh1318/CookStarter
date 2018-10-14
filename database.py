import numpy as np


DICTIONARY_FILE = "./user_inventory.pkl"


def sample_inventory():
    pass


def generate_test_inventory():
    inventory = ["milk", "eggs", "wine", "bread", "butter", "cheese", "yogurt", "cream", "tomato",
                 "potato", "beans", "onions", "okra", "chicken", "beef", "pork", "salt", "sausage",
                 "apples", "water", "flour", "rice", "vinegar"]
    df = {item: np.random.randint(1, 10) for item in inventory}
    return df

