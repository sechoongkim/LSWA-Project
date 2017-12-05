/* Create our database */
CREATE DATABASE streeTunes CHARACTER SET utf8;

/* Setup permissions for the server */
CREATE USER 'appserver'@'54.145.132.94' IDENTIFIED BY 'foobarzoot';
CREATE USER 'www-data'@'54.145.132.94' IDENTIFIED BY 'foobarzoot';
GRANT ALL ON streeTunes.* TO 'appserver'@'54.145.132.94';
GRANT ALL ON streeTunes.* TO 'www-data'@'54.145.132.94';
