
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

itemDict = {}
userDict = {}
bidArr = []
categoryDict = {}

def quoteChecker(word):
    if (word != None):
        return '\"'+word.replace('\"', '\"\"')+'\"'      
    return '"NULL"'

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file):
    with open(json_file, 'r') as f:
        items = loads(f.read())['Items'] 
        for item in items:
            if item['ItemID'] not in itemDict:
                itemDict[item['ItemID']] = {  
                    'ItemID': item['ItemID'], 
                    'Name': quoteChecker(item['Name']), 
                    'Currently': transformDollar(item['Currently']), 
                    'First_Bid': transformDollar(item['First_Bid']), 
                    'Number_of_Bids': item['Number_of_Bids'], 
                    'Started': transformDttm(item['Started']), 
                    'Ends': transformDttm(item['Ends']), 
                    'Description': quoteChecker(item['Description']), 
                    'UserID': item['Seller']['UserID']
                }          
            if item['Seller']['UserID'] not in userDict:
                userDict[item['Seller']['UserID']] = {
                    'Rating': item['Seller']['Rating'],
                    'UserID': quoteChecker(item['Seller']['UserID']),
                    'Location': quoteChecker(item['Location']), 
                    'Country': quoteChecker(item['Country'])
                }

            if item['Bids']:
                for bid in item['Bids']:
                    bidder = bid['Bid']['Bidder']
                    if bidder['UserID'] not in userDict:
                        bidder_location = 'NULL'
                        bidder_country = 'NULL'
                        if 'Location' in bidder:
                            bidder_location = bidder['Location']
                        if 'Country' in bidder:
                            bidder_country = bidder['Country']
                        userDict[bidder['UserID']] = {
                            'Rating': bidder['Rating'],
                            'UserID': quoteChecker(bidder['UserID']), 
                            'Location': quoteChecker(bidder_location), 
                            'Country': quoteChecker(bidder_country)
                        }
                    bidArr.append({
                        'ItemID': item['ItemID'], 
                        'Amount': transformDollar(bid['Bid']['Amount']),
                        'UserID': bidder['UserID'], 
                        'Time': transformDttm(bid['Bid']['Time'])
                    })
          
            for category in item['Category']:
                if category not in categoryDict:
                    categoryDict[category] = {
                        'Items': [item['ItemID']], 
                        'Category': quoteChecker(category)
                    }
                elif category in categoryDict and item['ItemID'] not in categoryDict[category]['Items']:
                    categoryDict[category]['Items'].append(item['ItemID'])
                    
def writeUsers():
    open('users.dat', 'w').close()
    usersOutput = open('users.dat', 'a')
    for id, attributes in userDict.items():
        line = ""
        for a, j in attributes.items():
            line += str(j)+'|'
        usersOutput.write(line[:-1]+'\n')
    usersOutput.close()

def writeItems():
    open('items.dat', 'w').close()
    itemsOutput= open('items.dat', 'a')
    for id, attributes in itemDict.items():
        line = ""
        for a, j in attributes.items():
            line += str(j)+'|'
        itemsOutput.write(line[:-1]+'\n')
    itemsOutput.close()

def writeBids():
    open('bids.dat', 'w').close()
    bidsOutput= open('bids.dat', 'a')
    for attributes in bidArr:
        line = ""
        for a, j in attributes.items():
            line += str(j)+'|'
        bidsOutput.write(line[:-1]+'\n')
    bidsOutput.close()

def writeCategories():
    open('categories.dat', 'w').close()
    categoriesOutput= open('categories.dat', 'a')
    for category in categoryDict:
        line = ""
        for item in categoryDict[category]['Items']:
            line += str(item)+'|'+str(category)+'\n'
        categoriesOutput.write(line)
    categoriesOutput.close()
       
    

"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
        sys.exit(1)

    for f in argv[1:]:
        if isJson(f):
            parseJson(f)
            print("Success parsing " + f)
            
    writeUsers()
    writeItems()
    writeBids()
    writeCategories()

if __name__ == '__main__':
    main(sys.argv)
