products = [
    {"name": "tv", "price": 100, "stock": 3},
    {"name": "pc", "price": 120, "stock": 2},
    {"name": "mobile", "price": 80, "stock": 5},
    {"name": "tablette", "price": 120, "stock": 4}
]
products_tries = sorted(products, key=lambda p: (p['price'], -p['stock']))
print(products_tries)


numbers = [1, 2, 3, 4, 5, -1, -3, 7]
positive_numbers = list(filter(lambda x: x > 0, numbers))
positive_numbers_cube = list(map(lambda x: x**3, positive_numbers))
print(positive_numbers)
print(positive_numbers_cube)