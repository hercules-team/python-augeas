from __future__ import print_function

import os
import sys
import unittest

import augeas

__mydir = os.path.dirname(sys.argv[0])
if not os.path.isdir(__mydir):
    __mydir = os.getcwd()

sys.path.insert(0, __mydir + "/..")


MYROOT = __mydir + "/testroot"

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
        a = augeas.Augeas(root=MYROOT)
        self.failUnless(a.get("/wrong/path") == None)
        del a

    def test02Match(self):
        "test aug_match"
        a = augeas.Augeas(root=MYROOT)
        matches = a.match("/files/etc/hosts/*")
        self.failUnless(matches)
        for i in matches:
            for attr in a.match(i+"/*"):
                self.failUnless(a.get(attr) != None)
        del a

    def test03PrintAll(self):
        "print all tree elements"
        output = open("test03PrintAll.out", "w")
        a = augeas.Augeas(root=MYROOT)
        path = "/"
        matches = recurmatch(a, path)
        for (p, attr) in matches:
            print(p, attr, file=output)
            self.failUnless(p != None and attr != None)
        output.close()

    def test04Grub(self):
        "test default setting of grub entry"
        a = augeas.Augeas(root=MYROOT)
        num = 0
        for entry in a.match("/files/etc/grub.conf/title"):
            num += 1
        self.assertEqual(num, 2)
        default = int(a.get("/files/etc/grub.conf/default"))
        self.assertEqual(default, 0)
        a.set("/files/etc/grub.conf/default", str(1))
        a.save()
        default = int(a.get("/files/etc/grub.conf/default"))
        self.assertEqual(default, 1)
        a.set("/files/etc/grub.conf/default", str(0))
        a.save()

    def test05Defvar(self):
        "test defvar"
        a = augeas.Augeas(root=MYROOT)
        a.defvar("hosts", "/files/etc/hosts")
        matches = a.match("$hosts/*")
        self.failUnless(matches)
        for i in matches:
            for attr in a.match(i+"/*"):
                self.failUnless(a.get(attr) != None)
        del a
        
    def test06Defnode(self):
        "test defnode"
        a = augeas.Augeas(root=MYROOT)
        a.defnode("bighost", "/files/etc/hosts/50/ipaddr", "192.168.1.1")
        value = a.get("$bighost")
        self.assertEqual(value, "192.168.1.1")
        del a

    def test07Setm(self):
        "test setm"
        a = augeas.Augeas(root=MYROOT)
        matches = a.match("/files/etc/hosts/*/ipaddr")
        self.failUnless(matches)
        a.setm("/files/etc/hosts", "*/ipaddr", "192.168.1.1")
        for i in matches:
            self.assertEqual(a.get(i), "192.168.1.1")
        del a

    def test08Span(self):
        "test span"
        data = [ {"expr": "/files/etc/hosts/1/ipaddr", "f": "hosts",
                  "ls": 0, "le": 0, "vs": 104, "ve": 113, "ss": 104, "se": 113},
                 {"expr": "/files/etc/hosts/1", "f": "hosts",
                  "ls": 0, "le": 0, "vs": 0, "ve": 0, "ss": 104, "se": 155},
                 {"expr": "/files/etc/hosts/*[last()]", "f": "hosts",
                  "ls": 0, "le": 0, "vs": 0, "ve": 0, "ss": 155, "se": 202},
                 {"expr": "/files/etc/hosts/#comment[2]", "f": "hosts",
                  "ls": 0, "le": 0, "vs": 58, "ve": 103, "ss": 56, "se": 104},
                 {"expr": "/files/etc/hosts", "f": "hosts",
                  "ls": 0, "le": 0, "vs": 0, "ve": 0, "ss": 0, "se":202 },
                ]
        a = augeas.Augeas(root=MYROOT, flags=augeas.Augeas.ENABLE_SPAN)
        for d in data:
            r = a.span(d["expr"])
            self.assertEquals(os.path.basename(r[0]), d["f"])
            self.assertEquals(r[1], d["ls"])
            self.assertEquals(r[2], d["le"])
            self.assertEquals(r[3], d["vs"])
            self.assertEquals(r[4], d["ve"])
            self.assertEquals(r[5], d["ss"])
            self.assertEquals(r[6], d["se"])

        error = None
        try:
            r = a.span("/files")
        except ValueError as e:
            error = e
        self.assertTrue(isinstance(error, ValueError))

        error = None
        try:
            r = a.span("/random")
        except ValueError as e:
            error = e
        self.assertTrue(isinstance(error, ValueError))

        del a

    def test09TextStore(self):
        hosts = "192.168.0.1 rtr.example.com router\n"
        a = augeas.Augeas(root=MYROOT)
        r = a.set("/raw/hosts", hosts);
        r = a.text_store("Hosts.lns", "/raw/hosts", "/t1")

        # Test bad lens name
        try:
            r = a.text_store("Notthere.lns", "/raw/hosts", "/t2")
        except ValueError as e:
            error = e
        self.assertTrue(isinstance(error, ValueError))

    def test10TextRetrieve(self):
        hosts = "192.168.0.1 rtr.example.com router\n"
        a = augeas.Augeas(root=MYROOT)
        r = a.set("/raw/hosts", hosts);
        r = a.text_store("Hosts.lns", "/raw/hosts", "/t1")
        r = a.text_retrieve("Hosts.lns", "/raw/hosts", "/t1", "/out/hosts")
        hosts_out = a.get("/out/hosts")
        self.assertEqual(hosts, hosts_out)

        # Test bad lens name
        try:
            r = a.text_store("Notthere.lns", "/raw/hosts", "/t2")
        except ValueError as e:
            error = e
        self.assertTrue(isinstance(error, ValueError))

    def test11Rename(self):
        a = augeas.Augeas(root=MYROOT)
        r = a.set("/a/b/c", "value");
        r = a.rename("/a/b/c", "d");
        self.assertEqual(r, 1)
        r = a.set("/a/e/d", "value2");
        r = a.rename("/a//d", "x");
        self.assertEqual(r, 2)
        try:
            r = a.rename("/a/e/x", "a/b");
        except ValueError as e:
            error = e
        self.assertTrue(isinstance(error, ValueError))

    def test12Transform(self):
        a = augeas.Augeas(root=MYROOT)

        r = a.transform("Foo", "/tmp/bar")
        lens = a.get("/augeas/load/Foo/lens")
        self.assertEqual(lens, "Foo.lns")
        incl = a.get("/augeas/load/Foo/incl")
        self.assertEqual(incl, "/tmp/bar")

        r = a.transform("Foo", "/tmp/baz", True)
        excl = a.get("/augeas/load/Foo/excl")
        self.assertEqual(excl, "/tmp/baz")

    def test13AddTransform(self):
        a = augeas.Augeas(root=MYROOT)

        r = a.add_transform("Foo", "/tmp/bar")
        incl = a.get("/augeas/load/Foo/incl")
        self.assertEqual(incl, "/tmp/bar")

        r = a.add_transform("Foo", "/tmp/bar", "Faz", "/tmp/baz")
        excl = a.get("/augeas/load/Foo/excl")
        self.assertEqual(excl, "/tmp/baz")

    def test14Label(self):
        a = augeas.Augeas(root=MYROOT)

        lbl = a.label("/augeas/version")
        self.assertEqual(lbl, "version")

    def test15Copy(self):
        a = augeas.Augeas(root=MYROOT)

        orig_path = '/tmp/src/copy_test/a'
        copy_path = '/tmp/dst/copy_test/a'
        orig_value = 'test value'

        a.set(orig_path, orig_value)

        matches = a.match(orig_path)
        self.failUnless(matches)

        a.copy(orig_path, copy_path)

        matches = a.match(copy_path)
        self.failUnless(matches)
        self.assertEqual(a.get(copy_path), a.get(orig_path))


def getsuite():
    suite = unittest.TestSuite()
    suite = unittest.makeSuite(TestAugeas, 'test')
    return suite

if __name__ == "__main__":
    __testRunner = unittest.TextTestRunner(verbosity=2)
    __result = __testRunner.run(getsuite())
    sys.exit(not __result.wasSuccessful())

__author__ = "Harald Hoyer <harald@redhat.com>"
