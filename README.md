
# isoc-ams

A Python Interface to access the 'Advanced Members Administration System' (AMS) of the 'Internet Society' (ISOC). This especially usefulfor ISOC Chapter Admins who want to synchronize their Chapter Database with AMS (semi)automatically.

After 10 years+  of sorrow, millions minutes of waiting for answers from the AMS web interface, tons of useless clicks, many (in fact) rejected requests to provide an API access: the author decided to build an API himself. Even if it might not be more than a demonstrator for the functionality needed. Anyhow (see below): for now it is running on a weekly basis doing a great job in avoiding manual work. 

Unfortunately the constraints are severe:
- access had to be through the web interface since this is the only interface provided. As a consequence it is slow, sometimes unreliable and hard to implement. At least there are working implementations of the "W3C webdriver" recommendtion. One of them is Selenium used for this project.
- the existing web interface is far from being stable or guarateed. So changes to the web interface might spoil the whole project. There is great chance that few weeks from now a new "super dooper" AMS will be announced and as always after these announcements things will get worse.
- tests are close to impossible. There is no such thing as a TEST AMS.

Is there a possible good exit? Well, maybe some day soon - in 10 or 20 years if ISOC still exists - there will be an API provided by ISOC that makes this project obsolete. Or at least may be an all-mighty AI will step in. Let's dream on!

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

Don't forget: it takes time and you may see many kinds of errors. Often the cure is "try again later". Any expectation of flawless is not appropriate.

So here we go:

## Installation

Install isoc-ams with pip.

```bash
  python -m pip install -U isoc-ams
```

Best would be to use a virtual environment (venv).

## Running isoc_ams

You may select a webdriver of your choice (provided it is one of "firefox" or "chrome") by setting an environment variable ISOC_AMS_WEBDRIVER e.g.:
```bash
ISOC_AMS_WEBDRIVER=firefox
```
Recommended (and default) is "firefox".

Since crazy things may happen it is important to keep track of what is going on. So ISOC_AMS lets you know what it is doing.
by providing a logfile (goes to stdout by default).

So this happens if we call the module with:
```bash
python -m isoc_ams
```

```
Username: xxx
Password: 

AMS 2025-07-03 10:49:07 logging in
AMS 2025-07-03 10:49:11 log in started
AMS 2025-07-03 10:49:20 now on community portal
AMS 2025-07-03 10:49:25 waiting for Chapter Leader portal
AMS 2025-07-03 10:49:27 Chapter Leader portal OK


AMS 2025-07-03 10:49:27 start build members list
AMS 2025-07-03 10:49:27 Creating page for Members
AMS 2025-07-03 10:49:33 Members page created
AMS 2025-07-03 10:49:33 Loading Members
AMS 2025-07-03 10:49:39 got list of Members
AMS 2025-07-03 10:49:39 collecting the following fields: "ISOC-ID", "first name", "last name", "email"
AMS 2025-07-03 10:49:39 Total (records expected): 38
AMS 2025-07-03 10:49:39 Waiting for Total to stabilise
AMS 2025-07-03 10:49:42 Total (records expected): 59
AMS 2025-07-03 10:49:45 calling reader with 31 table rows,  (collected records so far: 0 )
AMS 2025-07-03 10:49:50 calling reader with 32 table rows,  (collected records so far: 29 )
AMS 2025-07-03 10:49:54 calling reader with 24 table rows,  (collected records so far: 53 )
AMS 2025-07-03 10:49:55 records collected / total 59  / 59
AMS 2025-07-03 10:49:55 Creating page for Member Contacts
AMS 2025-07-03 10:50:00 Member Contacts page created
AMS 2025-07-03 10:50:00 Loading Member Contacts
AMS 2025-07-03 10:50:04 got list of Member Contacts
AMS 2025-07-03 10:50:04 collecting the following fields: "action link" (for taking actions), "email" (to connect with members list)
AMS 2025-07-03 10:50:04 Total (records expected): 8
AMS 2025-07-03 10:50:04 Waiting for Total to stabilise
AMS 2025-07-03 10:50:07 Total (records expected): 59
AMS 2025-07-03 10:50:10 calling reader with 30 table rows,  (collected records so far: 0 )
AMS 2025-07-03 10:50:14 calling reader with 31 table rows,  (collected records so far: 28 )
AMS 2025-07-03 10:50:18 calling reader with 25 table rows,  (collected records so far: 51 )
AMS 2025-07-03 10:50:18 records collected / total 59  / 59
AMS 2025-07-03 10:50:18 members list finished


AMS 2025-07-03 10:50:18 start build pending applications
AMS 2025-07-03 10:50:18 Creating page for Pending Applications
AMS 2025-07-03 10:50:22 collecting the following fields: "name", "email", "action link", "date"
AMS 2025-07-03 10:50:24 Total (records expected): 8
AMS 2025-07-03 10:50:24 Waiting for Total to stabilise
AMS 2025-07-03 10:50:27 Total (records expected): 8
AMS 2025-07-03 10:50:30 calling reader with 8 table rows,  (collected records so far: 0 )
AMS 2025-07-03 10:50:31 records collected / total 8  / 8
AMS 2025-07-03 10:50:31 pending application list finished


MEMBERS
1 ...
2 ...
...

PENDING APPLICATIONS
1 ...
2 ...
...
```

Normally isoc_ams wont show any browser output - running headless. To do debugging it might useful to follow the activities in the browser. If you call isoc_ams with a -h option the browser will open.

## Using the API

isoc_ams unleashes its full power when used as API to make things happen without human intervention. Check the file "isoc_de_ams_main.py" as an example for fully automatic synchronizing of local membership administration with AMS.

Here an excerpt of the output:
```
Pending Applications:

   the following pending applications will be approved:
   ...
   the following pending applications will be denied:
   ...
   the following pending applications will be invited:
   ...
   the following pending applications will be waiting:
   ...

Members:
   the following members will be deleted from AMS:
   ...
   for the following members a nagging mail will be sent to AMS-support (we are not authorized to fix it!):
   ...
   the following members are in sync
   ...
      
AMS 2025-07-03 12:00:32 start delete ... from AMS Chapter members list
   ...

Dear MAS-support team,
this is an automatic, complimentary Message from the ISOC German Chapter
Members Administration System (ISOC.DE MAS).

The following individuals are legally registered paying members
of ISOC.DE - many of them for more than 25 years.
...
   Uwe Mayer, xxx@yyy.com (ISOC-ID=1234567)
   ...
   
Thank you,
Your ISOC.DE MAS support team
...

DEVIATIONS FROM EXPECTED RESULTS
not deleted from members
...
not approved from pending applicants list
...
not removed from pending applicants list
...
```
See file isoc_ams.doc for doc on the API interface.

Have fun!
