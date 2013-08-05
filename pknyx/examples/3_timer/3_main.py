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

Example 3 - timer

Implements
==========

 - B{TimerFB}
 - B{main}

Documentation
=============

This example implements a timer which switches off something when switch on has been detected, after a delay.

3 datapoints are create:
 - 'cmd' is the command (output)
 - 'state' is the sate (input)
 - 'delay' is the timer delay value (input)

This functional block monitors the 'state' datapoint; when this datapoint changes from 'Off' to 'On', the functional
block starts the timer.
When the timer delay expires, the functional blocks sends 'Off' on its 'cmd' datapoint.
If the 'state' datapoint changes back to 'Off' before the timer expires, the timer is desactivated.
If the 'delay' datapoint changes while the timer is active, the timer is restarted with the new value.

Just weave these datapoints to group address and give it a try.

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

from pknyx.api import Logger
from pknyx.api import FunctionalBlock, Stack, ETS
from pknyx.api import Scheduler, Notifier

stack = Stack(individualAddress="1.2.3")
ets = ETS(stack)

schedule = Scheduler()
notify = Notifier()

logger = Logger()


class TimerFB(FunctionalBlock):
    """ Timer functional block
    """

    # Datapoints definition
    DP_01 = dict(name="cmd", access="output", dptId="1.001", default="Off")
    DP_02 = dict(name="state", access="input", dptId="1.001", default="Off")
    DP_03 = dict(name="delay", access="input", dptId="7.005", default=10)

    GO_01 = dict(dp="cmd", flags="CWT", priority="low")
    GO_02 = dict(dp="state", flags="CWUI", priority="low")
    GO_03 = dict(dp="delay", flags="CWU", priority="low")

    DESC = "Timer"

    def _init(self):
        """ Additionnal init of the timer
        """
        self._timer = 0

    @schedule.every(seconds=1)
    def updateTimer(self):
        """ Method called every second.
        """
        #logger.trace("TimerFB.updateTimer()")

        if self._timer:
            self._timer -= 1
            if not self._timer:
                logger.info("%s: timer expired; switch off" % self._name)
                self.dp["cmd"].value = "Off"

    @notify.datapoint(dp="state", condition="change")
    def stateChanged(self, event):
        """ Method called when the 'state' datapoint changes
        """
        logger.debug("TimerFB.stateChanged(): event=%s" % repr(event))

        if event['newValue'] == "On":
            delay = self.dp["delay"].value
            Logger().info("%s: start timer for %ds" % (self._name, delay))
            self._timer = delay
        elif event['newValue'] == "Off":
            if self._timer:
                Logger().info("%s: switched off detected; cancel timer" % self._name)
                self._timer = 0

    @notify.datapoint(dp="delay", condition="change")
    def delayChanged(self, event):
        """ Method called when the 'delay' datapoint changes
        """
        logger.debug("TimerFB.delayChanged(): event=%s" % repr(event))

        # If the timer is running, we reset it to the new delay
        if self._timer:
            delay = self.dp["delay"].value
            Logger().info("%s: delay changed; restart timer" % self._name)
            self._timer = delay


def main():

    # Register functional blocks
    ets.register(TimerFB, name="timer", desc="")

    # Weave datapoints
    ets.weave(fb="timer", dp="cmd", gad="6/0/1")
    ets.weave(fb="timer", dp="state", gad="6/1/1")
    ets.weave(fb="timer", dp="delay", gad="6/2/1")

    print
    ets.printGroat("gad")
    print
    ets.printGroat("go")
    print
    schedule.printJobs()
    print

    # Run the stack main loop (blocking call)
    stack.mainLoop()


if __name__ == "__main__":
    try:
        main()
    except:
        logger.exception("3_main")
