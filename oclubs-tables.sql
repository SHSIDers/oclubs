CREATE DATABASE oclubs CHARACTER SET utf8;
USE oclubs;

CREATE TABLE user (
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

CREATE UNIQUE INDEX user_login_name ON user (user_login_name);
CREATE INDEX user_passport_name ON user (user_passport_name);

CREATE TABLE club (
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
	club_joinmode tinyint NOT NULL, # 1 = free join, 2 = by invitation,
	club_reactivate boolean NOT NULL,
	club_reservation_allowed boolean NOT NULL, # true = allowed, false = not allowed,
	club_smartboard_allowed boolean NOT NULL # true = allowed, false = not allowed
);

CREATE INDEX club_name ON club (club_name);
CREATE INDEX club_teacher ON club (club_teacher);
CREATE INDEX club_leader ON club (club_leader);


CREATE TABLE club_member (
	cm_club int NOT NULL, # Foreign key to club.club_id
	cm_user int NOT NULL, # Foreign key to user.user_id
	PRIMARY KEY (cm_club, cm_user)
);

#CREATE UNIQUE INDEX cm_club_user ON club_member (cm_club,cm_user);
CREATE INDEX cm_club ON club_member (cm_club);
CREATE INDEX cm_user ON club_member (cm_user);


CREATE TABLE activity (
	act_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	act_name varchar(255) NOT NULL,
	act_club int NOT NULL, # Foreign key to club.club_id
	act_desc int NOT NULL, # Foreign key to text.text_id
	act_date int unsigned NOT NULL,
	act_time tinyint NOT NULL, # 0 = unknown, 1 = noon, 2 = afterschool, 3 = hongmei, 4 = others
	act_location varchar(255) NOT NULL,
	act_cas int NOT NULL, # CAS hours
	act_post int NOT NULL, # Foreign key to text.text_id
	act_selections varchar(255), NOT NULL # stores object in JSON
	act_reservation int, # Foreign key to reservation.reservations_id
);

CREATE INDEX act_club ON activity (act_club);
CREATE INDEX act_post ON activity (act_post);
CREATE INDEX act_date ON activity (act_date);
CREATE INDEX act_time ON activity (act_time);


CREATE TABLE act_pic (
	actpic_act int NOT NULL, # Foreign key to activity.act_id
	actpic_upload int NOT NULL, # Foreign key to upload.upload_id
	PRIMARY KEY (actpic_act, actpic_upload)
);

#CREATE UNIQUE INDEX actpic_act_upload ON act_pic (actpic_act, actpic_upload);
CREATE INDEX actpic_act ON act_pic (actpic_act);
CREATE INDEX actpic_upload ON act_pic (actpic_upload);


CREATE TABLE attendance (
	att_act int NOT NULL, # Foreign key to activity.activity_id
	att_user int NOT NULL, # Foreign key to user.user_id
	PRIMARY KEY (att_act, att_user)
);

#CREATE UNIQUE INDEX att_act_user ON attendance (att_act, att_user);
CREATE INDEX att_act ON attendance (att_act);
CREATE INDEX att_user ON attendance (att_user);


CREATE TABLE text (
	text_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	text_club int NOT NULL, # Foreign key to club.club_id
	text_user int NOT NULL, # Foreign key to user.user_id
	text_data mediumblob NOT NULL, # data depends on flags
	text_flags tinyblob NOT NULL # comma-separated list of gzip,external
);

CREATE INDEX text_club ON text (text_club);
CREATE INDEX text_user ON text (text_user);


CREATE TABLE upload (
	upload_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	upload_club int NOT NULL, # Foreign key to club.club_id
	upload_user int NOT NULL, # Foreign key to user.user_id
	upload_loc varchar(255) NOT NULL,
	upload_mime varchar(255) NOT NULL # MIME type
);

CREATE INDEX upload_club ON upload (upload_club);
CREATE INDEX upload_user ON upload (upload_user);


CREATE TABLE notification (
	notification_id int unsigned NOT NULL PRIMARY KEY AUTO_INCREMENT,
	notification_user int NOT NULL, # Foreign key to user.user_id
	notification_text varchar(255) NOT NULL,
	notification_isread boolean NOT NULL,
	notification_date int NOT NULL
);

CREATE INDEX notification_user ON notification (notification_user);


CREATE TABLE signup (
	signup_act int NOT NULL, # Foreign key to act.act_id
	signup_user int NOT NULL, # Foreign key to user.user_id
	signup_consentform boolean NOT NULL,
	signup_selection varchar(255) NOT NULL,
	PRIMARY KEY (signup_act, signup_user)
);

CREATE INDEX signup_act ON signup (signup_act);
CREATE INDEX signup_user ON signup (signup_user);


CREATE TABLE invitation (
	invitation_club int NOT NULL, # Foreign key to club.club_id
	invitation_user int NOT NULL, # Foreign key to user.user_id
	invitation_date int NOT NULL,
	PRIMARY KEY (invitation_club, invitation_user)
);

CREATE INDEX invitation_user ON invitation (invitation_user);


CREATE TABLE preferences (
	pref_user int NOT NULL, # Foreign key to user.user_id
	pref_type varchar(255) NOT NULL,
	pref_value varchar(255) NOT NULL,
	PRIMARY KEY (pref_user, pref_type)
);

CREATE INDEX pref_user ON preferences (pref_user);

CREATE TABLE classroom (
	room_id NOT NULL PRIMARY KEY AUTO_INCREMENT,
	room_number NOT NULL,
	room_studentsToUse boolean NOT NULL, # true = available to students, false = not available to students
	room_building tinyint, # 0 = XMT, 1 = ZXB
	room_desc varchar(255) # optional descriptors (eg ASB only)
);

CREATE TABLE reservation (
	res_id NOT NULL PRIMARY KEY AUTO_INCREMENT;
	res_activity int NOT NULL, # Foreign key to act.act_id
	res_classroom int NOT NULL, # Foreign key to classroom.classroom_id
	res_SBNeeded boolean NOT NULL, # true = need smartboard, false = no need smartboard
	res_SBAppDesc varchar(500) NOT NULL,
	res_instructors_approval boolean NOT NULL,
	res_directors_approval boolean NOT NULL,
	res_SBApp_success boolean NOT NULL # true = sucess, allowed to use smartboard, default = false, application to use still pending
);

