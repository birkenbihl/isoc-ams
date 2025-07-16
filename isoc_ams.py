#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""Extract or modify Chapter Data of the ISOC AMS (Salesforce) Database.

DESCRIPTION

    This module consists of a Class ISOC_AMS wrapping _ISOC_AMS which subclasses
    the webdriver.<browser> of Selenium. Up to now ownly firefox and chrome
    drivers are implemented and tested.

CLASS
    PROPERTIES
        The ISOC_AMS class provides the following properties:
            members_list:
                a list of Chapter members (according to AMS) with data (and links)
            pending_applicants_list:
                a list of pending appplicants  (according to AMS) for a Chapter
                membership with data (and links)
        these properties are initialized after login ... and this will take time

    METHODS
        The ISOC_AMS class provides the following methods:
            build_members_list:
                to build a list of Chapter members with data (and links)
            build_pending_applicants_list:
                to build a list of pending appplicants for a Chapter membership with
                data (and links)
            deny_applicants:
                to deny Chapter membership for a list of applicants
            approve_applicants:
                to approve Chapter membership for a list of applicants
            delete_members:
                to revoke Chapter membership for members from the members list
            difference_from_expected:
                to reread AMS and check if all operations were successfull (not ever
                problem can be detected by the methods)

    ISOC_AMS will log you in to ISOC.ORG and check your authorization at
    instantiation.

    To select a webdriver, an ISOC_AMS_WEBDRIVER environment variable can be used.
    E.g.
        ISOC_AMS_WEBDRIVER=Firefox

    Default is Firefox. Only Firefox and Chrome are allowed for now.

FUNCTIONS
    3 functions are provided to support logging:
        log, dlog, strong_message
    (see below)

EXAMPLE

        from isoc_ams import ISOC_AMS
        userid, password = "myuserid", "mysecret"

        # this will log you in
        # and instantiate an ISOC_AMS object
        ams = ISOC_AMS(userid, password)

        # this will read the list of members,
        # registered as chapters members
        members = ams.members_list

        # print the results
        for isoc_id, member in members.items():
            print(isoc_id,
                  member["first name"],
                  member["last name"],
                  member["email"],
                 )
        # select members to be deleted
        deletees = <...>  # various formats are allowed for operation methods
        delete_members(deletees)

        # check if all went well
        difference_from_expected()

CHANGELOG
    Version 0.0.2
        Allow input if executed as module
        Add dryrun to ISOC_AMS class
    Version 0.1.0
        Improved logging
        minor bug fixes
    Version 0.1.1
        minor bug fixes
"""
__version__ = "0.1.1"

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import logging

import io
import time
import sys
import os

_logger = logging.getLogger("AMS")
_logger.setLevel(logging.DEBUG)

_dr = os.environ.get("ISOC_AMS_WEBDRIVER", "firefox").lower()

if  _dr == "firefox":
    _options = webdriver.FirefoxOptions()
    Driver = webdriver.Firefox
elif _dr == "chrome":
    _options = webdriver.ChromeOptions()
    Driver = webdriver.Chrome
else:
    sys.exit("Selenium Driver " + _dr + " not implemented.")


def _WaitForTextInElement(element):

    def _predicate(_):
        return element.text
    return _predicate

#
# logging
#

def _init_logging(logfile, debuglog):

    _logger.normalLogFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                               '%Y-%m-%d %H:%M:%S')
    _logger.blankLogFormat = logging.Formatter('%(message)s')

    if type(logfile) is str:
        lfh = logging.FileHandler(logfile)
    elif isinstance(logfile, io.TextIOBase):
        lfh = logging.StreamHandler(logfile)
    elif logfile is None:
        lfh = logging.NullHandler()
    lfh.setLevel(logging.INFO)
    lfh.setFormatter(_logger.normalLogFormat)
    _logger.addHandler(lfh)

    if type(debuglog) is str:
        dlh = logging.FileHandler(debuglog)
    elif isinstance(debuglog, io.TextIOBase):
        dlh = logging.StreamHandler(debuglog)
    elif debuglog is None:
        dlh = logging.NullHandler()
    dlh.setLevel(logging.DEBUG)
    dlh.setFormatter(_logger.normalLogFormat)
    _logger.addHandler(dlh)

#
# utilities
#

def log(*args, date: bool = True, level: int = logging.INFO):
    """Write to log.

ARGUMENTS
        args: tuple of message parts
        level: logging level
        date: if False ommit time and level info in logrecord
    """
    if len(args) > 0:
        msg = (len(args) * "%s ") % args
    else:
        msg = ""
    if date:
        _logger.log(level, msg)
    else:
        for h in _logger.handlers:
            h.setFormatter(_logger.blankLogFormat)
        _logger.log(level, msg)
        for h in _logger.handlers:
            h.setFormatter(_logger.normalLogFormat)

def dlog(*args, date: bool = True):
    """ Short for log(*args, date=True, level=logging.DEBUG)."""
    log(*args, date=True, level=logging.DEBUG)

def strong_msg(*args, date: bool = True, level: int = logging.INFO):
    """Write to log emphasized message.

ARGUMENTS
        args: tuple of message parts
        level: logging level
        date: if False ommit time and level info in logrecord
    """
    x = 0
    for t in args:
        x += len(str(t)) + 1
    x = x + 1 + 30
    log("\n" + x * "*", date=False, level=level)
    log(*args, date=date, level=level)
    log(x * "*", date=False, level=level)



class ISOC_AMS:
    """Perform admin operations on a Chaper's members list stored in AMS.

DESCRIPTION

    This is the main class to interface with the ISOC-AMS system.

    By default all operations run headless. If you want to follow it on
    a browser window use headless=False.

ARGUMENTS
        user: username (email) for ISO.ORG login
        password: password for ISO.ORG login
        logfile: where to write ISOC_AMS info-log output
        debuglog: where to write ISOC_AMS debug-level log output
        headless: run without GUI
        dryrun: only check input, no actions
    """

    def __init__(self,
                 user: str,
                 password: str,
                 logfile: io.TextIOBase | str | None = sys.stdout,
                 debuglog: io.TextIOBase | str | None = None,
                 headless: bool = True,
                 dryrun:  bool = False,):
        if _dr == "firefox" and headless:
            _options.add_argument("--headless")
        elif _dr == "chrome" and headless:
            _options.add_argument("--headless=new")
        self._dryrun = dryrun
        _init_logging(logfile, debuglog)
        self._ams = _ISOC_AMS()
        if self._dryrun:
            strong_msg("START DRYRUN:", "Webdriver is", _dr)
        else:
            strong_msg("START:", "Webdriver is", _dr)
        self._ams.login((user, password))
        self._members_list = self._ams.build_members_list()
        self._pending_applications_list = self._ams.build_pending_applicants_list()


    @property
    def members_list(self) -> dict:
        """Collects data about Chapter members.

DESCRIPTION
        Collects the relevant data about ISOC members
        registered as Chapter members in AMS

RETURNS
            dictionary with the following scheme:
                {<ISOC-ID>:
                     {"first name": <first name>,
                      "last name": <last name>,
                      "email": <Email address>',
                      "action link": <url of page to edit this entry>
                     },
                  ...
                 }

ISOC-ID are used as keys for the entries
        """
        return self._members_list

    @property
    def pending_applications_list(self) -> dict:
        """Collects data about pending Chapter applications.

DESCRIPTION
        Collects the relevant data about pending Chapter applicants
        registered as pending Chapter applicants in AMS

RETURNS
            dictionary with the following scheme:
                {<ISOC-ID>:
                     {"name": <name>,
                      "email": <Email address>',
                      "action link": <url of page to edit this entry>
                      "date": <date of application>
                     },
                  ...
                 }
        ---------------------------------------------
ISOC-ID are used as keys for the entries
        """
        return self._pending_applications_list

    def delete_members(self, delete_list: list | dict | str | int):
        """Delete Member(s) from AMS-list of Chapter members.

DESCRIPTION
    deletes delete_list entries from AMS-list of Chapter members

ARGUMENTS
        delete_list: list of dict-entrys, or ISOC-IDs, or single entry
                         or an ISOC-ID
        """
        if type(delete_list) in (str, int):
            delete_list = [delete_list]
        for deletee in map(str, delete_list):
            if deletee in self._members_list:
                deletee = str(deletee)
                if not self._dryrun:
                    self._ams.delete(self._members_list[deletee])
                log("Deleted", deletee,
                    self._members_list[deletee]["first name"],
                    self._members_list[deletee]["last name"])
                del self._members_list[deletee]
            else:
                log("ISOC-ID", deletee,
                    "is not in AMS Chapter members list",
                    level=logging.ERROR)


    def approve_pending_applications(self, approve_list: list | dict | str | int):
        """Approve pending Members as Chapter members.

DESCRIPTION
    approves pending members on approve_list as Chapter members

ARGUMENTS
        approve_list: list of dict-entrys, or ISOC-IDs, or single entry
                          or ISOC-ID
        """
        if type(approve_list) in (int, str):
            approve_list = [approve_list]
        for approvee in map(str, approve_list):
            if approvee in self._pending_applications_list:
                if approvee not in self._members_list:
                    if not self._dryrun:
                        self._ams.approve(self._pending_applications_list[approvee])
                    log("Approved", approvee,
                        self._pending_applications_list[approvee]["name"])
                    del self._pending_applications_list[approvee]
                else:
                    log(self._pending_applications_list[approvee]["name"],
                        approvee,
                        "not approved - is already registered as member",
                        level=logging.ERROR)
            else:
                log("ISOC-ID", approvee,
                    "is not in pending applications list",
                    level=logging.ERROR)

    def deny_pending_applications(self,
                                  deny_list: list | dict | str | int,
                                  reason: str = "Timeout, did not apply"):
        """Denies pending Members Chapter membership.

DESCRIPTION
    denies Chapter membership for members on deny_list

ARGUMENTS
            deny_list: list of dict-entrys, or ISOC-IDs, or single entry
                       or ISOC-ID
            reason: All denied applicants have to be denied for a reason
        """
        if type(deny_list) in (str, int):
            deny_list = [deny_list],
        for denyee in map(str, deny_list):
            if denyee in self._pending_applications_list:
                if not self._dryrun:
                    self._ams.deny(self._pending_applications_list[denyee],
                                   reason)
                log("Denied", denyee,
                              self._pending_applications_list[denyee]["name"])
                del self._pending_applications_list[denyee]
            else:
                log("ISOC-ID", denyee,
                    "is not in pending applications list",
                    level=logging.ERROR)

    def difference_from_expected(self, test=None) -> dict | str:
        """Compare intended outcome of operations with real outcome.

DESCRIPTION
    Compares the contents of the ISOC-AMS database with the expected result of
    operations

RETURNS
    A dict containing deviations of the inteded outcome:
            {
                "not deleted from members":
                    All entries in AMS-Chapter-Members that were supposed
                    to be deleted,
                "not approved from pending applicants list":
                    All entries in pending applications that were supposed
                    to be approved but were not added to the AMS-Chapter-Members
                "not removed from pending applicants list":
                    All entries in pending applications that should be
                    removed - either since approved or since denied
            }
    Or a string with the result of the comoarision.
        """
        if not self._dryrun:

            log(date=False)

            strong_msg("Check if actions ended up in AMS database")
            log("we have to read the AMS Database tables again to find deviations from expected result after actions :(")
            log("", date=False)

            not_deleted = {}
            not_approved = {}
            not_removed_from_pending = {}
            new_members_list = self._ams.build_members_list()
            dlog("Check members list")
            for nm in new_members_list:
                if nm not in self._members_list:
                    dlog(new_members_list[nm]["first name"],
                         new_members_list[nm]["last name"],
                         "("+nm+")",
                         "was not deleted")
                    not_deleted[nm] = new_members_list[nm]
            for nm in self._members_list:
                if nm not in new_members_list:
                    dlog(self._members_list[nm]["first name"],
                         self._members_list[nm]["last name"],
                         "("+nm+")",
                         "was not approved")
                    not_approved[nm] = self._members_list[nm]
            new_pending_applications_list = self._ams.build_pending_applicants_list()
            for np in new_pending_applications_list:
                if np not in self._pending_applications_list:
                    dlog(self._members_list[nm]["name"],
                         "("+nm+")",
                         "was not removed from pending aoolications")
                    not_removed_from_pending[np] = new_pending_applications_list[np]

            result = {}
            if not_deleted:
                result["not deleted from members"] = not_deleted
            if not_approved:
                result["not approved from pending applicants list"] = not_approved
            if not_removed_from_pending:
                result["not removed from pending applicants list"] = not_removed_from_pending
            if not result:
                result = "everything OK"
                dlog(result)
            return result
        else:
            dlog("DRYRUN: No results expected")
            return "Dryrun: No results expected"

class _ISOC_AMS(Driver):

    def __init__(self, logfile: str = sys.stdout):

        super().__init__(_options)
        self.windows = {}

    def __del__(self):
        self.quit()

    def activate_window(self, name: str, url: str | None = None, refresh: bool = False):
        if self.windows.get(name):
            dlog("switching to window", name)
            self.switch_to.window(self.windows[name])
            if refresh:
                self.navigate().refresh()
            if url:
                self.get(url)
            return True
        elif url:
            dlog("switching to NEW window", name)
            self.switch_to.new_window('tab')
            self.windows[name] = self.current_window_handle
            self.get(url)
            return True
        else:
            sys.exit('neither name nor url specified for "activate_window"'
                     'or window "' + name + '" not found')


    def waitfor(self, cond, val, timeout=20, message="", by=By.XPATH):
        try:
            if val:
                elem = WebDriverWait(self, timeout).until(
                    cond((by, val)))
            else:
                elem = WebDriverWait(self, timeout).until(cond)
            return elem
        except TimeoutException:
            strong_msg(message, level=logging.ERROR)
            raise

#
# setup session, init windows
#

    def login(self, credentials):
        # Sign on user and navigate to the Chapter leaders page,

        log(date=False)
        log("logging in")

        # go to community home page after succesfullogin
        self.get("https://community.internetsociety.org/s/home-community")
        # login
        elem = self.waitfor(EC.element_to_be_clickable,
                            "next",
                            by=By.ID,
                            message="timelimit exceeded while waiting "
                            "for login page to complete")
        # we use JS to fill the logi form, since sendkeys doesn'twork properly
        self.execute_script(
            "document.getElementById('signInName').value='%s';"
            "document.getElementById('password').value='%s';"
            "arguments[0].click();"
            % credentials,
            elem)

        # self.set_window_size(1600, 300)
        dlog("log in started")
        # community portal
        # self.waitfor(EC.presence_of_element_located,
        #              "siteforceStarterBody",
        #              by=By.CLASS_NAME,
        #              message=)

        try:
            elem = WebDriverWait(self, 10).until(
                EC.any_of(
                  EC.presence_of_element_located((By.CLASS_NAME, "siteforceStarterBody")),
                  EC.visibility_of_element_located((By.CSS_SELECTOR, "form div.error p"))))
        except TimeoutException:
            strong_msg("timelimit exceeded while waiting "
                       "for Community portal to open", level=logging.ERROR)
            raise
        if elem.tag_name == "p":
            strong_msg(elem.text, level=logging.ERROR)
            exit(1)

        dlog("now on community portal")

        # open chapter Leader Portal
        self.get("https://community.internetsociety.org/leader")
        dlog("waiting for Chapter Leader portal")

        # look if menue appears to be ready (and grab link to reports page)
        reports_ref = self.waitfor(EC.element_to_be_clickable,
                                   "//a[starts-with(@href,"
                                   "'/leader/s/report/')]",
                                   message="timelimit exceeded while waiting "
                                   "for Chapter Leader portal to open"
                                   )
        # since group applications from the report page don't provide an ISOC ID
        # we need it from the leader page menue
        group_application_ref = self.waitfor(
            EC.element_to_be_clickable,
            "//a[starts-with(@href,"
            "'/leader/s/isoc-group-application/')]",
            message="timelimit exceeded while waiting "
            "for Chapter Leader portal to open"
            )

        self.windows["leader"] = self.current_window_handle
        log("Now on Chapter Leader portal")
        log(date=False)

        # get lists (in an extra "reports" tab)
        self.reports_link = reports_ref.get_attribute('href')
        self.group_application_link = group_application_ref.get_attribute('href')
        self.reports_page_ready = (EC.element_to_be_clickable,
                                   "//table//lightning-button//button")
#
#   functions to aquire data
#

    def build_members_list(self) -> dict:

        # we have to scrape data from 2 pages called:
        #   Active Chapter Members
        #   Active Members with Contact Info
        # reason is Active Chapter Members doesn't give us the link to
        # act on the list (to delete members)

        log(date=False)
        log("start build members list")
        self.create_report_page("Members",
                                "Active Chapter Members")
        self.load_report("Members")
        members = self.get_table(self.get_members)

        self.create_report_page("Member Contacts",
                                "Active Members with Contact Info")
        self.load_report("Member Contacts")
        contacts = self.get_table(self.get_member_contacts)

        for k, v in members.items():
            v["action link"] = contacts.get(v["email"])
        log("members list finished / ", len(members), "collected")
        log(date=False)
        return members

    def build_pending_applicants_list(self) -> dict:
        """Collect the relevant dataabout members registered as chapters members.

        Returns:
            A 2 level dictionary
                ISOC-ID of pending applicants: dictionary with relevant fields
        """
        # we have to scrape data from the page provided via the menue
        # reason is the page referred to in the reports page doesn't give
        # us the ISOC-ID

        log(date=False)
        log("start build pending applications")
        dlog("Creating page for Pending Applications")
        msg = "timelimit exceeded while waiting " \
            "for report page for Pending Application report"
        cond = (EC.presence_of_element_located,
#                "table.slds-table td.cellcontainer a.forceOutputLookup")
                "table")
        self.activate_window("report",
                             url=self.group_application_link)
        dlog("Pending applications", "page created")
        pendings = self.get_table(self.get_pendings)
        log("Pending applications list finished / ", len(pendings), "collected")
        log(date=False)
        return pendings

    def create_report_page(self, subject, button_title):
        dlog("Creating page for", subject)
        msg = "timelimit exceeded while waiting " \
            "for report page for " + subject + " report"
        self.activate_window("report",
                             url=self.reports_link)
        elem = WebDriverWait(self, 30).until(EC.element_to_be_clickable((
            By.XPATH,
            "//table//lightning-button"
            "//button[@title='%s']" % button_title)
            ))
        time.sleep(1)
        self.execute_script('arguments[0].click();', elem)
        dlog(subject, "page created")

    def load_report(self, subject):
        dlog("Loading", subject)
        cond = EC.presence_of_element_located;
        val = "iframe"
        msg = "timelimit exceeded while waiting " \
              "waiting for list of " + subject
        iframe = self.waitfor(EC.presence_of_element_located, "iframe.isView",
                     message=msg, timeout=30, by=By.CSS_SELECTOR)

        # this is so strange: this page doesnt hold all columns (fields) if
        # they don't fit on the iframe. So we have to set a new (big) width
        # to receive the required data
        self.execute_script('arguments[0].style.width = "4000px";', iframe)

        WebDriverWait(self, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,
                                                       "iframe.isView")))
        self.waitfor(EC.presence_of_element_located, "//table//tbody//td",
                     message=msg)
        dlog("got list of", subject)

    def get_table(self, reader: callable):
        # this is a wrapper for reading tables
        # the reading itself is done by the reader argument
        def getint(s: str) -> int:
            # get integer from start of string
            i = 0
            for c in s:
                if c.isdigit():
                    i += 1
                else:
                    break
            return int(s[:i])
        if reader == self.get_members:
            dlog('collecting the following fields: "ISOC-ID", "first name", '
                '"last name", "email"')
        if reader == self.get_member_contacts:
            dlog('collecting the following fields: '
                '"action link" (for taking actions), '
                '"email" (to connect with members list)')
        if reader == self.get_pendings:
            dlog('collecting the following fields: "name", "email", '
                '"action link", "date"')

        if reader == self.get_pendings:
            tableselector = "table.uiVirtualDataTable tbody tr"
            total_elem = self.waitfor(
                EC.presence_of_element_located,
                "//force-list-view-manager-status-info/span/span",
                message="timeout waiting for Metrics",
                timeout=30)
        else:
            tableselector = "table.data-grid-full-table tbody tr"
            self.waitfor(EC.presence_of_element_located,
                         "span.metricsAnnouncement",
                         by=By.CSS_SELECTOR,
                         message="timeout waiting for Metrics",
                         timeout=30)
            total_selector = "div.metricsValue"
            total_elem = self.find_element(By.CSS_SELECTOR, total_selector)
        WebDriverWait(self, 10).until(_WaitForTextInElement(total_elem))
        total = getint(total_elem.text)
        dlog("Total (records expected):", total)
        dlog("Waiting for Total to stabilise")
        # wait a few seconds for total to become stable
        time.sleep(3)
        total = getint(total_elem.text)
        dlog("Total (records expected):", total)
        data = {}
        while total > len(data):
            time.sleep(3)
            rows = self.find_elements(
                By.CSS_SELECTOR, tableselector)
            dlog("calling reader with", len(rows), "table rows, ",
                  "(collected records so far:", len(data),")")
            scr_to = reader(rows, data)
            if getint(total_elem.text) != total:
                total = getint(total_elem.text)
                dlog("Total was updated, now:", total)
            if len(data) < total:
                self.execute_script('arguments[0].scrollIntoView(true);', scr_to)
            else:
                dlog("records collected / total", len(data), " /", total)
                return data

    def get_members(self, rows, members):
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            if cells and cells[0].text and cells[0].text not in members.keys():
                member = {}
                member["first name"] = cells[1].text
                member["last name"] = cells[2].text
                member["email"] = cells[7].text
                members[cells[0].text] = member
            orow = row
        return orow

    def get_member_contacts(self, rows, members):
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            if cells and \
                    len(cells) > 11 and \
                    cells[11].text and \
                    cells[11].text not in members.keys():
                lnk = cells[1].find_element(By.CSS_SELECTOR, "a[href]"). \
                    get_attribute('href')
                members[cells[11].text] = lnk
            orow = row
        return orow

    def get_pendings(self, rows, pendings):
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, ".slds-cell-edit")
            if cells and cells[3].text:
                pending = {}
                pending["name"] = cells[4].text
                pending["email"] = cells[5].text
                # pending["contact link"] = cells[4]. \
                #     find_element(By.CSS_SELECTOR, "a[href]"). \
                #         get_attribute('href')
                pending["action link"] = cells[3]. \
                    find_element(By.CSS_SELECTOR, "a[href]"). \
                        get_attribute('href')
                pending["date"] = datetime.strptime(
                    cells[10].text, "%m/%d/%Y")
                pendings[cells[6].text] = pending
            orow = row
        return orow

#
#  operations on data
#

    def deny(self, entry, reason):
        time_to_wait = 100
        log(date=False)
        log("start denial for", entry["name"])
        # operation will take place in an own tab
        self.activate_window("action",
                             url=entry["action link"])

        elem = self.waitfor(EC.element_to_be_clickable,
                            '//button'
                            '[contains(text(),'
                            '"Deny Applicant")]',
                            message="timelimit exceeded while waiting "
                            "waiting for details page for " +
                            entry["name"] + " to complete")

        time.sleep(1)  # for what ist worth?
        self.execute_script('arguments[0].click();', elem)

        d_close = WebDriverWait(self, 10, 0.3). \
                until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, 'button.slds-modal__close')))

        dlog("select a reason for denial to feed AMS's couriosity")
        elem = self.waitfor(EC.element_to_be_clickable,
                            "//div"
                            "[contains(concat(' ',normalize-space(@class),' '),"
                            "'slds-dropdown-trigger')]",
                            message="timelimit exceeded while waiting "
                            "for deny reason box")
        time.sleep(1)  # for what ist worth?
        self.execute_script('arguments[0].click();', elem)
###
        dlog("Waiting for combobox, chose 'other'")

        elem = self.waitfor(EC.element_to_be_clickable,
                            "//lightning-base-combobox-item"
                            "[@data-value='Other']",
                            message="timelimit exceeded while waiting "
                            "for deny reason 'Other'")
        time.sleep(1)  # for what ist worth?
        self.execute_script('arguments[0].click();', elem)

        elem = self.waitfor(EC.presence_of_element_located,
                            "//flowruntime-record-field"
                            "//lightning-primitive-input-simple"
                            "//input",
                            message="timelimit exceeded while waiting "
                            "for deny reason 'Other - Details'")
        log(f"we'll give '{reason}' as reason")
        time.sleep(1)
        # elem.send_keys(reason)
        self.execute_script(f'arguments[0].value="{reason}";', elem)
        dlog("finally click next")

        elem = self.waitfor(EC.element_to_be_clickable,
                            "//flowruntime-navigation-bar"
                            "/footer"
                            "//lightning-button/button",
                            message="timelimit exceeded while waiting "
                            "for 'Next' button to complete")
        time.sleep(2)  # for what ist worth?
        self.execute_script('arguments[0].click();', elem)
        try:
            WebDriverWait(self, 15).until(EC.staleness_of(d_close))
        except TimeoutException:
            strong_msg("Timeout: Maybe operation was not performed")
            log(date=False)
            return False
        log("done")
        return True

    def approve(self, entry):
        log(date=False)
        log("start approval for", entry["name"])

        self.activate_window("action",
                             url=entry["action link"])

        elem = self.waitfor(EC.presence_of_element_located,
                            '//button'
                            '[contains(text(),'
                            '"Approve Applicant")]',
                            message="timelimit exceeded while waiting "
                            "waiting for details page for " +
                            entry["name"] + " to complete")

        dlog("starting with approval")
        time.sleep(1)  # for what ist worth?
        self.execute_script('arguments[0].click();', elem)

        d_close = WebDriverWait(self, 10, 0.3). \
                until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, 'button.slds-modal__close')))

        dlog("finally click next")
        elem = self.waitfor(EC.element_to_be_clickable,
                            "//flowruntime-navigation-bar"
                            "/footer"
                            "//lightning-button/button",
                            message="timelimit exceeded while waiting "
                            "for 'Next' button to complete")
        time.sleep(1)  # for what ist worth?
        self.execute_script('arguments[0].click();', elem)

        try:
            WebDriverWait(self, 15).until(EC.staleness_of(d_close))
        except TimeoutException:
            strong_msg("Timeout: Maybe operation was not performed",
                       level=logging.ERROR)
            log(date=False)
            return False
        log("done")
        return True


    def delete(self, entry):
        log(date=False)
        name = entry["first name"] + " " + entry["last name"]
        log("start delete", name, "from AMS Chapter members list" )

        self.activate_window("action",
                             url=entry["action link"])

        elem = self.waitfor(EC.element_to_be_clickable,
                            "//runtime_platform_actions-action-renderer"
                            "[@title='Terminate']"
                            "//button",
                            message="timelimit exceeded while waiting "
                            "waiting for details page for " +
                            name + " to complete")

        time.sleep(1)  # for what ist worth?
        self.execute_script('arguments[0].click();', elem)

        d_close = WebDriverWait(self, 10, 0.3). \
                until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, 'button.slds-modal__close')))

        try:
            WebDriverWait(self, 15).until(EC.staleness_of(d_close))
        except TimeoutException:
            strong_msg("Timeout: Maybe operation was not performed",
                       level=logging.ERROR)
            log(date=False)
            return False
        log("done")
        return True


if __name__ == "__main__":
    from getpass import getpass
    headless = True
    if "-h" in sys.argv:
        headless = False
    inp = False
    if "-i" in sys.argv:
        inp = True
    dryrun = False
    if "-d" in sys.argv:
        dryrun = True
    debug = False
    if "--debug" in sys.argv:
        debug = True

    print("Username", end=":")
    user_id = input()
    password = getpass()
    if debug:
        ams = ISOC_AMS(
            user_id,
            password,
            headless=headless,
            dryrun=dryrun,
            logfile=sys.stdout,
            debuglog=NoneHh,
            )
    else:
        ams = ISOC_AMS(
            user_id,
            password,
            headless=headless,
            dryrun=dryrun,
            logfile=sys.stdout,
            )
    members = ams.members_list
    pendings = ams.pending_applications_list

    strong_msg("MEMBERS")
    i = 0
    for k, v in members.items():
        i += 1
        log(i, k,  v["first name"], v["last name"], v["email"], date=False)

    strong_msg("PENDING APPLICATIONS")
    i = 0
    for k, v in pendings.items():
        i += 1
        # print(i, k, v)
        log(i, k, v["name"], v["email"], v["date"].isoformat()[:10], date=False)

    if inp:
        log('READING COMMANDS:')
        import re
        patt = re.compile(r'(approve|deny|delete):?\s*([\d, ]+)')
        func = {"approve": ams.approve_pending_applications,
                "deny": ams.deny_pending_applications,
                "delete": ams.delete_members,
                }
        splitter = re.compile(r'[\s,]+')
        for rec in sys.stdin:
            rec = rec.strip()
            if m := patt.match(rec):
                command = m.group(1)
                keys = splitter.split(m.group(2))
                func[command](keys)
            else:
                log(rec, "contains an error", level=logging.ERROR)
        log("EOF of command input")

        result = ams.difference_from_expected()
        if type(result) is not str:
            for data in result.items():
                log(data[0])
                for k, v in data[1].items():
                    if "members" in data[0]:
                        log("        ", v["first name"], v["last name"], v["email"], "("+k+")", date=False)
                    else:
                        log("        ", v["name"], v["email"], "("+k+")", date=False)
