"""

This script is a wrapper to allow imglib2-imglyb code that uses Java's AWT
to run properly on OS X.  It starts the Cocoa event loop before Java and
keeps Cocoa happy  See https://github.com/kivy/pyjnius/issues/151 for more.

In particular, this wrapper allows one to run the code from imglyb-examples.

Tested in Python 3 only!  Not sure if you'd need to change anything for Python 2
beyond the print statements.

usage: python OSXAWTwrapper.py [module name | script path] [module or script parameters]

"""

import os
import sys


import objc
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper

usage = "usage: python OSXAWTwrapper.py [module name | script path] [module or script parameters]"

def runAwtStuff():

    import runpy

    # user can provide either a module or a path to a script;
    #   either way, need to remove it from sys.argv,
    #   because the wrapped module or script might parse sys.argv for its own reasons:
    if len(sys.argv) > 1:
        name = sys.argv[1]
        sys.argv.remove(name)

        # whether module or script, need to set the run_name for things to work as expected!
        try:
            if os.path.exists(name):
                runpy.run_path(name, run_name="__main__")
            else:            
                runpy.run_module(name, run_name="__main__")
        except Exception as e:
            print("exception occurred while running {}: {}".format(name, e))

            ## lots can go wrong here, and exceptions can bubble up from
            #   the Java layer, too; uncomment lines below to print
            #   more information on exception
            # note: different exceptions have different attributes, so you
            #   might need to adjust the lines below; use dir(e) to see
            #   what you have available when you are debugging
            # print("exception details: ")
            # print("e.args: ", e.args)
            # print("e.__class__: ", e.__class__)
            # print("e.stacktrace: ")
            # for line in e.stacktrace:
            #     print("\t", line)
            ## if Java throws a reflection error, you might want this:
            ## print("e.innermessage", e.innermessage)
    else:
        print(usage)
        print("no module or script specified")


class AppDelegate (NSObject):
    def init(self):
        self = objc.super(AppDelegate, self).init()
        if self is None:
            return None
        return self

    def runjava_(self, arg):
        runAwtStuff()
        # we need to terminate explicitly, or it'll hang when
        #   the wrapped code exits
        NSApp().terminate_(self)

    def applicationDidFinishLaunching_(self, aNotification):
        self.performSelectorInBackground_withObject_("runjava:", 0)


def main():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
    # this is necessary to have keyboard events sent to the UI;
    #   basically this call makes the script act like an OS X application,
    #   with Dock icon and everything
    NSApp.setActivationPolicy_(NSApplicationActivationPolicyRegular)
    AppHelper.runEventLoop()

if __name__ == '__main__' : 
    main()

