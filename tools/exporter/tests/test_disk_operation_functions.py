import os
import sys
import errno

import unittest
import mock
from mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'exporter'))
import exporter as exp

logger = exp.configure_logger()

class ExporterDiskFunctionsTestCase(unittest.TestCase):

    @patch('exporter.os')
    def test_create_directory_if_not_exists_calls_makedirs_with_supplied_arg(self, mock_os):
        args = ['a', 'b', 'c']
        for arg in args:
            exp.create_directory_if_not_exists(logger, arg)
            mock_os.makedirs.assert_called_with(arg)

    @patch('exporter.log_critical_error')
    @patch('exporter.os')
    def test_create_directory_if_not_exists_ignores_os_error_if_directory_exists(self, mock_os, mock_logger_critical_error):

        def mock_isdir(path):
            return True
        mock_os.makedirs.side_effect = OSError(errno.EEXIST)
        mock_os.path.isdir.side_effect = mock_isdir
        with self.assertRaises(OSError):
            exp.create_directory_if_not_exists(logger, 'x')
            mock_logger_critical_error.assert_not_called()

    @patch('exporter.log_critical_error')
    @patch('exporter.os')
    def test_create_directory_if_not_exists_logs_other_error(self, mock_os, mock_log_critical_error):
        mock_os.makedirs.side_effect = OSError(errno.ENOMEM)

        with self.assertRaises(OSError):
            exp.create_directory_if_not_exists(logger, 'x')
            mock_log_critical_error.assert_called()


    ###HOW TO MOCK OPEN()

    @patch('exporter.open')
    @patch('exporter.os')
    def test_save_exported_document(self, mock_os, mock_open):
        mock_file = mock.Mock()
        def returns_mock_file(path, action):
            mock_file.called_path = path
            mock_file.called_action = action
            return mock_file
        mock_open.side_effect = returns_mock_file

        def mock_isfile(path):
            return True
        mock_os.path.isfile.side_effect = mock_isfile

        def mock_join(dir, file):
            return 'joined_path'
        mock_os.path.join.side_effect = mock_join

        exp.save_exported_document(logger, 'edir', 'edoc', 'fname', 'ext')
        mock_os.path.join.assert_called_with('edir', 'fname.ext')
        mock_os.path.isfile.assert_called_with('joined_path')
        mock_open.assert_called_with('joined_path', 'w')
        mock_file.write.assert_called_with('edoc')

if __name__ == '__main__':
    unittest.main()