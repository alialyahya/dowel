"""A `dowel.logger.LogOutput` for CSV files."""
import csv

from dowel import TabularInput
from dowel.simple_outputs import FileOutput


class CsvOutput(FileOutput):
    """CSV file output for logger.

    :param file_name: The file this output should log to.
    """

    def __init__(self, file_name):
        super().__init__(file_name)
        self._writer = None
        self._fieldnames = None

    @property
    def types_accepted(self):
        """Accept TabularInput objects only."""
        return (TabularInput, )

    def record(self, data, prefix=''):
        """Log tabular data to CSV."""
        if isinstance(data, TabularInput):

            to_csv = data.as_primitive_dict

            if not to_csv.keys() and not self._writer:
                return

            if not self._writer:
                self._fieldnames = set(to_csv.keys())
                self._writer = csv.DictWriter(self._log_file,
                                              fieldnames=self._fieldnames)
                self._writer.writeheader()

            if set(to_csv.keys()) - self._fieldnames:
                # setting the file pointer to the
                # start of the file in order to rewrite the csv
                self._log_file.seek(0)

                # adding the new keys to the current fieldnames
                for possible_newkey in set(to_csv.keys()):
                    if possible_newkey not in self._fieldnames:
                        self._fieldnames.add(possible_newkey)

                # creating new writer object for new fieldnames
                self._writer = csv.DictWriter(self._log_file,
                                              fieldnames=self._fieldnames)

                # reading past data to add new keys
                tmp_file = self._log_file.name
                with open(tmp_file, 'r+', newline='') as csvfile:
                    tmp_reader = csv.DictReader(csvfile)
                    tmp_data = []
                    for old_data in tmp_reader:
                        for field in self._fieldnames:
                            if field not in old_data:
                                old_data[field] = ''
                        tmp_data.append(old_data)

                self._writer.writeheader()
                for i in tmp_data:
                    self._writer.writerow(i)

            self._writer.writerow(to_csv)

            for k in to_csv.keys():
                data.mark(k)

        else:
            raise ValueError('Unacceptable type.')
