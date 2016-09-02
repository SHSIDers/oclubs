CREATE DATABASE IF NOT EXISTS oclubs CHARACTER SET utf8;
USE oclubs;

CREATE TABLE IF NOT EXISTS user (
	user_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	user_login_name varchar(255) NOT NULL, # Student ID
	user_nick_name varchar(255) NOT NULL,
	user_passport_name varchar(255) NOT NULL,
	user_password tinyblob,
	user_picture int NOT NULL, # Foreign key to upload.upload_id
	user_email tinytext NOT NULL,
	user_phone bigint,
	user_type tinyint NOT NULL, # 1=student 2=teacher 3=admin
	user_grade tinyint, # NULL for teachers
	user_class tinyint # NULL for teachers
);

CREATE UNIQUE INDEX IF NOT EXISTS user_login_name ON user (user_login_name);


CREATE TABLE IF NOT EXISTS club (
	club_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	club_name varchar(255) NOT NULL,
	club_teacher int NOT NULL, # Foreign key to user.user_id
	club_leader int NOT NULL, # Foreign key to user.user_id
	club_intro tinytext NOT NULL,
	club_picture int NOT NULL, # Foreign key to upload.upload_id
	club_desc int NOT NULL, # Foreign key to text.text_id
	club_location varchar(255) NOT NULL,
	club_inactive boolean NOT NULL,
	club_type tinyint NOT NULL, # 1 = academics, 2 = sports, 3 = arts, 4 = services, 5 = entertainment, 6 = others, 7 = school teams
	club_joinmode tinyint NOT NULL # 1 = free join, 2 = by invitation
);

CREATE INDEX IF NOT EXISTS club_name ON club (club_name);
CREATE INDEX IF NOT EXISTS club_teacher ON club (club_teacher);
CREATE INDEX IF NOT EXISTS club_leader ON club (club_leader);


CREATE TABLE IF NOT EXISTS club_member (
	cm_club int NOT NULL, # Foreign key to club.club_id
	cm_user int NOT NULL, # Foreign key to user.user_id
	PRIMARY KEY (cm_club, cm_user)
);

#CREATE UNIQUE INDEX IF NOT EXISTS cm_club_user ON club_member (cm_club,cm_user);
CREATE INDEX IF NOT EXISTS cm_club ON club_member (cm_club);
CREATE INDEX IF NOT EXISTS cm_user ON club_member (cm_user);


CREATE TABLE IF NOT EXISTS activity (
	act_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	act_name varchar(255) NOT NULL,
	act_club int NOT NULL, # Foreign key to club.club_id
	act_desc int NOT NULL, # Foreign key to text.text_id
	act_date int unsigned NOT NULL,
	act_time tinyint NOT NULL, # 0 = unknown, 1 = noon, 2 = afterschool, 3 = hongmei, 4 = others
	act_location varchar(255) NOT NULL,
	act_cas int NOT NULL, # CAS hours
	act_post int NOT NULL, # Foreign key to text.text_id
	act_selections varchar(255) NOT NULL # stores object in JSON
);

CREATE INDEX IF NOT EXISTS act_club ON activity (act_club);
CREATE INDEX IF NOT EXISTS act_post ON activity (act_post);
CREATE INDEX IF NOT EXISTS act_date ON activity (act_date);
CREATE INDEX IF NOT EXISTS act_time ON activity (act_time);


CREATE TABLE IF NOT EXISTS act_pic (
	actpic_act int NOT NULL, # Foreign key to activity.act_id
	actpic_upload int NOT NULL, # Foreign key to upload.upload_id
	PRIMARY KEY (actpic_act, actpic_upload)
);

#CREATE UNIQUE INDEX IF NOT EXISTS actpic_act_upload ON act_pic (actpic_act, actpic_upload);
CREATE INDEX IF NOT EXISTS actpic_act ON act_pic (actpic_act);
CREATE INDEX IF NOT EXISTS actpic_upload ON act_pic (actpic_upload);


CREATE TABLE IF NOT EXISTS attendance (
	att_act int NOT NULL, # Foreign key to activity.activity_id
	att_user int NOT NULL, # Foreign key to user.user_id
	PRIMARY KEY (att_act, att_user)
);

#CREATE UNIQUE INDEX IF NOT EXISTS att_act_user ON attendance (att_act, att_user);
CREATE INDEX IF NOT EXISTS att_act ON attendance (att_act);
CREATE INDEX IF NOT EXISTS att_user ON attendance (att_user);


CREATE TABLE IF NOT EXISTS text (
	text_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	text_club int NOT NULL, # Foreign key to club.club_id
	text_user int NOT NULL, # Foreign key to user.user_id
	text_data mediumblob NOT NULL, # data depends on flags
	text_flags tinyblob NOT NULL # comma-separated list of gzip,external
);

CREATE INDEX IF NOT EXISTS text_club ON text (text_club);
CREATE INDEX IF NOT EXISTS text_user ON text (text_user);


CREATE TABLE IF NOT EXISTS upload (
	upload_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	upload_club int NOT NULL, # Foreign key to club.club_id
	upload_user int NOT NULL, # Foreign key to user.user_id
	upload_loc varchar(255) NOT NULL,
	upload_mime varchar(255) NOT NULL # MIME type
);

CREATE INDEX IF NOT EXISTS upload_club ON upload (upload_club);
CREATE INDEX IF NOT EXISTS upload_user ON upload (upload_user);


CREATE TABLE IF NOT EXISTS notification (
	notification_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	notification_user int NOT NULL, # Foreign key to user.user_id
	notification_text varchar(255) NOT NULL,
	notification_isread boolean NOT NULL,
	notification_date int NOT NULL
);

CREATE INDEX IF NOT EXISTS notification_user ON notification (notification_user);


CREATE TABLE IF NOT EXISTS signup (
	signup_act int NOT NULL, # Foreign key to act.act_id
	signup_user int NOT NULL, # Foreign key to user.user_id
	signup_consentform boolean NOT NULL,
	signup_selection varchar(255) NOT NULL,
	PRIMARY KEY(signup_act, signup_user)
);

CREATE INDEX IF NOT EXISTS signup_act ON signup (signup_act);
CREATE INDEX IF NOT EXISTS signup_user ON signup (signup_user);


CREATE TABLE IF NOT EXISTS invitation (
	invitation_club int NOT NULL, # Foreign key to club.club_id
	invitation_user int NOT NULL, # Foreign key to user.user_id
	invitation_date int NOT NULL,
	PRIMARY KEY(invitation_club, invitation_user)
);

CREATE INDEX IF NOT EXISTS invitation_user ON invitation (invitation_user);


CREATE TABLE IF NOT EXISTS preferences (
	pref_user int NOT NULL, # Foreign key to user.user_id
	pref_type varchar(255) NOT NULL,
	pref_value varchar(255) NOT NULL,
	PRIMARY KEY (pref_user, pref_type)
);

CREATE INDEX IF NOT EXISTS pref_user ON user (pref_user);
