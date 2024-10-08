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

CREATE TABLE IF NOT EXISTS sprint (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    start_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS workspace (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL
);



CREATE TABLE IF NOT EXISTS user_secret (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_sysgen INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user (id)
);


CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("user_id"),
    FOREIGN KEY("user_id") REFERENCES "user"("id")
);





CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    issue_id INTEGER NULL,

    create_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    title TEXT NOT NULL,
    description TEXT NULL,
    status TEXT NOT NULL,
    priority INT NOT NULL DEFAULT 0,
    
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (issue_id) REFERENCES issue (id)
);




CREATE TABLE IF NOT EXISTS kanban_board (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    description TEXT NULL,
    FOREIGN KEY("user_id") REFERENCES "user"("id")
);


CREATE TABLE IF NOT EXISTS kanban_lane (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kanban_board_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    description TEXT NULL,
	display_order INTEGER DEFAULT 0,
    FOREIGN KEY("kanban_board_id") REFERENCES "kanban_board"("id")
);

CREATE TABLE IF NOT EXISTS kanban_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kanban_lane_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    description TEXT NULL,
	display_order INTEGER DEFAULT 0,
    FOREIGN KEY("kanban_lane_id") REFERENCES "kanban_lane"("id")
);


insert into kanban_board (user_id, title, description) values (1, 'Tasks', 'My tasks')
insert into kanban_lane (kanban_board_id, title, description, display_order) VALUES (1, 'Tasks', 'Available tasks', 1);
insert into kanban_lane (kanban_board_id, title, description, display_order) VALUES (1, 'In Progress', 'Tasks in progress', 2);
insert into kanban_lane (kanban_board_id, title, description, display_order) VALUES (1, 'Testing', 'Completion verification', 3);
insert into kanban_lane (kanban_board_id, title, description, display_order) VALUES (1, 'Done', 'Completed tasks', 4);

insert into kanban_item (kanban_lane_id, title, description, display_order) VALUES 
    (1, 'Task One',  '<p>I am a very simple card. I am good at containing small bits of information.I am convenient because I require little markup to use effectively.</p>', 1);
insert into kanban_item (kanban_lane_id, title, description, display_order) VALUES 
    (1, 'Task Two',  '<p>I am a very simple card. I am good at containing small bits of information.I am convenient because I require little markup to use effectively.</p>', 2);
insert into kanban_item (kanban_lane_id, title, description, display_order) VALUES 
    (1, 'Task Three',  '<p>I am a very simple card. I am good at containing small bits of information.I am convenient because I require little markup to use effectively.</p>', 3);
insert into kanban_item (kanban_lane_id, title, description, display_order) VALUES 
    (1, 'Task Four',  '<p>I am a very simple card. I am good at containing small bits of information.I am convenient because I require little markup to use effectively.</p>', 4);
insert into kanban_item (kanban_lane_id, title, description, display_order) VALUES 
    (1, 'Task Five',  '<p>I am a very simple card. I am good at containing small bits of information.I am convenient because I require little markup to use effectively.</p>', 5);
insert into kanban_item (kanban_lane_id, title, description, display_order) VALUES 
    (1, 'Task Six',  '<p>I am a very simple card. I am good at containing small bits of information.I am convenient because I require little markup to use effectively.</p>', 6);


-- CREATE TABLE IF NOT EXISTS oanda_intrument (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     type TEXT NOT NULL,
--     display_name TEXT NOT NULL,
    
--     user_id INTEGER NOT NULL,
--     update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     is_sysgen INTEGER DEFAULT 0,
--     FOREIGN KEY (user_id) REFERENCES user (id)
-- );

CREATE TABLE IF NOT EXISTS oanda_intrument (
    id INTEGER NOT NULL,
    name TEXT NOT NULL,
    instrument_type_id TEXT NOT NULL,
    display_name TEXT NOT NULL,
    -- pipLocation INTEGER NOT NULL,
    -- minimumTradeSize REAL NOT NULL,
    update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "oanda_intrument_pk_idx" PRIMARY KEY("id" AUTOINCREMENT),
	CONSTRAINT "oanda_intrument_u_idx" UNIQUE("name"),
    FOREIGN KEY ("instrument_type_id") REFERENCES "oanda_intrument_type"("id")
);



CREATE TABLE IF NOT EXISTS oanda_intrument_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    description TEXT NOT NULL
);
INSERT INTO oanda_intrument_type (id, code, description) VALUES (1, 'CURRENCY', 'Currency');
INSERT INTO oanda_intrument_type (id, code, description) VALUES (2, 'CFD', 'Contract For Difference');
INSERT INTO oanda_intrument_type (id, code, description) VALUES (3, 'METAL', 'Metal');


CREATE TABLE IF NOT EXISTS oanda_intrument_tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY ("instrument_id") REFERENCES "oanda_intrument"("id")
);



CREATE TABLE IF NOT EXISTS todo_task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    create_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,    
    description TEXT NULL,
    is_completed INTEGER NOT NULL DEFAULT 0,
    priority INT NOT NULL DEFAULT 0
);
