#!/usr/bin/env python3

import unittest
from raster import Raster

class TestRaster(unittest.TestCase):

    def test_parsemetadata(self):
        key = """10 5
1
3
2
3
1
1
1
3
1 1
3
1
1 1
8 1
3 1 1
1 1 1""".split("\n")
        internals = Raster.parse_metadata(key)
        print(Raster(**internals))
        #self.assertParseMeta({'col_meta': [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}],
        #    'table': [bytearray(b'..........'), bytearray(b'..........'),
        #        bytearray(b'..........'), bytearray(b'..........'),
        #        bytearray(b'..........')], 'row_meta': [{}, {}, {}, {}, {}]},
        #    key)

    def assertParseMeta(self, expected_result, input_):
        self.assertEqual(expected_result, Raster.parse_metadata(input_))


if __name__ == '__main__':
    unittest.main()
