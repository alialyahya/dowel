import csv
import tempfile

import pytest

from dowel import CsvOutput, TabularInput


class TestCsvOutput:

    def setup_method(self):
        self.log_file = tempfile.NamedTemporaryFile()
        self.csv_output = CsvOutput(self.log_file.name)
        self.tabular = TabularInput()
        self.tabular.clear()

    def teardown_method(self):
        self.log_file.close()

    def test_record(self):
        foo = 1
        bar = 10
        self.tabular.record('foo', foo)
        self.tabular.record('bar', bar)
        self.csv_output.record(self.tabular)
        self.tabular.record('foo', foo * 2)
        self.tabular.record('bar', bar * 2)
        self.csv_output.record(self.tabular)
        self.csv_output.dump()

        correct = [
            {'foo': str(foo), 'bar': str(bar)},
            {'foo': str(foo * 2), 'bar': str(bar * 2)},
        ]  # yapf: disable
        self.assert_csv_matches(correct)

    def test_record_inconsistent(self):

        self.tabular.record('first', 50)
        self.csv_output.record(self.tabular)
        self.csv_output.dump()

        self.tabular.record('first', 100)
        self.tabular.record('second', 200)
        self.csv_output.record(self.tabular)

        self.csv_output.dump()
        correct = [{
            'first': str(50),
            'second': ''
        }, {
            'first': str(100),
            'second': str(200)
        }]

        self.assert_csv_matches(correct)

    def test_empty_record(self):
        self.csv_output.record(self.tabular)
        assert not self.csv_output._writer

        foo = 1
        bar = 10
        self.tabular.record('foo', foo)
        self.tabular.record('bar', bar)
        self.csv_output.record(self.tabular)
        assert self.csv_output._fieldnames

    def test_unacceptable_type(self):
        with pytest.raises(ValueError):
            self.csv_output.record('foo')

    def assert_csv_matches(self, correct):
        """Check the first row of a csv file and compare it to known values."""
        with open(self.log_file.name, 'r') as file:
            reader = csv.DictReader(file)

            for correct_row in correct:
                row = next(reader)
                assert row == correct_row
