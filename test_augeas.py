import unittest
import sys
import augeas


class TestAugeas(unittest.TestCase):
    def testGet(self):
        "test aug_get"
        a = augeas.augeas()
        self.failUnless(a.get("/wrong/path") == None)

    def testMatch(self):
        "test aug_match"
        a = augeas.augeas()
        matches = a.match("/files/etc/hosts/*")
        self.failUnless(matches)
        for i in matches:
	    for attr in a.match(i+"/*"):
                self.failUnless(a.get(attr) != None)

def suite():
    suite = unittest.TestSuite()
    suite = unittest.makeSuite(TestAugeas, 'test')
    return suite

if __name__ == "__main__":
    testRunner = unittest.TextTestRunner(verbosity=2)
    result = testRunner.run(suite())
    sys.exit(not result.wasSuccessful())

__author__ = "Harald Hoyer <harald@redhat.com>"
