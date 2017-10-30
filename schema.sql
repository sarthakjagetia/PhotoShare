CREATE DATABASE photoshare;
USE photoshare;


-- CREATE USER TABLE
CREATE TABLE Users (
    user_id INT NOT NULL AUTO_INCREMENT,
    gender VARCHAR(6),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(40) NOT NULL,
    dob DATE NOT NULL,
    hometown VARCHAR(40),
    fname VARCHAR(40) NOT NULL,
    lname VARCHAR(40) NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE Albums(
	album_id INT AUTO_INCREMENT,
	Name VARCHAR(40) NOT NULL,
	date_of_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
	user_id INT NOT NULL,
	PRIMARY KEY (album_id),
	FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- CREATE Photo TABLE (include photo entity and 'contains' relationship)
CREATE TABLE Pictures(
	picture_id INT AUTO_INCREMENT,
  user_id INT,
	caption VARCHAR(200),
	imgdata LONGBLOB,
	album_id INT NOT NULL,
	PRIMARY KEY (picture_id),
  FOREIGN KEY (user_id) REFERENCES Users (user_id),
	FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE
);

-- CREATE FRIENDSHIP TABLE
CREATE TABLE Friendship(
	UID1 INT NOT NULL,
	UID2 INT NOT NULL,
	PRIMARY KEY(UID1, UID2),
	FOREIGN KEY (UID1) REFERENCES Users (user_id) ON DELETE CASCADE,
	FOREIGN KEY (UID2) REFERENCES Users (user_id) ON DELETE CASCADE
);


-- CREATE Comment TABLE (include comment entity and 'comment' relationship)
CREATE TABLE Comments(
	comment_id INT NOT NULL AUTO_INCREMENT,
	text TEXT NOT NULL,
	date DATETIME DEFAULT CURRENT_TIMESTAMP,
	user_id INT NOT NULL,
	picture_id INT NOT NULL,
	PRIMARY KEY (comment_id),
	FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE,
	FOREIGN KEY (picture_id) REFERENCES Pictures (picture_id) ON DELETE CASCADE
);

-- CREATE THE LIKETABLE. WE CAN'T name it LIKE
CREATE TABLE Likes(
	user_id INT NOT NULL,
	picture_id INT NOT NULL,
	date_of_like DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (picture_id),
  UNIQUE (picture_id, user_id),
	FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE,
	FOREIGN KEY (picture_id) REFERENCES Pictures (picture_id) ON DELETE CASCADE
);


-- CREATE Tag TABLE
CREATE TABLE Tags (
  tag_id INT NOT NULL AUTO_INCREMENT,
  tag_word VARCHAR(30),
	picture_id INT NOT NULL,
  PRIMARY KEY (tag_id),
	FOREIGN KEY (picture_id) REFERENCES Pictures (picture_id) ON DELETE CASCADE
);


INSERT INTO Users(user_id, email, password, dob, fname, lname) VALUE (1, 'guest@bu.edu', 'guest', '29-01-04', 'guest', 'user');
#INSERT INTO Albums (album_id, Name, user_id) VALUES (1, 'hardcoded', 1);
#INSERT INTO Pictures (picture_id, album_id) VALUES (1, 1);
#INSERT INTO Tags(tag_id, picture_id) VALUES (1, 1);


