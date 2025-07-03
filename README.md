
# isoc-ams

A Python Interface to access the 'Advanced Members Administration System' (AMS) of the 'Internet Society' (ISOC). This especially usefulfor ISOC Chapter Admins who want to synchronize their Chapter Database with AMS (semi)automatically.

After 10 years+  of sorrow, millions minutes of waiting for answers from the AMS web interface, tons of useless clicks, many (in fact) rejected requests to provide an API access: the author decided to build an API himself.

Unfortunately the constraints are severe:
- access had to be through the web interface since this is the only interface provided. As a consequence it is slow, sometimes unreliable and hard to implement. At least there are working implementations of the "W3C webdriver" recommendtion. One of them is Selenium used for this project.
- the existing web interface is far from being stable or guarateed. So changes to the web interface may spoil
the whole project.

So maybe some day soon - in 10 or 20 years - if ISOC still exists there will be an API provided by ISOC that makes this project obsolete.

## Features
ISOC maintains two main Lists that are relevant for the operation of this interface: 
- a list of ISOC members registered as members of the Chapter
- a list of ISOC members that applied for a Chapter membership.
  
Consequently isoc-ams provides methods for the following tasks:
1. read list of ISOC members registered as Chapter members
1. read list of ISOC members that applied for a Chapter membership
1. approve ISOC AMS applications
1. deny ISOC AMS applications
1. delete members from ISOC AMS Chapters Member list
1. add members to  ISOC AMS Chapters Member list (Chapter admins are not authorized to do this. So the author suggest to write a mail to ams-support.)

Don't forget: it takes time and you may see many kinds of errors. Often the cure is "try again later".

## Installation

Install isoc-ams with pip.

```bash
  python -m pip -U isoc-ams
```

## Usage/Examples
Print a list of ISOC members registered as chapter members.

```python
from isoc_ams import ISOC_AMS

userid, password = "myuserid", "mysecret"

# this will log you in
# and instantiate an ISOC_AMS object
ams = ISOC_AMS(userid, password)

# will read the list of members,
# registered as chapters members
members = ams.build_members_list()

for isoc_id, member in members.items():
    print(isoc_id,
          member["first name"],
          member["last name"],
          member["email"],
         )

```
You may select a webdriver of your choice (provided it is one of "firefox" or "chrome") by setting an environment variable SELENIUM_DRIVER e.g.:
```bash
SELENIUM_DRIVER=firefox
```
Recommended is  firefox.
Recommended (and default) is "firefox".

