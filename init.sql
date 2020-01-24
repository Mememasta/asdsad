


create table groups (
        id serial primary key,
        name varchar(255),
        author_id integer references users(id),
        commander integer references users(id)
        
);

create table users (
        id serial primary key,
        name varchar(255),
        secondname varchar(255),
        email varchar(255),
        phone integer,
        birthday VARCHAR(40),
        occupation varchar(255),
        city varchar(40),
        password VARCHAR(255),
        user_photo VARCHAR(255)

);


create table projects (
        id serial primary key,
        name VARCHAR(255),
        company text,
        author_id integer references users(id),
        description text,
        presentation VARCHAR(255),
        deadline VARCHAR(255),
        member Integer,
        gift text,
        video VARCHAR(255)
);

create table projects_user (
        user_id integer references users(id),
        project_id integer references projects(id)

);

create table groups_user (
        user_id integer references users(id),
        groups_id integer references groups(id)
);
