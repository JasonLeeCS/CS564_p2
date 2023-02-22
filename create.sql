drop table if exists Bid;
drop table if exists Category;
drop table if exists Item;
drop table if exists User;
create table Bid(
    itemID int NOT NULL, 
    amount float NOT NULL,
    userID varchar(255) NOT NULL, 
    time time NOT NULL, 
    foreign key (itemID) references item(itemID),
    foreign key (userID) references user(userID)
);
create table Category(
    itemID int NOT NULL, 
    category varchar(255) NOT NULL,
    foreign key (itemID) references bid(itemID)
);
create table Item(
    itemID int NOT NULL, 
    ends time NOT NULL, 
    first_bid float NOT NULL, 
    name varchar(255) NOT NULL, 
    started time NOT NULL, 
    number_of_bids int NOT NULL, 
    currently float NOT NULL, 
    userID varchar(255) NOT NULL, 
    description varchar(255),
    primary key(itemID),
    foreign key(userID) references user(userID)
);
create table User(
    rating int NOT NULL, 
    userID varchar(255) NOT NULL,
    location varchar(255),
    country varchar(255),
    primary key(userID)
);
