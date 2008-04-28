import unittest
import sys
import augeas

import os

mydir = os.path.dirname(sys.argv[0])
if not os.path.isdir(mydir):
    mydir = os.getcwd()

myroot = mydir + "/testroot"

def recurmatch(aug, path):
    if path:
        if path != "/":
            val = aug.get(path)
            if val:
                yield (path, val)

        m = []
        if path != "/":
            aug.match(path)
        for i in m:
            for x in recurmatch(aug, i):                
                yield x
        else:
            for i in aug.match(path + "/*"):
                for x in recurmatch(aug, i):
                    yield x

class TestAugeas(unittest.TestCase):
    def test01Get(self):
        "test aug_get"
        a = augeas.augeas(root=myroot)
        self.failUnless(a.get("/wrong/path") == None)

    def test02Match(self):
        "test aug_match"
        a = augeas.augeas(root=myroot)
        matches = a.match("/files/etc/hosts/*")
        self.failUnless(matches)
        for i in matches:
	    for attr in a.match(i+"/*"):
                self.failUnless(a.get(attr) != None)

    def test03PrintAll(self):
        "print all tree elements"
        a = augeas.augeas(root=myroot)
        path = "/"
        matches = recurmatch(a, path)
        for (p, attr) in matches:
            print >> sys.stderr, p, attr
            self.failUnless(p != None and attr != None)

    def test04Grub(self):
        "test default setting of grub entry"
        a = augeas.augeas(root=myroot)
        num = 0
        for entry in a.match("/files/etc/grub.conf/title"):
            num += 1
        self.failUnless(num == 2)
        default = int(a.get("/files/etc/grub.conf/default"))
        self.failUnless(default == 0)
        a.set("/files/etc/grub.conf/default", str(1))
        a.save()
        default = int(a.get("/files/etc/grub.conf/default"))
        self.failUnless(default == 1)
        a.set("/files/etc/grub.conf/default", str(0))
        a.save()
        

def suite():
    suite = unittest.TestSuite()
    suite = unittest.makeSuite(TestAugeas, 'test')
    return suite

if __name__ == "__main__":
    testRunner = unittest.TextTestRunner(verbosity=2)
    result = testRunner.run(suite())
    sys.exit(not result.wasSuccessful())

__author__ = "Harald Hoyer <harald@redhat.com>"
