CREATE DATABASE IF NOT EXISTS oclubs CHARACTER SET utf8;
USE oclubs;

CREATE TABLE IF NOT EXISTS user (
	user_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	user_login_name varchar(255) binary NOT NULL, # Student ID
	user_nick_name varchar(255) binary NOT NULL,
	user_passport_name varchar(255) binary NOT NULL,
	user_password tinyblob NOT NULL,
	user_picture int NOT NULL, # Foreign key to upload.upload_id
	user_email tinytext NOT NULL,
	user_photo int NOT NULL, # Foreign key to upload.upload_id
	user_type int NOT NULL, # 0=student 1=teacher 2=admin
	user_grad_year int # NULL for teachers
);

CREATE UNIQUE INDEX IF NOT EXISTS user_login_name ON user (user_login_name);


CREATE TABLE IF NOT EXISTS club (
	club_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	club_name varchar(255) binary NOT NULL,
	club_teacher int NOT NULL, # Foreign key to user.user_id
	club_leader int NOT NULL, # Foreign key to user.user_id
	club_intro tinyblob NOT NULL,
	club_picture int NOT NULL, # Foreign key to upload.upload_id
	club_desc int NOT NULL, # Foreign key to text.text_id
	club_location tinyblob NOT NULL, # stores object in JSON
	club_inactive boolean NOT NULL
);

CREATE INDEX IF NOT EXISTS club_name ON club (club_name);
CREATE INDEX IF NOT EXISTS club_teacher ON club (club_teacher);
CREATE INDEX IF NOT EXISTS club_leader ON club (club_leader);


CREATE TABLE IF NOT EXISTS club_member (
	cm_club int NOT NULL, # Foreign key to club.club_id
	cm_user int NOT NULL # Foreign key to user.user_id
);

CREATE UNIQUE INDEX IF NOT EXISTS cm_club_user ON club_member (cm_club,cm_user);
CREATE INDEX IF NOT EXISTS cm_club ON club_member (cm_club);
CREATE INDEX IF NOT EXISTS cm_user ON club_member (cm_user);


CREATE TABLE IF NOT EXISTS activity (
	act_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	act_name varchar(255) binary NOT NULL,
	act_club int NOT NULL, # Foreign key to club.club_id
	act_desc int NOT NULL, # Foreign key to text.text_id
	act_date int unsigned NOT NULL,
	act_time int NOT NULL, # 0 = unknown, 1 = noon, 2 = afterschool, 3 = hongmei, 4 = others
	act_location mediumblob NOT NULL, # stores object in JSON
	act_cas int NOT NULL, # CAS hours
	act_cp int # Foreign key to clubpost.cp_act
);

CREATE INDEX IF NOT EXISTS act_club ON activity (act_club);
CREATE INDEX IF NOT EXISTS act_cp ON activity (act_cp);

CREATE TABLE IF NOT EXISTS activity_pic (
	ap_act int NOT NULL, # Foreign key to activity.act_id
	ap_upload int NOT NULL # Foreign key to upload.upload_id
);

CREATE UNIQUE INDEX IF NOT EXISTS ap_act_upload ON activity_pic (ap_act, ap_upload);
CREATE INDEX IF NOT EXISTS ap_act ON activity_pic (ap_act);
CREATE INDEX IF NOT EXISTS ap_upload ON activity_pic (ap_upload);

CREATE TABLE IF NOT EXISTS attendance (
	att_act int NOT NULL, # Foreign key to activity.activity_id
	att_user int NOT NULL # Foreign key to user.user_id
);

CREATE UNIQUE INDEX IF NOT EXISTS att_act_user ON attendance (att_act, att_user);
CREATE INDEX IF NOT EXISTS att_act ON attendance (att_act);
CREATE INDEX IF NOT EXISTS att_user ON attendance (att_user);


CREATE TABLE IF NOT EXISTS clubpost (
	cp_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	cp_club int NOT NULL, # Foreign key to club.club_id
	cp_title varchar(255) binary NOT NULL,
	cp_text int NOT NULL, # Foreign key to text.text_id
	cp_editor int NOT NULL, # Foreign key to user.user_id
	cp_timestamp int NOT NULL
);

CREATE INDEX IF NOT EXISTS clubpost_club ON clubpost (cp_club);

CREATE TABLE IF NOT EXISTS clubpost_pic (
	cp_post int NOT NULL, # Foreign key to clubpost.cp_id
	cp_upload int NOT NULL # Foreign key to upload.upload_id
);

CREATE UNIQUE INDEX IF NOT EXISTS cp_post_upload ON clubpost_pic (cp_post, cp_upload);
CREATE INDEX IF NOT EXISTS cp_post ON clubpost_pic (cp_post);
CREATE INDEX IF NOT EXISTS cp_upload ON clubpost_pic (cp_upload);

CREATE TABLE IF NOT EXISTS text (
	text_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	text_data mediumblob NOT NULL, # data depends on flags
	text_flags tinyblob NOT NULL # comma-separated list of gzip,external
);


CREATE TABLE IF NOT EXISTS upload (
	upload_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	upload_club int NOT NULL, # Foreign key to club.club_id
	upload_user int NOT NULL, # Foreign key to user.user_id
	upload_loc tinyblob NOT NULL,
	upload_mime varchar(255) binary NOT NULL # MIME type
);


CREATE TABLE IF NOT EXISTS notification (
	notification_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	notification_club int NOT NULL, # Foreign key to club.club_id
	notification_user int NOT NULL, # Foreign key to user.user_id
	notification_text int NOT NULL, # Foreign key to text.text_id
	notification_type varchar(255) NOT NULL
);

CREATE INDEX IF NOT EXISTS notification_club ON notification (notification_club);


CREATE TABLE IF NOT EXISTS signup (
	signup_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	signup_act int NOT NULL, # Foreign key to act.act_id
	signup_user int NOT NULL, # Foreign key to user.user_id
	signup_comment int NOT NULL, # Foreign key to text.text_id
	signup_time int NOT NULL,
	signup_consentform boolean NOT NULL
);

CREATE INDEX IF NOT EXISTS upload_club ON upload (upload_club);
CREATE INDEX IF NOT EXISTS upload_user ON upload (upload_user); 