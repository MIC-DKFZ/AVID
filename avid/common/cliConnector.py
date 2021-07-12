# AVID
# Automated workflow system for cohort analysis in radiology and radiation therapy
#
# Copyright (c) German Cancer Research Center,
# Software development for Integrated Diagnostic and Therapy (SIDT).
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE.txt or http://www.dkfz.de/en/sidt/index.html for details.

import logging
import math
import os
import stat
import subprocess
import time

from avid.common import osChecker
import avid.common.settings as AVIDSettings

logger = logging.getLogger(__name__)


class DefaultCLIConnector(object):
    """Default implementation of a CLI connector. It is used to abstract between the action logic and the system
     specific peculiarities for cli the execution (e.g. direct cli call or a call via a container)."""

    def __init__(self):
        pass

    def get_artefact_url_extraction_delegate(self, action_extraction_delegate=None):
        """Returns the URL extraction delegate that should be used when working with the connector.
        :param action_extraction_delegate: If the actions specifies its own delegate it can be passed
        and will be wrapped accordingly."""
        return action_extraction_delegate

    def generate_cli_file(self, file_path_base, content):
        global logger

        """Function generates the CLI file based on the passed file name base (w/o extension, extension will be added)
         and the content. It returns the full path to the CLI file."""

        if osChecker.isWindows():
            file_name = file_path_base + os.extsep + 'bat'
        else:
            file_name = file_path_base + os.extsep + 'sh'

        path = os.path.split(file_name)[0]

        try:
            osChecker.checkAndCreateDir(path)
            with open(file_name, "w") as outputFile:
                outputFile.write(content)
                outputFile.close()

            if not osChecker.isWindows():
                st = os.stat(file_name)
                os.chmod(file_name, st.st_mode | stat.S_IXUSR)

        except:
            logger.error("Error when writing cli script. Location: %s.", file_name)
            raise

        return file_name

    def execute(self, cli_file_path, log_file_path=None, error_log_file_path=None, cwd=None):
        global logger

        logfile = None

        if log_file_path is not None:
            try:
                logfile = open(log_file_path, "w")
            except:
                logfile = None
                logger.debug('Unable to generate log file for call: %s', cli_file_path)

        errlogfile = None

        if error_log_file_path is not None:
            try:
                errlogfile = open(error_log_file_path, "w")
            except:
                errlogfile = None
                logger.debug('Unable to generate error log file for call: %s', cli_file_path)

        try:
            returnValue = 0

            if os.path.isfile(cli_file_path):
                # Fix for T20136. Unsatisfying solution, but found no better way on
                # windows. If you make the subprocess calls to batch files (thats the
                # reason for the isfile() check) directly you get random "Error 32"
                # file errors (File already opened by another process) caused
                # by opening the bat files, which are normally produced by the actions.
                # "os.rename" approach was the simpliest way to check os independent
                # if the process can access the bat file or if there is still a racing
                # condition.
                pause_duration = AVIDSettings.getSetting(AVIDSettings.SUBPROCESS_PAUSE)
                max_pause_count = math.ceil(AVIDSettings.getSetting(AVIDSettings.ACTION_TIMEOUT) / pause_duration)
                pause_count = 0
                time.sleep(0.1)
                while True:
                    try:
                        os.rename(cli_file_path, cli_file_path)
                        break
                    except OSError:
                        if pause_count < max_pause_count:
                            time.sleep(pause_duration)
                            pause_count = pause_count + 1
                            logger.debug('"%s" is not accessible. Wait and try again.', cli_file_path)
                        else:
                            break

            useShell = not osChecker.isWindows()
            if cwd is None:
                subprocess.call(cli_file_path, stdout=logfile, stderr=errlogfile, shell=useShell)
            else:
                subprocess.call(cli_file_path, cwd=cwd, stdout=logfile, stderr=errlogfile, shell=useShell)

            if returnValue == 0:
                logger.debug('Call "%s" finished and returned %s', cli_file_path, returnValue)
            else:
                logger.error('Call "%s" finished and returned %s', cli_file_path, returnValue)

        finally:
            if logfile is not None:
                logfile.close()
            if errlogfile is not None:
                errlogfile.close()
