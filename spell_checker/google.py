#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Oliver Groth, Yutian Li

"""Google spell checker."""

from __future__ import absolute_import
from __future__ import print_function
import time
import random
import traceback
import os

from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.common import exceptions
import nltk

from .utils import log

logger = log.get_logger(__name__)


class GoogleSpellChecker(object):

    def __init__(self, exe_path, max_edit_dist=5, delay=2, timeout=10,
                 max_retries=3, sleep_before_retry=60):
        # Configure spellchecker.
        self._exe_path = exe_path
        # Only return suggestions within edit distance range.
        self._max_edit_dist = max_edit_dist
        # Minimum delay between two spellcheck requests in seconds.
        self._delay = delay
        # Url to request from.
        self._url = 'http://www.google.com'
        # Maximum wait time before timeout for retrieving result page.
        self._timeout = timeout
        # Field to keep track of last request as `time.time()`.
        self._last_request = 0
        # Maximum number of retries when encountering timeout errors.
        self._max_retries = max_retries
        # Sleep time between two retries.
        self._sleep_before_retry = sleep_before_retry

        logger.info('Launching PhantomJS driver...')
        logger.info(self._exe_path)
        self._driver = webdriver.PhantomJS(
            executable_path=self._exe_path, service_log_path=os.path.devnull)

    def __del__(self):
        self.__terminate_driver()

    def __can_request(self):
        ts = time.time()
        lr = self._last_request
        idle = ts - lr
        if self._delay < idle:
            logger.debug('Free to request.')
            return True
        else:
            logger.debug('Waiting for request permission.')
            time.sleep((self._delay - idle) + random.randint(0, 2))
            logger.debug('Free to request.')
            return True

    def __request_done(self):
        self._last_request = time.time()

    def __terminate_driver(self):
        logger.info('Terminating PhantomJS driver...')
        self._driver.quit()

    def __start_driver(self):
        logger.info('Launching PhantomJS driver...')
        self._driver = webdriver.PhantomJS(executable_path=self._exe_path)

    def __reset_driver(self):
        """Reset driver.

        PhantomJS driver tends to produce memory leaks or gets stuck for some
        reason. This method resets the driver.
        """
        if self._driver:
            try:
                self.__terminate_driver()
            except:
                logger.warn('Driver already terminated.')
            self.__start_driver()
        else:
            self.__start_driver()

    def correct_spelling(self, query):
        """Correct spelling.

        Corrects all spelling errors in `query` with Google's algorithm.

        Args:
            query: Query to correct.
        """
        if self.__can_request():
            # Set timestamp for last request in spell checker.
            self.__request_done()

            retries = 0
            while True:
                try:
                    wait = ui.WebDriverWait(self._driver, self._timeout)
                    self._driver.get(self._url)
                    wait.until(lambda driver: driver.find_elements_by_xpath(
                        '/html/body/center/form/table/tbody/'
                        'tr/td[2]/span[1]/span/input'))
                    logger.debug(
                        'Request done. Back on page: {}'.format(
                            self._driver.current_url))

                    # Set waiting handler for AJAX request.
                    wait = ui.WebDriverWait(self._driver, self._timeout)
                    input_element = self._driver.find_element_by_name('q')
                    # Input query into search box.
                    input_element.send_keys(query)
                    input_element.submit()
                    logger.info('Submitting query: {}'.format(query))
                    wait.until(lambda driver: driver.find_elements_by_xpath(
                        '//*[@id=\'resultStats\']'))
                    logger.debug(
                        'Response loaded. Now on page: {}'.format(
                            self._driver.current_url))
                    break
                except exceptions.TimeoutException as ste:
                    retries += 1
                    if self._max_retries <= retries:
                        logger.error(
                            'Exceeded maximum number of {} retries.'.format(
                                self._max_retries))
                        logger.error(ste)
                        logger.error(traceback.print_exc())
                        self.__terminate_driver()
                        raise ste
                    else:
                        logger.warn(
                            'Encountered timeout. Retry {} time(s).'.format(retries))
                        naptime = self._sleep_before_retry + \
                            random.randint(0, 600)
                        logger.warn('Sleeping for {} seconds.'.format(naptime))
                        time.sleep(naptime)
                        self.__reset_driver()
                except Exception as t:
                    logger.error(t)
                    self.__reset_driver()
            # Get suggestion field.
            field = self._driver.find_elements_by_xpath(
                '//*[@id=\'_FQd\']/div/a')

            if 0 < len(field):
                suggested_text = str(field[0].text)
                logger.debug(
                    'Did you mean encountered. Suggested query: {}'.format(
                        suggested_text))
            else:
                suggested_text = query
                logger.debug('No suggestion.')

            # Google messed things up
            if self._max_edit_dist < nltk.edit_distance(suggested_text, query):
                logger.warn('Suggested text beyond edit distance threshold'
                            'of {}. Returning original query.'.format(
                                self._max_edit_dist))
                suggested_text = query
            logger.info('Checker returns: {}'.format(suggested_text))
            return suggested_text
        else:
            logger.warn(
                'Unable to request right now! '
                'Returning original query: {}'.format(query))
            return query
