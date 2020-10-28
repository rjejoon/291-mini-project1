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


insert into users values ('rjej', 'Kevin Ryu', 'rjj0220', 'Regina', date('now'));
insert into privileged values ('rjej');
insert into users values ('moe', 'Moe Numasawa', '1234', 'Edmonton', date('now')); 


insert into posts values ('p001', '2020-10-21', 'What is database?', 'test body texts1', 'rjej');
insert into posts values ('p002', '2020-10-21', 'I hate database. What should I do?', 'Db is too complicated...', 'rjej');
insert into posts values ('p003', '2020-10-21', 'What is SqL?', 'I still do not quite understand what it is.', 'rjej');
insert into posts values ('p004', '2020-10-21', 'What is your favorite pizza?', 'My favorite pizza is pepperoni pizza!', 'rjej');
insert into posts values ('p005', '2020-10-21', 'What is relational algebra?', 'test body texts5 database database database database', 'rjej');

insert into questions values ('p001', null);
insert into questions values ('p002', null);
insert into questions values ('p003', null);
insert into questions values ('p004', null);
insert into questions values ('p005', null);

insert into tags values ('p001', 'database');
insert into tags values ('p001', 'd');
insert into tags values ('p001', 'da');
insert into tags values ('p001', 'fj');
insert into tags values ('p001', 'dont');


insert into posts values ('p006', '2020-10-21', 'What is database?', 'test body texts1', 'moe');
insert into posts values ('p007', '2020-10-21', 'What is database?', 'test body texts2 database', 'moe');
insert into posts values ('p008', '2020-10-21', 'What is database?', 'test body texts1', 'moe');

insert into answers values ('p006', 'p001');
insert into answers values ('p007', 'p001');
insert into answers values ('p008', 'p001');

insert into badges values ('excellent question','gold');
insert into badges values ('good question', 'silver');
