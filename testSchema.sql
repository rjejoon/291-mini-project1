drop table if exists answers;
drop table if exists questions;
drop table if exists votes;
drop table if exists tags;
drop table if exists posts;
drop table if exists ubadges;
drop table if exists badges;
drop table if exists privileged;
drop table if exists users;

PRAGMA foreign_keys = ON;

create table users (
  uid		char(4),
  name		text,
  pwd		text,
  city		text,
  crdate	date,
  primary key (uid)
);
create table privileged (
  uid		char(4),
  primary key (uid),
  foreign key (uid) references users
);
create table badges (
  bname		text,
  type		text,
  primary key (bname)
);
create table ubadges (
  uid		char(4),
  bdate		date,
  bname		text,
  primary key (uid,bdate),
  foreign key (uid) references users,
  foreign key (bname) references badges
);
create table posts (
  pid		char(4),
  pdate		date,
  title		text,
  body		text,
  poster	char(4),
  primary key (pid),
  foreign key (poster) references users
);
create table tags (
  pid		char(4),
  tag		text,
  primary key (pid,tag),
  foreign key (pid) references posts
);
create table votes (
  pid		char(4),
  vno		int,
  vdate		text,
  uid		char(4),
  primary key (pid,vno),
  foreign key (pid) references posts,
  foreign key (uid) references users
);
create table questions (
  pid		char(4),
  theaid	char(4),
  primary key (pid),
  foreign key (theaid) references answers
);
create table answers (
  pid		char(4),
  qid		char(4),
  primary key (pid),
  foreign key (qid) references questions
);


insert into users values ('rj', 'Kevin Ryu', 'rjj0220', 'Regina', date('now'));
insert into users values ('rjej', 'Kevin Ryu', 'rjj0220', 'Regina', date('now'));
insert into privileged values ('rjej');
insert into users values ('moen', 'Moe Numasawa', '12345', 'Edmonton', date('now'));
insert into users values ('mnmn', 'Moe Ordinary', '12345', 'Edmonton', date('now'));
insert into privileged values ('moen');

-- test cases for searchPosts()
-- 1. Ordering works
insert into posts values ('p001', date('now'), 'What is database?', '6Database, database, database, database', 'rjej');
insert into questions values ('p001', null);
insert into tags values ('p001', 'Database');

insert into posts values ('p002', date('now'), 'What is ?', '5Database, database, database, database', 'rjej');
insert into questions values ('p002', null);
insert into tags values ('p002', 'Database');

insert into posts values ('p003', date('now'), 'What is database?', '4Database, database', 'rjej');
insert into questions values ('p003', null);
insert into tags values ('p003', 'Database');

insert into posts values ('p004', date('now'), 'What is database?', '3Database, database', 'rjej');
insert into questions values ('p004', null);

insert into posts values ('p005', date('now'), 'What is database?', '4Database, database', 'rjej');
insert into questions values ('p005', null);
insert into tags values ('p005', 'Database');

insert into posts values ('p006', date('now'), 'What is database?', '3Database, database', 'rjej');
insert into questions values ('p006', null);



insert into badges values ('excellent question','gold');
insert into badges values ('good question', 'silver');
