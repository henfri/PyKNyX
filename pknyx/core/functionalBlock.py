# -*- coding: utf-8 -*-

""" Python KNX framework

License
=======

 - B{pKNyX} (U{http://www.pknyx.org}) is Copyright:
  - (C) 2013 Frédéric Mantegazza

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

Application management

Implements
==========

 - B{FunctionalBlock}
 - B{FunctionalBlockValueError}

Documentation
=============

B{FunctionalBlock} is one of the most important object of B{pKNyX} framework, after L{Datapoint<pknyx.core.datapoint>}.

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id: device.py 130 2013-07-02 08:58:54Z fma $"

from pknyx.common.exception import PKNyXValueError
from pknyx.common.helpers import reprStr
from pknyx.services.loggingServices import Logger
from pknyx.core.datapoint import Datapoint
from pknyx.core.groupObject import GroupObject
from pknyx.stack.individualAddress import IndividualAddress


class FunctionalBlockValueError(PKNyXValueError):
    """
    """


class FunctionalBlock(object):
    """ FunctionalBlock class

    The Datapoints of a FunctionalBlock must be defined in sub-classes, as class dict, and named B{DP_xxx}. They will be
    automatically instanciated as real L{Datapoint} objects, and added to the B{_datapoints} dict.

    #Same for GroupObject.

    @ivar _name: name of the device
    @type _name:str

    @ivar _desc: description of the device
    @type _desc:str

    @ivar _datapoints: Datapoints exposed by this FunctionalBlock
    @type _datapoints: dict of L{Datapoint}

    @ivar _groupObjects: GroupObjects exposed by this FunctionalBlock
    @type _groupObjects: dict of L{GroupObject}
    """
    def __new__(cls, *args, **kwargs):
        """ Init the class with all available types for this DPT
        """
        self = object.__new__(cls, *args, **kwargs)

        # class objects named B{DP_xxx} are treated as Datapoint and added to the B{_datapoints} dict
        self._datapoints = {}
        for key, value in cls.__dict__.iteritems():
            if key.startswith("DP_"):
                name = value['name']
                if self._datapoints.has_key(name):
                    raise FunctionalBlockValueError("duplicated Datapoint (%s)" % name)
                self._datapoints[name] = Datapoint(self, **value)

        # class objects named B{GO_xxx} are treated as GroupObjects and added to the B{_groupObjects} dict
        self._groupObjects = {}
        for key, value in cls.__dict__.iteritems():
            if key.startswith("GO_"):
                try:
                    datapoint = self._datapoints[value['dp']]
                except KeyError:
                    raise FunctionalBlockValueError("unknown datapoint (%s)" % value['dp'])
                name = datapoint.name
                if self._groupObjects.has_key(name):
                    raise FunctionalBlockValueError("duplicated GroupObject (%s)" % name)

                # Remove 'dp' key from GO_xxx dict
                # Use a copy to let original untouched
                value_ = {}
                value_.update(value)
                value_.pop('dp')
                self._groupObjects[name] = GroupObject(datapoint, **value_)

        try:
            self._desc = cls.__dict__["DESC"]
        except KeyError:
            Logger().exception("FunctionalBlock.__new__()", debug=True)
            self._desc = None

        return self

    def __init__(self, name, desc=None, individualAddress=None):
        """

        @param name: name of the device
        @type name: str

        @param desc: description of the device
        @type desc: str

        @param individualAddress: individual address used as source address when transmitting on the bus
        @type individualAddress: L{IndividualAddress}

        raise FunctionalBlockValueError:
        """
        super(FunctionalBlock, self).__init__()

        self._name = name
        if desc is not None:
            self._desc = "%s - %s" % (desc, self._desc)
        self._individualAddress = individualAddress

    def __repr__(self):
        return "<%s(name='%s', desc='%s')>" % (reprStr(self.__class__), self._name, self._desc)

    def __str__(self):
        return "<%s('%s')>" % (reprStr(self.__class__), self._name)

    @property
    def name(self):
        return self._name

    @property
    def desc(self):
        return self._desc

    @property
    def individualAddress(self):
        return self._individualAddress

    @property
    def dp(self):
        return self._datapoints

    @property
    def go(self):
        return self._groupObjects

    def notify(self, dpName, oldValue, newValue):
        """ Notify the functional block of a datapoint value change

        The functional block must trigger all methods bound to this notification with xxx.notify.datapoint()

        @param dpName: name of the datapoint which sent this notification
        @type dpName: str

        @param oldValue: old value of the datapoint
        @type oldValue: depends on the datapoint DPT

        @param newValue: new value of the datapoint
        @type newValue: depends on the datapoint DPT

        @todo: use an Event as param
        """
        Logger().debug("FuntionalBlock.notify(): datapoint=%s, oldValue=%s, newValue=%s" % (dpName, oldValue, newValue))


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class FunctionalBlockTestCase(unittest.TestCase):

        class TestFunctionalBlock(FunctionalBlock):
            DP_01 = dict(name="temperature", access="output", dptId="9.001", defaultValue=19.)
            DP_02 = dict(name="humidity", access="output", dptId="9.007", defaultValue=50.)
            DP_03 = dict(name="wind_speed", access="output", dptId="9.005", defaultValue=0.)
            DP_04 = dict(name="wind_alarm",  access="output", dptId="1.005", defaultValue="No alarm")
            DP_05 = dict(name="wind_speed_limit",  access="input", dptId="9.005", defaultValue=15.)
            DP_06 = dict(name="wind_alarm_enable", access="input", dptId="1.003", defaultValue="Disable")

            DESC = "Dummy description"

        def setUp(self):
            self.fb1 = FunctionalBlockTestCase.TestFunctionalBlock(name="test1")
            self.fb2 = FunctionalBlockTestCase.TestFunctionalBlock(name="test2", desc="pipo")

        def tearDown(self):
            pass

        def test_display(self):
            print repr(self.fb1)
            print self.fb2

        def test_constructor(self):
            pass


    unittest.main()