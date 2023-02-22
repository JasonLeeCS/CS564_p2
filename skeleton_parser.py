"""
FILE: skeleton_parser.py
------------------
Author: Firas Abuzaid (fabuzaid@stanford.edu)
Author: Perth Charernwattanagul (puch@stanford.edu)
Modified: 04/21/2014

Skeleton parser for CS564 programming project 1. Has useful imports and
functions for parsing, including:

1) Directory handling -- the parser takes a list of eBay json files
and opens each file inside of a loop. You just need to fill in the rest.
2) Dollar value conversions -- the json files store dollar value amounts in
a string like $3,453.23 -- we provide a function to convert it to a string
like XXXXX.xx.
3) Date/time conversions -- the json files store dates/ times in the form
Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.

Your job is to implement the parseJson function, which is invoked on each file by
the main function. We create the initial Python dictionary object of items for
you; the rest is up to you!
Happy parsing!
"""

import sys
from json import loads
from re import sub

columnSeparator = "|"

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

"""
Returns true if a file ends in .json
"""
def isJson(f):
    return len(f) > 5 and f[-5:] == '.json'

"""
Converts month to a number, e.g. 'Dec' to '12'
"""
def transformMonth(mon):
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

"""
Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
"""
def transformDttm(dttm):
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

"""
Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
"""

def transformDollar(money):
    if money == None or len(money) == 0:
        return money
    return sub(r'[^\d.]', '', money)

"""
Escapes quotation marks for strings
"""

itemEntity = {}
userEntity = {}
bidEntity = []
categoryEntity = {}

def escapeDQ(str):
    if (str == None):
        return '"NULL"'
    return '"'+str.replace('"', '""')+'"'

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file):

    with open(json_file, 'r') as f:
        items = loads(f.read())['Items'] # creates a Python dictionary of Items for the supplied json file
        for item in items:
            # hello
            # Create Item Entity
            if (item['ItemID'] not in itemEntity):
                itemEntity[item['ItemID']] = {  
                    'ItemID': item['ItemID'], 
                    'Name': escapeDQ(item['Name']), 
                    'Currently': transformDollar(item['Currently']), 
                    'First_Bid': transformDollar(item['First_Bid']), 
                    'Number_of_Bids': item['Number_of_Bids'], 
                    'Started': transformDttm(item['Started']), 
                    'Ends': transformDttm(item['Ends']), 
                    'Description': escapeDQ(item['Description']), 
                    'UserID': item['Seller']['UserID']
                }
            
            # Create User Entity using Seller Information
            if (item['Seller']['UserID'] not in userEntity):
                userEntity[item['Seller']['UserID']] = {
                    'UserID': escapeDQ(item['Seller']['UserID']), 
                    'Rating': item['Seller']['Rating'], 
                    'Location': escapeDQ(item['Location']), 
                    'Country': escapeDQ(item['Country'])
                }

            # Traverse through bids for Sellers and Bid information
            if (item['Bids']):
                for bid in item['Bids']:
                    bidder = bid['Bid']['Bidder']

                    # Create User Entity using Bidder information
                    if (bidder['UserID'] not in userEntity):
                        bidder_location = 'NULL'
                        bidder_country = 'NULL'
                        if 'Location' in bidder:
                            bidder_location = bidder['Location']
                        if 'Country' in bidder:
                            bidder_country = bidder['Country']
                        userEntity[bidder['UserID']] = {
                            'UserID': escapeDQ(bidder['UserID']), 
                            'Rating': bidder['Rating'], 
                            'Location': escapeDQ(bidder_location), 
                            'Country': escapeDQ(bidder_country)
                        }

                    # Create Bid Entity
                    bidEntity.append({
                        'ItemID': item['ItemID'], 
                        'UserID': bidder['UserID'], 
                        'Time': transformDttm(bid['Bid']['Time']), 
                        'Amount': transformDollar(bid['Bid']['Amount'])
                    })
            
            # Create Category Entity
            for category in item['Category']:
                # Check whether category exists and create category if not exists
                if (category not in categoryEntity):
                    categoryEntity[category] = {
                        'Items': [item['ItemID']], 
                        'Category': escapeDQ(category)
                    }
                elif (category in categoryEntity and item['ItemID'] not in categoryEntity[category]['Items']):
                    categoryEntity[category]['Items'].append(item['ItemID'])
                    

"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
        sys.exit(1)
    
    # Empty the data files first
    open('users.dat', 'w').close()
    open('items.dat', 'w').close()
    open('bids.dat', 'w').close()
    open('categories.dat', 'w').close()
    
    # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            parseJson(f)
            print("Success parsing " + f)
    

    # Begin Write to Data Files
    usersFile = open('users.dat', 'a')
    itemsFile = open('items.dat', 'a')
    bidsFile = open('bids.dat', 'a')
    categoriesFile = open('categories.dat', 'a')

    # Write User Entity to users.dat
    for id, attributes in userEntity.items():
        line = ''
        for a in attributes.values():
            line += str(a)+'|'
        usersFile.write(line[:-1]+'\n')

    # Write Item Entity to items.dat
    for id, attributes in itemEntity.items():
        line = ''
        for a in attributes.values():
            line += str(a)+'|'
        itemsFile.write(line[:-1]+'\n')


    # Write Bid Entity to bids.dat
    for attributes in bidEntity:
        line = ''
        for a in attributes.values():
            line += str(a)+'|'
        bidsFile.write(line[:-1]+'\n')

    # Write Category Entity to category.dat
    for category in categoryEntity:
        line = ''
        for item in categoryEntity[category]['Items']:
            line += str(item)+'|'+str(category)+'\n'
        categoriesFile.write(line)

    usersFile.close()
    bidsFile.close()
    itemsFile.close()
    categoriesFile.close()

if __name__ == '__main__':
    main(sys.argv)