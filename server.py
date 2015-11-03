from __future__ import absolute_import
from __future__ import print_function
import os.path

import spell_checker


if __name__ == '__main__':

    a = spell_checker.GoogleSpellChecker(os.path.abspath('./phantomjs'))
