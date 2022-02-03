"""
This script is a wrapper to allow Java code that uses AWT to run properly on
macOS. It starts the Cocoa event loop before Java and keeps Cocoa happy.

See https://github.com/kivy/pyjnius/issues/151 for more.

In particular, this wrapper allows one to run the code from imglyb-examples.

usage: python OSXAWTwrapper.py [module name | script path] [module or script parameters]

NB: Since the creation of this script, the imglyb project switched from pyjnius
to jpype, and this script is not really necessary anymore. You can instead use
jpype.setupGuiEnvironment(...), passing a function that does Java AWT things,
and it will be executed on the correct thread.
"""

import os
import sys


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


def main():
    try:
        import objc
        from PyObjCTools import AppHelper
        from AppKit import NSApplication, NSApp, NSObject, NSApplicationActivationPolicyRegular
        # from Foundation import *

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

        app = NSApplication.sharedApplication()
        delegate = AppDelegate.alloc().init()
        NSApp().setDelegate_(delegate)
        # this is necessary to have keyboard events sent to the UI;
        #   basically this call makes the script act like an OS X application,
        #   with Dock icon and everything
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        AppHelper.runEventLoop()
    except ModuleNotFoundError:
        print("Skipping OSXAWTwrapper - module 'objc' is not installed") 

if __name__ == '__main__' : 
    main()

