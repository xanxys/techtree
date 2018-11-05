#!/bin/python3
import numpy as np
import csv
import re


class InputCoefficientTable:
    def __init__(self, path):
        self._parse_jp_input_coeff_table(path)

        for ix_code in range(self.num_codes):
            top_inputs = sorted(
                enumerate(self.coeff_matrix[:, ix_code]), key=lambda t: t[1], reverse=True)

            print(self.coeff_code_names[ix_code], ["%.3f:%s" % (
                k, self.coeff_code_names[i]) for (i, k) in top_inputs[:5]])

    def _parse_jp_input_coeff_table(self, path):
        """
        Parse input coefficient table in .csv, as downloaded from https://www.e-stat.go.jp

        raises: ValueError
        """

        rows = []
        with open(path, encoding='Shift-JIS') as f:
            for row in csv.reader(f, delimiter=',', quotechar='"'):
                rows.append(row)

        if not all(len(row) == len(rows[0]) for row in rows[1:]):
            raise ValueError(
                "Unexpected table dimensions. Disable e.g. 'include annotations' options.")

        # (ugly) table specifc magic numbers
        COL_IX_TYPE = 1
        COL_IX_CODE = 2
        COL_IX_CODE_NAME = 3
        COL_IX_DATA_START = 5
        COL_IX_DATA_END = -1  # exclusive. Last column is average
        ROW_IX_CODE = 0
        ROW_IX_CODE_NAME = 1
        ROW_IX_DATA_START = 2

        list_codes = rows[ROW_IX_CODE][COL_IX_DATA_START:COL_IX_DATA_END]
        code_to_name_table = dict(zip(rows[ROW_IX_CODE][COL_IX_DATA_START:COL_IX_DATA_END],
                                      map(self.cleanup_codename, rows[ROW_IX_CODE_NAME][COL_IX_DATA_START:COL_IX_DATA_END])))

        ix_list_code = 0
        verified_data_rows = []
        special_data = {}
        for data_row in rows[ROW_IX_DATA_START:]:
            if not data_row[COL_IX_TYPE] == '投入係数':
                raise ValueError("Unexpected row type: " +
                                 data_row[COL_IX_TYPE])

            code = data_row[COL_IX_CODE]
            if code in code_to_name_table:
                if code != list_codes[ix_list_code]:
                    raise ValueError("Inconsitent code ordering")
                ix_list_code += 1
                verified_data_rows.append(
                    data_row[COL_IX_DATA_START:COL_IX_DATA_END])
            else:
                special_data[data_row[COL_IX_CODE_NAME]
                             ] = data_row[COL_IX_DATA_START:COL_IX_DATA_END]

        coeff_matrix = np.array(verified_data_rows, dtype='float32')
        if coeff_matrix.shape[0] != coeff_matrix.shape[1]:
            raise ValueError(
                "Coeff matrix was not square; invalid table format")
        if coeff_matrix.shape != (len(verified_data_rows), len(verified_data_rows)):
            raise ValueError("Coeff matrix size and code size not matching")

        self.num_codes = len(list_codes)
        self.coeff_code_names = [code_to_name_table[code]
                                 for code in list_codes]
        self.coeff_matrix = coeff_matrix

    @staticmethod
    def cleanup_codename(codename_with_prefix):
        """
        Returns real japanese codename e.g. "飲食サービス" from number-prefixed input e.g. "6721_飲食サービス"
        """
        ix = codename_with_prefix.find('_')
        if ix >= 0:
            return codename_with_prefix[ix+1:]
        else:
            return codename_with_prefix


def main():
    table = InputCoefficientTable('data-jp/2011-input_coeff_table.csv')


if __name__ == '__main__':
    main()
