



CREATE DATABASE projet3 CHARACTER SET 'utf8';
-- for SQLite3
-- in bash: sqlite3 projet3.db


CREATE TABLE population(
    code_pays INT,
    pays VARCHAR (30),
    annee DATE,
    population INT,
    CONSTRAINT pk_population PRIMARY KEY (code_pays)
    );


CREATE TABLE dispo_alim(
    pays VARCHAR (30),
    code_pays INT,
    annee DATE,
    produit VARCHAR (30),
    code_produit INT,
    origin VARCHAR (10),
    dispo_alim_kcal_p_j FLOAT,
    dispo_mat_gr FLOAT,
    dispo_prot FLOAT,
    dispo_alim_tonnes INT
    CONSTRAINT pk_dispo_alim PRIMARY KEY (code_pays, code_produit)
    );


CREATE TABLE equilibre_prod(
    pays VARCHAR (30),
    code_pays INT,
    annee DATE,
    produit VARCHAR (30),
    code_produit INT,
    alim_ani INT,
    autres_utilisations INT,
    dispo_int INT,
    nourriture INT,
    pertes INT,
    semences INT,
    transfo INT,
    CONSTRAINT pk_equilibre_prod PRIMARY KEY (code_pays, code_produit)
    );

CREATE TABLE sous_nutrition(
    code_pays INT,
    pays VARCHAR (30),
    annee DATE,
    nb_personnes INT,
    CONSTRAINT pk_sous_nutrition PRIMARY KEY (code_pays)
    );



