drop table if exists orders;
drop table if exists users;

create table orders (
  orderid integer primary key autoincrement,
  cnname string not null,
  sex integer not null,
  tsize string not null,
  typeid integer not null,
  num integer not null,
  createtime datetime
);

create table users (
  userid integer primary key autoincrement,
  username string not null,
  password string not null,
  cnname string not null,
  userclass string not null 
);
