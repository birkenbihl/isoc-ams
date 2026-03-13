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
from datetime import timedelta
import isoc_ams
import logging


global ams # the instatiation of the ISOC_AMS class.

# we don't log to console if we run as cron job
logfile = isoc_de.logfile

def pendings_heuristics(pending):
    for isoc_id, r in isoc_de.members.items():
        if r["email"].lower() == pending["email"].lower():
            return r["mitgliedsnummer"], isoc_id
        if r["last name"].lower() in pending["name"].lower() and \
           r["first name"].lower() in pending["name"].lower():
            return r["mitgliedsnummer"], isoc_id
    for (mn, r) in isoc_de.no_ids.items():
        if r["email"].lower() == pending["email"].lower():
            return mn, None
        if r["last name"].lower() in pending["name"].lower():
            return mn, None
    return None

def member_heuristics(member):
    for isoc_id, r in isoc_de.members.items():
        if r["email"].lower() == member["email"].lower():
            return r["mitgliedsnummer"], isoc_id
        if r["last name"].lower() == member["last name"].lower() and \
           r["first name"].lower() in member["first name"].lower():
            return r["mitgliedsnummer"], isoc_id
    for (mn, r) in isoc_de.no_ids.items():
        if r["email"].lower() == member["email"].lower():
            return mn, None
        if r["last name"].lower() in member["last name"].lower():
            return mn, None
    return None

def noupdate_for(liste, idx, k):
    for i, v in liste.items():
        if v[k] == idx:
            return False
    return True


def process_pendings():  # process pending applications sorting them into 4 lists
    actions = {
        "deny": {},      # list of applications to deny
        "approve": {},   # list of applications to approve
        "invite": {},    # list of applications to invite to become a Chapter member
        "update_id": {}, # list of recovered isoc-ids
        "noop": {}       #  list of applications to leave as it is
        }
    for idx, pending in ams.pending_applications_list.items():  # walk through AMS pending applications
        if idx in isoc_de.members.keys():                       # if we have registered them as our member
            actions["approve"][idx] = pending                   # we can approve them on AMS

        elif r := pendings_heuristics(pending):                # if we have no ISOC-ID
            actions["approve"][idx] = pending
            actions["update_id"][idx] = r[0], r[1]

        elif idx in isoc_de.in_negotiations.keys() or \
                 idx in isoc_de.applications.keys():            # if we are negotiating with them
                                                                # or they are in our local pendings list
            actions["noop"][idx] = pending                      # do nothing
        elif idx not in isoc_de.in_negotiations.keys():         # if we are not in negotiations with them
            if pending["date"] + timedelta(1) < isoc_de.last_call:  # and they received an invitation before
                                                                # pending dates are now time 00:00:00
                                                                # so people may have registered up to 1 day
                                                                # this time and maybe last invitation
                actions["deny"][idx] = pending                  # we should deny membership
            else:                                               # else they did not get ann invitation before
                actions["invite"][idx] = pending                # they should be invited
    return actions



def process_members():   # compare local list of members with AMS sorting them into 3 lists

    actions = {
        "delete": {},    # delete member from AMS
        "add": {},       # ask ams-support to add this ISOC.ORG member as a Chapter member
        "update_id": {}, # list of recovered isoc-ids
        "noop": {},       # all fine, nothing to change
        }
    for idx, member in ams.members_list.items():                # walk through AMS Chapter members list
        if idx in list(isoc_de.terminated_members.keys()):
              actions["delete"][idx] = member

    for idx, member in ams.members_list.items():                # walk through AMS Chapter members list
        if idx in list(isoc_de.members.keys()):                 # if member is registered locally
            actions["noop"][idx] = member                       # we are fine
            if idx in actions["delete"]:
                actions["delete"].pop(idx)
        elif r := member_heuristics(member):
            actions["update_id"][idx] = r[0], r[1]
            if idx in actions["delete"]:
                actions["delete"].pop(idx)
        else:                                           # otherwise
            actions["delete"][idx] = member                     # it is no Chapter member - so delete it from AMS list

    for idx, member in isoc_de.members.items():                 # walk through local Chapter members list
        if idx not in ams.members_list and \
            idx not in ams.pending_applications_list and \
                noupdate_for(actions["update_id"], idx, 1):                          # if member is not registered as Chapter member with AMS
                                                            # and not on AMS pending applications list
            actions["add"][idx] = member                    #
    return actions


def main(
         headless=True,
         dryrun=None,
         logfile="stdout",
         debuglog=None,
         offline=None,
         export=None,
         driver='firefox'):

    global ams

    ams = ISOC_AMS(
                   *isoc_de.ams_credentials,
                   headless=headless,
                   logfile=sys.stdout,
                   debuglog=debuglog,
                   dryrun=dryrun,
                   driver=driver,
                   offline=offline,
                   export=export)                             # instantiate ISOC_AMS instance

    if ams.pending_applications_list is not None:
        pendings_operations = process_pendings()              # build lists for pending applications actions
    else:
        pendings_operations = None
    if ams.members_list is not None:
        members_operations = process_members()
                               # headless controls            # build lists for members actions
    else:
        members_operations = None

    #
    # print the lists for pending applications actions
    #
    if pendings_operations is not None:
        isoc_ams.strong_msg("Pending Applications:", date=False)

        isoc_ams.log("\n   the following pending applications will be approved:", date=False)
        if pendings_operations["approve"]:
            for k, v in pendings_operations["approve"].items():
                isoc_ams.log("        ", v["name"], v["email"],
                      v["date"].date().isoformat(), "("+k+")", date=False)
        else:
            isoc_ams.log("        ","*** None ***", date=False)

        isoc_ams.log("\n   the following pending applications will be denied:", date=False)
        if pendings_operations["deny"]:
            for k, v in pendings_operations["deny"].items():
                isoc_ams.log("        ", v["name"], v["email"],
                      v["date"].date().isoformat(), "("+k+")", date=False)
        else:
            isoc_ams.log("        ","*** None ***", date=False)

        isoc_ams.log("\n   the following pending applications will be invited:", date=False)
        if pendings_operations["invite"]:
            for k, v in pendings_operations["invite"].items():
                isoc_ams.log("        ", v["name"], v["email"],
                      v["date"].date().isoformat(), "("+k+")", date=False)
        else:
            isoc_ams.log("        ","*** None ***", date=False)

        isoc_ams.log("\n   the following pending applications will be waiting:", date=False)
        if pendings_operations["noop"]:
            for k, v in pendings_operations["noop"].items():
                isoc_ams.log("        ", v["name"], v["email"],
                      v["date"].date().isoformat(), "("+k+")", date=False)
        else:
            isoc_ams.log("        ","*** None ***", date=False)

        isoc_ams.log("\n   for the following members we guessed the isoc-id:", date=False)
        if pendings_operations["update_id"]:
            for k, v in pendings_operations["update_id"].items():                # k == (mitgliedsnummer, alte ISOC-ID)
                isoc_ams.log(f"         {v[0]} {k} ({v[1] or ''}) {ams.pending_applications_list[k]['name']}", date=False) # k == new ISOC-ID
        else:
            isoc_ams.log("        ","*** None ***", date=False)

    else:
        isoc_ams.strong_msg("No Pending Applications actions", level=logging.ERROR)
    #
    # print the lists for members actions
    #
    if members_operations is not None:
        isoc_ams.strong_msg("Members:", date=False)

        isoc_ams.log("\n   the following members will be deleted from AMS:", date=False)
        if members_operations["delete"]:
            for k, v in members_operations["delete"].items():
                isoc_ams.log("        ", v["first name"], v["last name"], v["email"], "("+k+")", date=False)
        else:
            isoc_ams.log("        ","*** None ***", date=False)

        isoc_ams.log("\n   the following members are not registered Chapter members with AMS", date=False)
        if members_operations["add"]:
            for k, v in members_operations["add"].items():
                isoc_ams.log("        ", v["first name"], v["last name"], v["email"], "("+k+")", date=False)
        else:
            isoc_ams.log("        ","*** None ***", date=False)

        isoc_ams.log("\n   for the following members we guessed the isoc-id:", date=False)
        if members_operations["update_id"]:
            for k, v in members_operations["update_id"].items():                # k == (mitgliedsnummer, alte ISOC-ID)
                isoc_ams.log(f"         {v[0]} {k} ({v[1] or ''}) {ams.members_list[k]['first name']} {ams.members_list[k]['last name']}", date=False) # k == new ISOC-ID
        else:
            isoc_ams.log("        ","*** None ***", date=False)

        isoc_ams.log("\n   for the following members we miss an ISOC-ID:", date=False)
        if isoc_de.no_ids:
            for k, v in isoc_de.no_ids.items():
                if noupdate_for(members_operations["update_id"], k, 0):
                    isoc_ams.log("        ", k, v["first name"], v["last name"], v["email"], date=False)
        else:
            isoc_ams.log("        ","*** None ***", date=False)


        isoc_ams.log("\n   the following locally registered members are in sync with AMS:", date=False)
        # too many to print ...
        isoc_ams.log("   ...  too many to print", date=False)
        # ... uncomment below if not
        # for k, v in members_operations["noop"].items():
        #     isoc_ams.log("        ", v["first name"], v["last name"], v["email"], "("+k+")", date=False)
    else:
        isoc_ams.strong_msg("No actions on Members due to previous error", level=logging.ERROR)

    #
    # operations on AMS system (will handle dry runs on its own)
    #
    if pendings_operations is not None:
        if pendings_operations["approve"]:
            ams.approve_pending_applications(pendings_operations["approve"])

        if pendings_operations["deny"]:
            ams.deny_pending_applications(pendings_operations["deny"])

    if members_operations is not None:
        if members_operations["delete"]:
            ams.delete_members(members_operations["delete"])


    #
    # other operations
    #

    if not ams.dryrun:
        if pendings_operations is not None:
            if pendings_operations["invite"]:
                for k, v in pendings_operations["invite"].items():
                    isoc_de.invite(k, v)            # send an invitation mail

        m = { **pendings_operations["update_id"], **members_operations["update_id"] }
        print(m)
        if m:
            isoc_de.set_isoc_ids(m)

        # if members_operations is not None:
        #     if members_operations["add"] and amsmail:
        #         # send a mail to ams_support to ask to have this list added to AMS Chapters members
        #         isoc_de.mail_to_ams_support_or_us(members_operations["add"], isoc_de.no_ids)

    #
    # check if AMS operations had the expected result
    #

    if members_operations is not None and pendings_operations is not None:
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
    else: ams.strong_msg("Results cannot be verified due to previous errors", level=logging.ERROR)

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("-h", "--head", help='show browser window', action='store_true')
    parser.add_argument("-d", "--dryrun", help='just run without modifying any data', action='store_true')
    parser.add_argument("--debuglog", help='file for detailed log')
    parser.add_argument("--logfile", help='file for log', default="stdout")
    parser.add_argument("-e", "--export", help='output AMS data to this JSON file and exit')
    parser.add_argument("-o", "--offline", help='read (fake) AMS data from this JSON file and run dry')
    parser.add_argument("--driver", help='Selenium driver', choices=["firefox", "chrome"], default="firefox")
    parser.add_argument("--help", help='Show this help',  action='store_true')

    args = parser.parse_args()
    if args.help:
        parser.print_help()
        sys.exit(0)


    else:

        main(
             headless=not args.head,
             dryrun=args.dryrun,
             logfile=args.logfile,
             debuglog=args.debuglog,
             offline=args.offline,
             export=args.export,
             driver=args.driver.lower(),
             )
