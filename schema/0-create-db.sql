drop table if exists ReceiptItems;
drop table if exists Receipts;
drop table if exists Items;
drop table if exists Tags;

create table Tags (
	id integer primary key auto_increment,
	name varchar(64),
	balance integer not null,

	check (balance >= 0)
);

create table Receipts (
	id integer primary key auto_increment,
	timestamp datetime default(current_timestamp),
	buyer integer references Tags(id)
);

create table Items (
	id integer primary key auto_increment,
	name varchar(64) not null,
	cost integer not null,
	stock integer null,

	image mediumblob
);

insert into Items(id, name, cost, stock, image) values(0, 'Check balance', 0, 999999999, load_file('/tmp/1.jpg'));

create table ReceiptItems (
	receipt_id integer references Receipts(id),
	item_id integer references Items(id),
	quantity integer not null default 1,

	primary key (receipt_id, item_id)
);
