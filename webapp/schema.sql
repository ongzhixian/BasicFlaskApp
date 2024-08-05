-- DROP TABLE IF EXISTS user;
-- DROP TABLE IF EXISTS post;
-- DROP TABLE IF EXISTS tool;

CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS tool (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    create_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name TEXT NOT NULL,
    description TEXT NULL,
    url TEXT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);


CREATE TABLE IF NOT EXISTS role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT NULL
);

CREATE TABLE IF NOT EXISTS user_role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
    FOREIGN KEY (role_id) REFERENCES role (id)
);



CREATE TABLE IF NOT EXISTS note (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    create_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NULL,  
    FOREIGN KEY (user_id) REFERENCES user (id)
);



CREATE TABLE IF NOT EXISTS blog_post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    create_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS issue_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    weight INTEGER NOT NULL
);
INSERT INTO issue_type (title, weight) VALUES ('Bug', 9);
INSERT INTO issue_type (title, weight) VALUES ('Feature', 6);
INSERT INTO issue_type (title, weight) VALUES ('Enhancement', 6);

CREATE TABLE IF NOT EXISTS issue_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    weight INTEGER NOT NULL
);
INSERT INTO issue_status (title, weight) VALUES ('New', 9);
INSERT INTO issue_status (title, weight) VALUES ('Assigned', 6);
INSERT INTO issue_status (title, weight) VALUES ('Closed', 1);
INSERT INTO issue_status (title, weight) VALUES ('Shelved', 3);

CREATE TABLE IF NOT EXISTS issue_priority (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    weight INTEGER NOT NULL
);
INSERT INTO issue_priority (title, weight) VALUES ('High', 9);
INSERT INTO issue_priority (title, weight) VALUES ('Medium', 6);
INSERT INTO issue_priority (title, weight) VALUES ('Low', 3);
INSERT INTO issue_priority (title, weight) VALUES ('Backlog', 1);



CREATE TABLE IF NOT EXISTS issue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    create_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    type_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NULL,
    status_id INTEGER NOT NULL,
    priority_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (type_id) REFERENCES issue_type (id),
    FOREIGN KEY (status_id) REFERENCES issue_status (id)
    FOREIGN KEY (priority_id) REFERENCES issue_priority (id)
);


CREATE TABLE IF NOT EXISTS url (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    create_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    href TEXT NOT NULL,
    status INTEGER DEFAULT 0
);



CREATE TABLE IF NOT EXISTS fixed_deposit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    create_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    company_name TEXT NOT NULL,
    interest_per_annum REAL NOT NULL,
    tenure TEXT NOT NULL,
    remarks TEXT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);


CREATE TABLE IF NOT EXISTS topic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS bank (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL
);
