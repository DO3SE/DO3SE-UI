import unittest
import StringIO

import do3se.dataset as dataset


class TestCSVLoader(unittest.TestCase):
    CSVEXAMPLE = """\
"foo","bar","baz"
3,4,5
1,xyz,3
6,8,10
1,"xyz",3
1,,3
12,15.3,12.0e-3"""

    def setUp(self):
        self.infile = StringIO.StringIO(self.CSVEXAMPLE)

    def tearDown(self):
        del self.infile

    def test_not_enough_trim(self):
        self.assertRaises(dataset.NotEnoughTrimError, dataset.data_from_csv,
                          self.infile, ('foo', 'bar', 'baz'), 0)

    def test_not_enough_columns(self):
        self.assertRaises(dataset.NotEnoughColumnsError, dataset.data_from_csv,
                          self.infile, ('foo', 'bar', 'baz', 'boggle'), 1)

    def test_unquoted_string(self):
        self.assertRaises(dataset.UnquotedStringError, dataset.data_from_csv,
                          self.infile, ('foo', 'bar', 'baz'), 1)

    def test_invalid_data(self):
        self.assertRaises(dataset.InvalidDataError, dataset.data_from_csv,
                          self.infile, ('foo', 'bar', 'baz'), 3)

    def test_missing_data(self):
        self.assertRaises(dataset.InvalidDataError, dataset.data_from_csv,
                          self.infile, ('foo', 'bar', 'baz'), 5)

    def test_all_correct(self):
        data = dataset.data_from_csv(self.infile, ('foo', 'bar', 'baz'), 6)
        self.assertEqual(data, [{'foo': 12, 'bar': 15.3, 'baz': 0.012}])

    def test_no_data(self):
        self.assertRaises(dataset.NoDataError, dataset.data_from_csv,
                          self.infile, ('foo', 'bar', 'baz'), 7)


if __name__ == '__main__':
    unittest.main()
