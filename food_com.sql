CREATE DATABASE food_com CHARACTER SET utf8;
USE food_com;

-- I suppose this data is used to fed a recommendation engine

CREATE TABLE users (
    pk_user_id INT,
    -- Techniques are consulted with user ratings ?
    -- ratings OK
    PRIMARY KEY (pk_user_id)
);

CREATE TABLE recipes (
    pk_recipe_id INT,
    name VARCHAR(100),
    minutes INT,
    fk_contributor INT,
    submitted DATE,
    -- tags OK
    -- techniques OK
    -- nutrition ? Implement as JSON array?
    steps TEXT,
    description TEXT DEFAULT NULL,
    -- ingredients OK
    calorie_level INT,
    PRIMARY KEY (pk_recipe_id),
    FOREIGN KEY (fk_contributor) REFERENCES users (pk_user_id)
);

CREATE TABLE ingredients (
    pk_ingredient_id INT AUTO_INCREMENT,
    name VARCHAR(100),
    PRIMARY KEY (pk_ingredient_id),
    UNIQUE INDEX ( (UPPER(name)) )
);

CREATE TABLE recipes_ingredients (
    fk_recipe_id INT,
    fk_ingredient_id INT,
    FOREIGN KEY (fk_recipe_id) REFERENCES recipes (pk_recipe_id),
    FOREIGN KEY (fk_ingredient_id) REFERENCES ingredients (pk_ingredient_id)
);

CREATE TABLE ratings (
    rating INT,
    fk_user_id INT,
    fk_recipe_id INT,
    FOREIGN KEY (fk_user_id) REFERENCES users (pk_user_id),
    FOREIGN KEY (fk_recipe_id) REFERENCES recipes (pk_recipe_id) ON DELETE CASCADE
);

CREATE TABLE tags (
    pk_tag_id INT,
    name VARCHAR(100),
    PRIMARY KEY (pk_tag_id),
    UNIQUE INDEX ( (UPPER(name)) )
);

CREATE TABLE recipe_tags (
    fk_recipe_id INT,
    fk_tag_id INT,
    FOREIGN KEY (fk_recipe_id) REFERENCES recipes (pk_recipe_id),
    FOREIGN KEY (fk_tag_id) REFERENCES tags (pk_tag_id)
);

CREATE TABLE techniques (
    pk_technique_id INT,
    PRIMARY KEY (pk_technique_id)
);

CREATE TABLE recipes_techniques (
    -- I suposse every recipe has some techniques, the idea is to recommend recipes to users based on techniques they used previously
    fk_recipe_id INT,
    fk_technique_id INT,
    FOREIGN KEY (fk_recipe_id) REFERENCES recipes (pk_recipe_id) ON DELETE CASCADE,
    FOREIGN KEY (fk_technique_id) REFERENCES techniques (pk_technique_id)
);

CREATE TABLE comments (
    fk_user_id INT,
    fk_recipe_id INT,
    interaction_date DATE,
    rating INT, -- Rating could be put into ratings table and this one removed from here, but some ratings are zero. I would ask before doing so
    review TEXT,
    FOREIGN KEY (fk_user_id) REFERENCES users (pk_user_id),
    FOREIGN KEY (fk_recipe_id) REFERENCES recipes (pk_recipe_id)
);