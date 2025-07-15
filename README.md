
# isoc-ams

A Python Interface to access the 'Advanced Members Administration System' (AMS) of the 'Internet Society' (ISOC). This is especially useful for ISOC Chapter Admins who want to synchronize their Chapter Database with AMS (semi)automatically.

After 10 years+  of sorrow, millions minutes of waiting for answers from the AMS web interface, tons of useless clicks, many (in fact) rejected requests to provide an API access: the author decided to build an API himself. Even if it might not be more than a demonstrator for the functionality needed. Anyhow (see below): for now it is running on a weekly basis doing a great job in avoiding manual work. 

Unfortunately the constraints are severe:
- access had to be through the web interface since this is the only interface provided. As a consequence it is slow, sometimes unreliable and hard to implement. At least there are working implementations of the "W3C web driver" recommendation. One of them is Selenium used for this project.
- the existing web interface is far from being stable or guaranteed. So changes to the web interface might spoil the whole project. There is great chance that few weeks from now a new "super duper" AMS will be announced and as always after these announcements things will get worse.
- tests are close to impossible. There is no such thing as a TEST AMS.

Is there a possible good exit? Well, maybe some day soon - in 10 or 20 years if ISOC still exists - there will be an API provided by ISOC that makes this project obsolete. Or at least may be an all-mighty AI will step in. Let's dream on!

Status quo: after some experiments with timings isoc-ams seems to run fairly stable for now. The main problem: it takes a lot of time. Not so much an issue if you run it unattended.

## Features
AMS maintains two main Lists that are relevant for the operation of this interface: 
- a list of ISOC members registered as members of the Chapter
- a list of ISOC members that applied for a Chapter membership.
  
Consequently isoc-ams provides methods for the following tasks:
1. read list of ISOC members registered as Chapter members
1. read list of ISOC members that applied for a Chapter membership
1. approve ISOC AMS applications
1. deny ISOC AMS applications
1. delete members from ISOC AMS Chapters Member list
1. add members to  ISOC AMS Chapters Member list (Chapter admins are not authorized to do this. So the author suggests to write a mail to ams-support.)

Don't forget: it takes time and you may see many kinds of errors. Often the cure is "try again later". Any expectation of flawless is not appropriate.
Anyhow, after running it some time now it seems to work better than expected.
So here we go:

## Installation

Install (or update) isoc-ams with pip.

```bash
  python -m pip install -U isoc-ams
```

Recommended to use a virtual environment (venv).

## Running isoc_ams

### Choosing a Webdriver
You may select a Webdriver of your choice (provided it is one of "firefox" or "chrome") by setting an environment variable ISOC_AMS_WEBDRIVER e.g.:
```bash
ISOC_AMS_WEBDRIVER=firefox
```
Recommended (and default) is "firefox".
### Start execution of the module
So this happens if we call the module with:
```bash
python -m isoc_ams
```
Output:
```
Username:xyz
Password: 

************************************* 
2025-07-13 19:25:54 - INFO - START 
************************************* 

2025-07-13 19:25:54 - INFO - logging in 

************************************************************* 
2025-07-13 19:25:59 - ERROR - Invalid username or password. 
************************************************************* 
```
OK, probably your fault. After fixing:
```
Username: xxx
Password: 

************************************* 
2025-07-13 19:26:27 - INFO - START 
************************************* 

2025-07-13 19:26:27 - INFO - logging in 
2025-07-13 19:26:45 - INFO - Now on Chapter Leader portal 


2025-07-13 19:26:45 - INFO - start build members list 
2025-07-13 19:27:36 - INFO - members list finished /  59 collected 


2025-07-13 19:27:36 - INFO - start build pending applications 
2025-07-13 19:27:50 - INFO - Pending applications list finished /  8 collected 


*************************************** 
2025-07-13 19:27:50 - INFO - MEMBERS 
*************************************** 
1 22158 ...
2 ...
...

**************************************************** 
2025-07-13 19:27:50 - INFO - PENDING APPLICATIONS 
**************************************************** 
1 2323 ...
2 ...
...
```
As you can see from the time stamps: building the lists is rather tedious. And finding all required info is a bit tricky sometimes.

### Logging
Since crazy things may happen it is important to keep track of what is going on. So ISOC_AMS lets you know what it is doing
by providing a logfile. With the option --debug you will get a more detailed log. Logs usually go to stdout.


### Running with head
Normally isoc_ams won't show any browser output - running headless. To do debugging it might useful to follow the activities in the browser. If you call isoc_ams with a -h option like 
```bash
python -m isoc_ams -h
```
the browser will open and you can follow all activities real time.

### User input and Dryrun
An argument -i tells the module that there will be (or is) input available with actions to execute.
An argument -d  tells isoc_ams to make a dry run. Actions will be computed but not executed.

Again an example:
```bash
python -m isoc_ams -i -d
```
Output:
```
Username: xxx
Password: 

******************************************** 
2025-07-15 10:35:57 - INFO - START DRYRUN 
******************************************** 

2025-07-15 10:35:57 - INFO - logging in 
2025-07-15 10:36:12 - INFO - Now on Chapter Leader portal 


2025-07-15 10:36:12 - INFO - start build members list 
2025-07-15 10:37:03 - INFO - members list finished /  59 collected 


2025-07-15 10:37:03 - INFO - start build pending applications 
2025-07-15 10:37:17 - INFO - Pending applications list finished /  9 collected 


*************************************** 
2025-07-15 10:37:17 - INFO - MEMBERS 
*************************************** 
1 2217734 Johannes Piesepampel self@piesepampel.com
...

**************************************************** 
2025-07-15 10:37:17 - INFO - PENDING APPLICATIONS 
**************************************************** 
1 23232 Franz Piesepampel franz@piesepampel.com 2025-01-22
2 22556 Abdul Piesepampel abdul@piesepampel.com 2025-03-21
...
READING COMMANDS:
```
*`  deny 23232 22556 123`*
```
2025-07-15 10:38:17 Denied 23232 Franz Piesepampel
2025-07-15 10:38:17 Denied 22556 Abdul Piesepampel
*******************************************************************************
2025-07-15 10:38:17 ISOC-ID 123 is not in pending applications list
*******************************************************************************
```
*`  delete 2217734`*
```
2025-07-15 10:38:59 Deleted 2217734 Johannes Piesepampel
2025-07-15 10:37:17
```

The following commands are available:
* deny (followed by a comma or space separated list of ISOC-IDs):
    deny Chapter membership for these applicants
* approve (followed by a comma or space separated list of ISOC-IDs):
    approve Chapter membership for these applicants
* delete (followed by a comma or space separated list of ISOC-IDs):
    delete these members from the Capter members list

## Using the API

isoc_ams unleashes its full power when used as API to make things happen without human intervention. Check the file "[isoc_de_ams_main.py](https://github.com/birkenbihl/isoc-ams/blob/main/isoc_de_ams_main.py)" as an example for fully automatic synchronizing of local membership administration with AMS.

Here the output:
```

************************************* 
2025-07-15 14:13:36 - INFO - START 
************************************* 

2025-07-15 14:13:36 - INFO - logging in 
2025-07-15 14:13:53 - INFO - Now on Chapter Leader portal 


2025-07-15 14:13:53 - INFO - start build members list 
2025-07-15 14:14:44 - INFO - members list finished /  59 collected 


2025-07-15 14:14:44 - INFO - start build pending applications 
2025-07-15 14:14:57 - INFO - Pending applications list finished /  8 collected 

2025-07-15 14:14:57 - INFO - Pending Applications: 

   the following pending applications will be approved: 
         ...
         
   the following pending applications will be denied: 
         ...

   the following pending applications will be invited: 
         ...

   the following pending applications will be waiting: 
         ...

2025-07-15 14:14:57 - INFO - Members: 

   the following members will be deleted from AMS: 
         ...

   for the following members a nagging mail will be sent to AMS-support (we are not authorized to fix it!): 
         ...

   the following locally registered members are in sync with AMS: 
         ... 

2025-07-15 14:14:57 - INFO - start delete ...
2025-07-15 14:15:10 - INFO - done 
2025-07-15 14:15:10 - INFO - Deleted 233658 ...


************************************************************************* 
2025-07-15 14:15:10 - INFO - Check if actions ended up in AMS database 
************************************************************************* 
2025-07-15 14:15:10 - INFO - we have to read the AMS Database tables again to find deviations from expected result after actions :( 
 

2025-07-15 14:15:10 - INFO - start build members list 
2025-07-15 14:15:56 - INFO - members list finished /  59 collected 


2025-07-15 14:15:56 - INFO - start build pending applications 
2025-07-15 14:16:06 - INFO - Pending applications list finished /  8 collected 

2025-07-15 14:16:06 - INFO - everything OK
```

The mail to be send to AMS-support team might look like this:

Dear AMS-support team,

this is an automatic, complimentary Message from the ISOC German Chapter
Members Administration System (ISOC.DE MAS).

Assuming you are interested in making ISOC AMS consistent, the purpose
of this message is to help you with valid, up-to-date data.

The following individuals are legally registered paying members
of ISOC.DE - many of them for more than 25 years. They all are
also registered as ISOC (global) members. Unfortunately they are
not registered with AMS as members of ISOC.DE. Even more we are
not authorized to fix this. So we forward this data to your attention:

   Uwe Mayer, xxx@yyy.com (ISOC-ID=1234567)
   ...
   
Thank you,

Your ISOC.DE MAS support team

See file [isoc_ams.html](https://html-preview.github.io/?url=https://github.com/birkenbihl/isoc-ams/blob/main/isoc_ams.html) for doc on the API interface.

