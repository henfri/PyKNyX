# -*- coding: utf-8 -*-

""" Python KNX framework.

License
=======

 - B{pKNyX} (U{http://www.pknyx.org}) is Copyright:
  - (C) 2013-2015 Frédéric Mantegazza

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see:

 - U{http://www.gnu.org/licenses/gpl.html}

Module purpose
==============

Logging service

Implements
==========

- B{LoggerValueError}
- B{LoggerObject}

@author: Frédéric Mantegazza
@copyright: (C) 2013-2015 Frédéric Mantegazza
@license: GPL
"""

import logging
import logging.handlers

getLogger = logging.getLogger

try:
    from io import StringIO
except ImportError:
    import StringIO
import traceback
import os.path
import time

from pknyx.common import config
from pknyx.common.exception import PKNyXValueError
from pknyx.common.singleton import Singleton
from pknyx.services.loggerFormatter import DefaultFormatter, ColorFormatter, \
                                           SpaceFormatter, SpaceColorFormatter
logging.raiseExceptions = 0
logging.TRACE = logging.DEBUG
logging.EXCEPTION = logging.ERROR + 5
logging.addLevelName(logging.TRACE, "TRACE")
logging.addLevelName(logging.EXCEPTION, "EXCEPTION")

def _setup():
    # Logger
    _logger = logging.getLogger('pknyx')
    _logger.propagate = False

    # Handlers
    _stdoutStreamHandler = logging.StreamHandler()
    streamFormatter = SpaceColorFormatter(config.LOGGER_STREAM_FORMAT)
    _stdoutStreamHandler.setFormatter(streamFormatter)
    _logger.addHandler(_stdoutStreamHandler)

    if config.LOGGER_BACKUP_COUNT:
        loggerFilename = os.path.join(config.LOGGER_DIR, "%s_%s.log" % (config.APP_NAME, deviceName))
        fileHandler = logging.handlers.RotatingFileHandler(loggerFilename, 'w',
                                                            config.LOGGER_MAX_BYTES,
                                                            config.LOGGER_BACKUP_COUNT)
        fileFormatter = SpaceFormatter(config.LOGGER_FILE_FORMAT)
        fileHandler.setFormatter(fileFormatter)
        _logger.addHandler(fileHandler)

    _logger.setLevel(logging._NameToLevel(config.LOGGER_LEVEL))

    def _trace(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'TRACE'.
        """
        if self.isEnabledFor(logging.TRACE):
            self._log(logging.TRACE, msg, args, **kwargs)
    logging.Logger.trace = _trace

    def _exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Log 'msg % args' with severity 'TRACE'.
        """
        if self.isEnabledFor(logging.TRACE):
            self._log(logging.EXCEPTION, msg, args, exc_info=exc_info, **kwargs)
    logging.Logger.exception = _exception

