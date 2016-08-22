#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run the test, run this in the this of repo:
python -m unittest discover
"""
import unittest

from dot import Dot, LazyDot


class This(Dot):

    def __init__(self, *args, **kwargs):
        super(This, self).__init__(*args, **kwargs)
        self.counter = 0
        self.items = {}
        self.setup()

    def load(self, paths):
        # imagine counter as being a hit counter to the external resource
        # to get the object.
        self.counter += 1
        return {i: self.items[i] if i in self.items else "value %s" % i for i in paths}

    def save(self, path, value):
        self.items[path] = value


class That(This):
    pass


class DotTestCase(unittest.TestCase):

    def test_one_object(self):
        this = This()
        aa = this.part1.part2.part3.part4
        self.assertEqual(str(aa), 'value this.part1.part2.part3.part4')

    def test_one_int_object(self):
        this = This()
        aa = this.part1.part2.i120.part4
        self.assertEqual(str(aa), 'value this.part1.part2.120.part4')

    def test_one_int_object2(self):
        this = This()
        aa = this.part1.part2.i120
        self.assertEqual(str(aa), 'value this.part1.part2.120')

    def test_getitem(self):
        this = This()
        aa = this['part1.part2.part4']
        self.assertEqual(str(aa), 'value this.part1.part2.part4')

    def test_change_root_name(self):
        this = This(root_name='my')
        aa = this.part1.part2.part3.part4
        self.assertEqual(str(aa), 'value my.part1.part2.part3.part4')

    def test_change_root_name_by_class_name(self):
        that = That()
        aa = that.part1.part2.part3.part4
        self.assertEqual(str(aa), 'value that.part1.part2.part3.part4')

    def test_several_object(self):
        this = This()
        aa = this.part1.part2.part3.part4
        bb = this.part10
        self.assertEqual(str(aa), 'value this.part1.part2.part3.part4')
        self.assertEqual(str(bb), 'value this.part10')

    def test_several_object_called_once(self):
        this = This()
        aa = this.part1.part2.part3.part4
        bb = this.part10
        self.assertEqual(this.counter, 0)
        str(aa)
        self.assertEqual(this.counter, 1)
        cc = this.part10
        str(cc)
        self.assertEqual(this.counter, 1)
        dd = this.something_else
        self.assertEqual(this.counter, 1)
        str(dd)
        self.assertEqual(this.counter, 2)

    def test_save_one_object_long_path(self):
        this = This()
        this.part1.part2.part3.part4 = "new value"
        aa = this.part1.part2.part3.part4
        self.assertEqual(str(aa), "new value")
        self.assertEqual(this.counter, 0)
        # Even though the str(aa) returns string,
        # it should be still an instance of LazyDot
        self.assertIsInstance(aa, LazyDot)

    def test_save_one_object_part1(self):
        this = This()
        this.hello = "new value"
        aa = this.hello
        self.assertEqual(str(aa), "new value")
        self.assertEqual(this.counter, 0)
        self.assertIsInstance(aa, LazyDot)

    def test_flush(self):
        this = This()
        aa = this.part10
        self.assertEqual(this.counter, 0)
        str(aa)
        self.assertEqual(this.counter, 1)
        cc = this.part10
        str(cc)
        self.assertEqual(this.counter, 1)
        this.flush()
        dd = this.part10
        str(dd)
        self.assertEqual(this.counter, 2)
