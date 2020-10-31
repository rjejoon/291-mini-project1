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
insert into users values ('okay', 'TEST', '12345', 'Edmonton', date('now'));
insert into privileged values ('moen');


-- ==========================Test cases for postQ()================================
-- 1. unique pid is assigned
insert into posts values ('s001', date('now'), 'What is a question?', '5question, questions, question, question', 'rjej');
insert into questions values ('s001', null);

insert into posts values ('abcd', date('now'), 'What is a question?', '5question, questions, question, question', 'rjej');
insert into questions values ('abcd', null);

insert into posts values ('efgh', date('now'), 'What is a question?', '5question, questions, question, question', 'rjej');
insert into questions values ('efgh', null);

insert into posts values ('ijkl', date('now'), 'What is a question?', '5question, questions, question, question', 'rjej');
insert into questions values ('ijkl', null);

insert into posts values ('zzzz', date('now'), 'What is a question?', '5question, questions, question, question', 'rjej');
insert into questions values ('zzzz', null);



-- ==========================Test cases for searchPosts()================================
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


--2. Multiple keywords search (keywords: dog, cat, bird)
insert into posts values ('p005', date('now'), 'My dogs and cats?', '10dog, dog, dog, dog, cat, cat, cat, cat', 'rjej');
insert into questions values ('p005', null);
insert into tags values ('p005', 'Animal');

insert into posts values ('p006', date('now'), 'I love dogs, cats, birds?', '12dog, dog, dog, cat, cat, cat, birds, bird, bird', 'rjej');
insert into questions values ('p006', null);
insert into tags values ('p006', 'Animal');
insert into tags values ('p006', 'Birds');

insert into posts values ('p007', date('now'), 'Ans for p005', '8dog, dog, dog, dog, cat, cat, cat, cat', 'rjej');
insert into answers values ('p007', 'p005');

-------------------------------Test cases for ANSWER--------------------------------
insert into posts values ('0001', date('now'), 'This is an answer', '6answers, answer, answers, answer', 'mnmn');
insert into answers values ('0001','p001');
insert into tags values ('0001', 'answers');

insert into posts values ('0002', date('now'), 'This is an answer', '4(v5)answers, answers, answer', 'mnmn');
insert into answers values ('0002','p001');
insert into tags values ('0002', 'fine');

insert into posts values ('0003', date('now'), 'This is an ans', '5(v4)answers, answer, answers, answer', 'mnmn');
insert into answers values ('0003','p002');
insert into tags values ('0003', 'answers');

insert into posts values ('0004', date('now'), 'This is an ans', '4answers, answer, answers', 'mnmn');
insert into answers values ('0004','p003');
insert into tags values ('0004', 'answers');

insert into posts values ('0005', date('now'), 'This is an ans', '1answers', 'mnmn');
insert into answers values ('0005','p003');

insert into posts values ('0006', date('now'), 'This is an answer', '2answers', 'mnmn');
insert into answers values ('0006','p004');


-------------------------------Test cases for VOTE--------------------------------
insert into votes values ('p001',1,date('now','-5 days'),'mnmn');
insert into votes values ('p001',2,date('now','-6 days'),'mnmn');
insert into votes values ('p001',3,date('now','-7 days'),'mnmn');
insert into votes values ('p001',4,date('now','-8 days'),'moen');
insert into votes values ('p001',5,date('now','-9 days'),'moen');
insert into votes values ('p001',6,date('now','-2 days'),'moen');
insert into votes values ('p001',7,date('now','-5 days'),'moen');

insert into votes values ('p002',1,date('now','-5 days'),'mnmn');
insert into votes values ('p002',2,date('now','-6 days'),'mnmn');
insert into votes values ('p002',3,date('now','-7 days'),'mnmn');
insert into votes values ('p002',4,date('now','-8 days'),'moen');
insert into votes values ('p002',5,date('now','-9 days'),'moen');
insert into votes values ('p002',6,date('now','-2 days'),'moen');

insert into votes values ('0002',1,date('now','-5 days'),'mnmn');
insert into votes values ('0002',2,date('now','-6 days'),'mnmn');
insert into votes values ('0002',3,date('now','-7 days'),'mnmn');
insert into votes values ('0002',4,date('now','-8 days'),'moen');
insert into votes values ('0002',5,date('now','-9 days'),'moen');

insert into votes values ('0003',1,date('now','-5 days'),'mnmn');
insert into votes values ('0003',2,date('now','-6 days'),'mnmn');
insert into votes values ('0003',3,date('now','-7 days'),'mnmn');
insert into votes values ('0003',4,date('now','-8 days'),'moen');



-------------------------------Test cases for BADGE--------------------------------

insert into badges values ('excellent question','gold');
insert into badges values ('great question', 'silver');
insert into badges values ('excellent answer', 'gold');
insert into badges values ('great answer', 'silver');
insert into badges values ('good question', 'bronze');
insert into badges values ('good answer', 'bronze');

--- TEST CASE FOR MARK ANSWER ---
insert into posts values ('p009', date('now'), 'Testing for mark answer?', 'a001 is a default accepted answer', 'rjej');
insert into questions values ('p009', null);

insert into posts values ('a001', date('now'), 'This is an accepted answer', 'mark, mark', 'mnmn');
insert into answers values ('a001','p009');

update questions set theaid = 'a001' where pid = 'p009';

insert into posts values ('a002', date('now'), 'Change this to accepted answer', 'mark, mark', 'mnmn');
insert into answers values ('a002','p009');