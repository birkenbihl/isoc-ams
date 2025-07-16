#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""local app to access the ISOC.ORG AMS system.
This app uses the isoc_de_ams module which provides the followin functions/properties:
    members
        a list of registered members from the local membership administration system
        items have the format (isoc-id, {firstname: ..., lastname: ..., email: ...})
    applications
        a list of people that have been invited for a chapter membership from the local administration system
        items have the format (isoc-id, {firstname: ..., lastname: ..., email: ...})
    in_negotiations
        a list of people that have filled an application form for a chapter membership from the local administration system
        items have the format (isoc-id, {firstname: ..., lastname: ..., email: ...})
    ams_credentials
        credentials needed to access the ISOC.ORG AMS
    last_call
        date of last sendout of invitations
    ams_support
        email of AMS support (default: amshelp@isoc.org)
    invite(isoc-id, {firstname: ..., lastname: ..., email: ...})
        send an invitation to people who applied, set new last_call
    mail_to_ams_support(list_of_members_to_add_to_ams)
        send a list of chapter members to be added to the ISOC.ORG AMS
"""

import isoc_de_ams as isoc_de  # this is an interface similar to isoc_ams (but lightning fast and reliable)
from isoc_ams import ISOC_AMS  # the ISOC_AMS class will do the job
import isoc_ams
import os
from datetime import datetime


global ams # the instatiation of the ISOC_AMS class.

####################################################################
# for tests we use this instead of the default amshelp@isoc.org
# isoc_de.ams_support = "klaus@zu-dumm.de"
################################### test ###########################

# we don't log to console if we run as cron job
logfile = os.environ["HOME"] + "/isoc-ams-logs/" + \
          datetime.now().date().isoformat() + ".log"


def process_pendings():  # process pending applications sorting them into 4 lists
    actions = {
        "deny": {},      # list of applications to deny
        "approve": {},   # list of applications to approve
        "invite": {},    # list of applications to invite to become a Chapter member
        "noop": {}       #  list of applications to leave as it is
        }
    for idx, pending in ams.pending_applications_list.items():  # walk through AMS pending applications
        if idx in isoc_de.members.keys():                       # if we have registered them as our member
            actions["approve"][idx] = pending                   # we can approve them on AMS
        elif idx in isoc_de.in_negotiations.keys() or \
                 idx in isoc_de.applications.keys():            # if we are negotiating with them
                                                                # or they are in our local pendings list
            actions["noop"][idx] = pending                      # do nothing
        elif idx not in isoc_de.in_negotiations.keys():         # if we are not in negotiations with them
            if pending["date"] < isoc_de.last_call:             # and they received an invitation before
                actions["deny"][idx] = pending                  # we should deny membership
            else:                                               # else they did not get ann invitation before
                actions["invite"][idx] = pending                # they should be invited
    return actions

def process_members():   # compare local list of members with AMS sorting them into 3 lists
    actions = {
        "delete": {},    # delete member from AMS
        "add": {},       # ask ams-support to add this ISOC.ORG member as a Chapter member
        "noop": {}       # all fine, nothing to change
        }
    for idx, member in ams.members_list.items():                # walk through AMS Chapter members list
        if idx in list(isoc_de.members.keys()):                 # if member is registered locally
            actions["noop"][idx] = member                       # we are fine
        else:                                                   # otherwise
            actions["delete"][idx] = member                     # it is no Chapter member - so delete it from AMS list
    for idx, member in isoc_de.members.items():                 # walk through local Chapter members list
        if idx not in ams.members_list.keys() and \
            idx not in ams.pending_applications_list.keys():    # if member is not registered as Chapter member with AMS
                                                                # and not on AMS pending applications list
            actions["add"][idx] = member                        # we ask AMS_support to add member as Chapter member
    return actions



def main(dryrun, headless):    # dryrun will only build the lists but will not really start actions
                               # headless controls weather the browser window will be opened
    global ams

    ams = ISOC_AMS(
                   *isoc_de.ams_credentials,
                   headless=headless,
                   logfile=sys.stdout,
                   debuglog=logfile,
                   dryrun=dryrun)                             # instantiate ISOC_AMS instance

    pendings_operations = process_pendings()                    # build lists for pending applications actions
    members_operations = process_members()                      # build lists for members actions

    #
    # print the lists for pending applications actions
    #
    isoc_ams.strong_msg("Pending Applications:")
    isoc_ams.log("\n   the following pending applications will be approved:", date=False)
    for k, v in pendings_operations["approve"].items():
        isoc_ams.log("        ", v["name"], v["email"],
              v["date"].date().isoformat(), "("+k+")", date=False)
    isoc_ams.log("\n   the following pending applications will be denied:", date=False)
    for k, v in pendings_operations["deny"].items():
        isoc_ams.log("        ", v["name"], v["email"],
              v["date"].date().isoformat(), "("+k+")", date=False)
    isoc_ams.log("\n   the following pending applications will be invited:", date=False)
    for k, v in pendings_operations["invite"].items():
        isoc_ams.log("        ", v["name"], v["email"],
              v["date"].date().isoformat(), "("+k+")", date=False)
    isoc_ams.log("\n   the following pending applications will be waiting:", date=False)
    for k, v in pendings_operations["noop"].items():
        isoc_ams.log("        ", v["name"], v["email"],
              v["date"].date().isoformat(), "("+k+")", date=False)
    #
    # print the lists for members actions
    #
    isoc_ams.strong_msg("Members:")
    isoc_ams.log("\n   the following members will be deleted from AMS:", date=False)
    for k, v in members_operations["delete"].items():
        isoc_ams.log("        ", v["first name"], v["last name"], v["email"], "("+k+")", date=False)
    isoc_ams.log("\n   for the following members a nagging mail will be sent to AMS-support (we are not authorized to fix it!):", date=False)
    for k, v in members_operations["add"].items():
        isoc_ams.log("        ", v["first name"], v["last name"], v["email"], "("+k+")", date=False)
    isoc_ams.log("\n   the following locally registered members are in sync with AMS:", date=False)
    # too many to print ...
    isoc_ams.log("   ...  too many to print", date=False)
    # ... uncomment below if not
    # for k, v in members_operations["noop"].items():
    #     isoc_ams.log("        ", v["first name"], v["last name"], v["email"], "("+k+")", date=False)

    #
    # operations on AMS system (will handle dry runs on its own)
    #
    if pendings_operations["approve"]:
        ams.approve_pending_applications(pendings_operations["approve"])

    if pendings_operations["deny"]:
        ams.deny_pending_applications(pendings_operations["deny"])

    if members_operations["delete"]:
        ams.delete_members(members_operations["delete"])

    #
    # other operations
    #

    if not dryrun:

        if pendings_operations["invite"]:
            for k, v in pendings_operations["invite"].items():
                isoc_de.invite(k, v)            # send an invitation mail

        if members_operations["add"]:
            # send a mail to ams_support to ask to have this list added to AMS Chapters members
            isoc_de.mail_to_ams_support(members_operations["add"])

    #
    # check if AMS operations had the expected result
    #
    r = ams.difference_from_expected()  # returns 3 lists - after an unreasonable time again:
                                        # not deleted from members
                                        # not approved from pending applicants list": not_approved,
                                        # not removed from pending applicants list"
        # if these lists are empty - we are done
        # otherwise here is what went wrong

    if type(r) is not str:
        for data in r.items():
            if data[1]:
                isoc_ams.log(data[0])
                for k, v in data[1].items():
                    if "members" in data[0]:
                        isoc_ams.log("        ", v["first name"],
                                     v["last name"],
                                     v["email"], "("+k+")",
                                     date=False)
                    else:
                        isoc_ams.log("        ", v["name"],
                                     v["email"], "("+k+")",
                                     date=False)
    else:
        isoc_ams.log(r)

if __name__ == "__main__":
    import sys

    maxargs = 1
    headless = True
    dryrun = False

    if "-d" in sys.argv or "--dry" in sys.argv:
        dryrun = True
        maxargs += 1
    else:
        dryrun=False

    if "-h" in sys.argv or "--head" in sys.argv:
        headless = False
        maxargs += 1
    else:
        headless = True

    if len(sys.argv) > maxargs:
        print("usage:", sys.argv[0], "[-d | --dry] [-h | --head]")
        print("      ", "-d | --dry   dry run")
        print("      ", "-h | --head  don't run headless")

    else:
        main(dryrun, headless)
