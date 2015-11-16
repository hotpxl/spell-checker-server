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

    def __init__(self, exe_path, max_edit_dist=5):
        # Configure spellchecker.
        self._exe_path = exe_path
        # Only return suggestions within edit distance range.
        self._max_edit_dist = max_edit_dist
        # Url to request from.
        self._url = 'http://www.google.com'
        # Start driver.
        self.__start_driver()

    def __del__(self):
        self.__terminate_driver()

    def __terminate_driver(self):
        logger.info('Terminating PhantomJS driver...')
        self._driver.quit()

    def __start_driver(self):
        logger.info('Launching PhantomJS driver...')
        self._driver = webdriver.PhantomJS(
            executable_path=self._exe_path, service_log_path=os.path.devnull)

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
        try:
            wait = ui.WebDriverWait(self._driver, self._timeout)
            self._driver.get(self._url)
            wait.until(lambda driver: driver.find_elements_by_xpath(
                '/html/body/center/form/table/tbody/'
                'tr/td[2]/span[1]/span/input'))
            logger.debug('Request done. Back on page: {}'.format(
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
        except Exception as t:
            logger.error(t)
            self.__reset_driver()
            return None
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
