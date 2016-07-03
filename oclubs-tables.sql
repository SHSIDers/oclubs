CREATE TABLE user (
	user_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	user_login_name varchar(255) binary NOT NULL,
	user_nick_name varchar(255) binary NOT NULL,
	user_password tinyblob NOT NULL,
	user_email tinytext NOT NULL,
	user_photo int NOT NULL, # Foreign key to upload.upload_id
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
	club_leader int NOT NULL, # Foreign key to user.user_id
	club_members int(255) NOT NULL, # Foreign key to user.user_id
	club_desc int NOT NULL, # Foreign key to text.text_id
	club_tips int NOT NULL, # Foreign key to text.text_id
	club_location int NOT NULL, # XMT,ZXB, basketball court,...
	club_inactive boolean NOT NULL, # !!!
	club_isexcellent boolean NOT NULL
);
CREATE INDEX club_isexcellent ON club (club_isexcellent);
CREATE INDEX club_name ON club (club_name);
CREATE INDEX club_teacher ON club (club_teacher);

CREATE TABLE activity (
	act_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	act_name varchar(255) binary NOT NULL,
	act_clubs int(255) NOT NULL, # Foreign key to club.club_id
	act_members int(255) NOT NULL # Foreign key to user.user_id
	act_desc int NOT NULL, # Foreign key to text.text_id
	act_pic int(255), # Foreign key to upload.upload_id
	act_date int(2) NOT NULL, # Year/Month/Date
	act_time int NOT NULL, # Uploaded time
	act_location int NOT NULL, #XMT,ZXB, basketball court, Hongmei,...
	act_CAS int NOT NULL # CAS hours
);

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
	cp_editor int NOT NULL, # Foreign key to user.user_id
	cp_pic int(255) NOT NULL, # Foreign key to upload.upload_id
	cp_timestamp int NOT NULL
);

CREATE INDEX club_posts_club ON club_posts (cp_club);

CREATE TABLE upload (
	upload_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	upload_club int NOT NULL, # Foreign key to club.club_id
	upload_user int NOT NULL, # Foreign key to user.user_id
	upload_loc tinyblob NOT NULL,
	upload_mime varchar(255) binary NOT NULL # MIME type
);

CREATE TABLE quit_club_request (
	quit_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	quit_club int NOT NULL, # Foreign key to club.club_id
	quit_user int NOT NULL, # Foreign key to user.user_id
	quit_reason int NOT NULL, # Foreign key to text.text_id
);

CREATE TABLE signup (
	signup_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	signup_act int NOT NULL, # Foreign key to act.act_id
	signup_user int NOT NULL, # Foreign key to user.user_id
	signup_comment int NOT NULL, # Foreign key to text.text_id
	signup_time int NOT NULL,
	signup_consentform boolean NOT NULL
);

CREATE INDEX upload_club ON upload (upload_club);
CREATE INDEX upload_user ON upload (upload_user); 
