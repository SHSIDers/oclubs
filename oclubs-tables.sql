CREATE TABLE user (
	user_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	user_login_name varchar(255) binary NOT NULL,
	user_nick_name varchar(255) binary NOT NULL,
	user_password tinyblob NOT NULL,
	user_email tinytext NOT NULL,
	user_type int NOT NULL, # 0=student 1=teacher 2=admin
	user_grad_year int # NULL for teachers
);

CREATE UNIQUE INDEX user_login_name ON user (user_login_name);

CREATE TABLE club_access (
	ca_club int NOT NULL, # Foreign key to club.club_id
	ca_user int NOT NULL, # Foreign key to user.user_id
	ca_access int NOT NULL # 0=member 1=leader
);

CREATE UNIQUE INDEX club_access_club_user ON club_access (ca_club,ca_user);
CREATE INDEX club_access_club ON club_access (ca_club);
CREATE INDEX club_access_user ON club_access (ca_user);

CREATE TABLE club (
	club_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	club_name varchar(255) binary NOT NULL,
	club_teacher int NOT NULL, # Foreign key to user.user_id
	club_desc int NOT NULL, # Foreign key to text.text_id
	club_inactive boolean NOT NULL # !!!
);

CREATE INDEX club_name ON club (club_name);
CREATE INDEX club_teacher ON club (club_teacher);

CREATE TABLE text (
	text_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	text_data mediumblob NOT NULL, # data depends on flags
	text_flags tinyblob NOT NULL # comma-separated list of gzip,utf-8,object,external
);

CREATE TABLE club_posts (
	cp_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	cp_club int NOT NULL, # Foreign key to club.club_id
	cp_title varchar(255) binary NOT NULL,
	cp_text int NOT NULL, # Foreign key to text.text_id
	cp_timestamp # !!!
);

CREATE INDEX club_posts_club ON club_posts (cp_club);

CREATE TABLE upload (
	upload_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	upload_club int NOT NULL, # Foreign key to club.club_id
	upload_user int NOT NULL, # Foreign key to user.user_id
	upload_loc tinyblob NOT NULL,
	upload_mime varchar(255) binary NOT NULL # MIME type
);

CREATE INDEX upload_club ON upload (upload_club);
CREATE INDEX upload_user ON upload (upload_user);