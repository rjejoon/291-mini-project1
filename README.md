# 291-mini-project1
> Python SQLite project for CMPUT 291

This application is a simple Q&A forum where users can post questions and share their answers with others. 

It also supports assigning badges and tags to a user, casting votes on other posts, edit a post, and search posts using one or more keywords.

All the data manipulation is done via SQLite.

## Quick Start

Create a database file:

```sh
$ sqlite3 test.db < testSchema.sql
```

Try out the application:

```sh
$ python3 main.py test.db
```

