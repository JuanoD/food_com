#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from mysql.connector import connect, Error

users = pd.read_csv('PP_users.csv')
for col in ('techniques', 'items', 'ratings'):
    users[col] = users[col].apply(lambda arr: [int(float(x)) for x in str(arr)[1:-1].split(', ')])

pp_recipes = pd.read_csv('PP_recipes.csv').sort_values('id')
raw_recipes = pd.read_csv('RAW_recipes.csv').sort_values('id')

for col in ('tags', 'steps', 'ingredients'):
    raw_recipes[col] = raw_recipes[col].apply(lambda arr: str(arr)[1:-1].split(', '))

raw_recipes['description'] = raw_recipes['description'].fillna('')

pp_recipes['techniques'] = pp_recipes['techniques'].apply(lambda arr: str(arr)[1:-1].split(', '))
pp_recipes['techniques'] = pp_recipes['techniques'].apply(lambda arr: list(map(int, arr)))

interactions = pd.read_csv('RAW_interactions.csv')

# Check max length for database schema
# print(f"""
# Max Length for
# Name: {raw_recipes['name'].apply(lambda x: len(str(x))).max()}
# Description: {raw_recipes['description'].apply(lambda x: len(str(x))).max()}
# Tags: {raw_recipes['tags'].apply(lambda x: max(map(len, x))).max()}
# Steps: {raw_recipes['steps'].apply(lambda x: sum(map(len, x))).max()}
# Ingredients: {raw_recipes['ingredients'].apply(lambda x: max(map(len, x))).max()}
# Review: {interactions['review'].apply(lambda x: len(str(x))).max()}
# """)

db_params = {
    'host': 'db',
    'user': 'root',
    'password': 'example',
    'database': 'food_com'
}

def mysql_many_query(query, params):
    try:
        with connect(**db_params) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, params)
                connection.commit()
                print(f"{cursor.rowcount} rows affected")
    except Error as e:
        print(e)

def mysql_query(query, params):
    try:
        with connect(**db_params) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                connection.commit()
                print(f"{cursor.rowcount} rows affected")
    except Error as e:
        print(e)

# Add user ids. Recipes need user id to be inserted. Comments need user id
mysql_many_query(
    """
    INSERT INTO users
    (pk_user_id)
    VALUES ( %s )
    """,
    [(int(id),) for id in users["u"].values]
)

mysql_many_query(
    """
    INSERT IGNORE INTO users
    (pk_user_id)
    VALUES ( %s )
    """,
    [(int(id),) for id in raw_recipes['contributor_id'].unique()]
)

mysql_many_query(
    """
    INSERT IGNORE INTO users
    (pk_user_id)
    VALUES ( %s )
    """,
    [(int(id),) for id in interactions['user_id'].unique()]
)

# Insert recipes
for i, row in raw_recipes[['id', 'name', 'minutes', 'contributor_id', 'submitted', 'steps', 'description']].iterrows():
    mysql_query(
        """
        INSERT INTO recipes
        (pk_recipe_id, name, minutes, fk_contributor, submitted, steps, description)
        VALUES ( %s, %s, %s, %s, %s, %s, %s )
        """,
        (row['id'], row['name'], row['minutes'], row['contributor_id'], row['submitted'], '\n'.join(''.join(row['steps']).split("''")).replace("'", ""), row['description'])
    )

# Insert user ratings
for i, row in users[['u', 'items', 'ratings']].iterrows():
    mysql_many_query(
        """
        INSERT INTO ratings
        (fk_user_id, fk_recipe_id, rating)
        VALUES ( %s, %s, %s )
        """,
        list(map(lambda x: (row['u'], *x) ,zip(row['items'], row['ratings'])))
    )

# Insert tags
tags = set()
for row in raw_recipes['tags']:
    tags.update(row)
tag_list = []
for tag in tags:
    tag_list.append((tag.replace("'", "").replace('"', ''),)) # this can be fixed erlier, after importing the csv

mysql_many_query(
    """
    INSERT INTO tags
    (name)
    VALUES ( %s )
    """,
    tag_list
)

# Insert recipe tags
for i, row in raw_recipes[['id', 'tags']].iterrows():
    mysql_many_query(
        """
        INSERT INTO recipe_tags
        (fk_recipe_id, fk_tag_id)
        VALUES ( %s, ( SELECT pk_tag_id FROM tags WHERE UPPER(name) = UPPER(%s) ) )
        """,
        list(map(lambda x: (row['id'], x.replace("'", "").replace('"', '')) , row['tags']))  # Doing this earlier avoids computing it twice
    )

# Insert ingredients
ingredients = set()
for row in raw_recipes['ingredients']:
    ingredients.update(row)
ingredients_list = []
for ingredient in ingredients:
    ingredients_list.append((ingredient.replace("'", "").replace('"', ''),))  # Same as tags

mysql_many_query(
    """
    INSERT INTO ingredients
    (name)
    VALUES ( %s )
    """,
    ingredients_list
)

# Insert recipe ingredients
for i, row in raw_recipes[['id', 'ingredients']].iterrows():
    mysql_many_query(
        """
        INSERT INTO recipes_ingredients
        (fk_recipe_id, fk_ingredient_id)
        VALUES ( %s, ( SELECT pk_ingredient_id FROM ingredients WHERE UPPER(name) = UPPER(%s) ) )
        """,
        list(map(lambda x: (row['id'], x.replace("'", "").replace('"', '')) , row['ingredients']))
    )    

# Insert techniques id
# Right now they have no name
# techs = pp_recipes[['id', 'techniques']]
# techs['techniques'] = techs['techniques'].apply(lambda x: len(x))
# techs[techs['techniques'] != 58]
# All rows have 58 techniques
mysql_many_query(
    """
    INSERT INTO techniques
    (pk_technique_id)
    VALUES ( %s )
    """,
    list(map(lambda x: (x,), list(range(58))))
)

# Insert recipes techniques

for i, row in pp_recipes[['id', 'techniques']].iterrows():
    techniques_list = []
    for technique, value in enumerate(row['techniques']):
        if value:
            techniques_list.append((row['id'], technique))
            mysql_many_query(
                """
                INSERT INTO recipes_techniques
                (fk_recipe_id, fk_technique_id)
                VALUES ( %s, %s )
                """,
                techniques_list
            )

for i, row in interactions.iterrows():
    mysql_query(
        """
        INSERT INTO comments
        (fk_user_id, fk_recipe_id, interaction_date, rating, review)
        VALUES ( %s, %s, %s, %s, %s )
        """,
        (row['user_id'], row['recipe_id'], row['date'], row['rating'], row['review'])  # tuple(row) would only work if the order of the columns is the same for every time the script is loaded
    )
