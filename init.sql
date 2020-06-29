DROP TABLE groups_user, answer_user, projects_user, projects, groups, users;

create table users (
        id serial primary key,
        name varchar(255) NOT NULL,
        secondname varchar(255),
        email varchar(255) not null,
        phone bigint,
        birthday VARCHAR(40),
        occupation varchar(255),
        city varchar(40),
        password VARCHAR(255),
        user_photo VARCHAR(255)

);




create table groups (
        id serial primary key,
        name varchar(255),
        author_id integer references users(id),
        commander integer references users(id),
        project_id integer references projects(id)
        
        
);


create table projects (
        id serial primary key,
        name VARCHAR(255) not null,
        company VARCHAR(255) not null,
        author_id integer references users(id) not null,
        description text not null,
        presentation VARCHAR(255),
        deadline timestamptz,
        member Integer,
        gift text not null,
        video VARCHAR(255)
);

create table projects_user (
        user_id integer references users(id),
        project_id integer references projects(id)

);

create table answer_user (
        user_id integer references users(id),
        projects_id integer references projects(id),
        answer VARCHAR(2048) not null
);

create table groups_user (
        user_id integer references users(id),
        groups_id integer references groups(id)
);
