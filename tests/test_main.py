from datetime import datetime
from io import StringIO
import json
import os
import sys
from unittest import TestCase
from unittest.mock import patch

from freezegun import freeze_time
from lxml import etree
from src import main


class TestCalculate(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.freezing_time = freeze_time(datetime(2007, 12, 12))
        cls.freezing_time.start()
        cls.test_file = 'tests/test_input.xml'

    @classmethod
    def tearDownClass(cls) -> None:
        cls.freezing_time.stop()

    def test_success(self):
        expected = {
            'user0': {
                '2007-12-12': 3600,
                '2007-12-13': 3600,
            },
            'user1': {
                '2007-12-12': 3600,
                '2007-12-13': 3600,
            },
        }
        self.assertDictEqual(main.calculate(self.test_file), expected)

    def test_success_with_start_filter(self):
        expected = {
            'user0': {
                '2007-12-13': 3600,
            },
            'user1': {
                '2007-12-13': 3600,
            },
        }
        result = main.calculate(
            self.test_file, start_filter=datetime(2007, 12, 13)
        )
        self.assertDictEqual(result, expected)

    def test_success_with_end_filter(self):
        expected = {
            'user0': {
                '2007-12-12': 3600,
            },
            'user1': {
                '2007-12-12': 3600,
            },
        }
        result = main.calculate(
            self.test_file, end_filter=datetime(2007, 12, 13)
        )
        self.assertDictEqual(result, expected)

    def test_success_with_users_filter(self):
        expected = {
            'user0': {
                '2007-12-12': 3600,
                '2007-12-13': 3600,
            }
        }
        result = main.calculate(self.test_file, users_filter=['user0'])
        self.assertDictEqual(result, expected)

    def test_invalid_end_date(self):
        root = etree.Element("people")
        person = etree.SubElement(root, "person", attrib={'full_name': 'user'})
        start = etree.SubElement(person, "start")
        start.text = '12-12-2007 00:00:00'
        end = etree.SubElement(person, "end")
        end.text = 'asd'

        file = open('asdasdasd.xml', 'wt')

        file.write(
            etree.tostring(
                root, xml_declaration=True, pretty_print=True, encoding='utf-8'
            ).decode()
        )
        file.close()
        log_message = """WARNING:src.main:---
Skipped! time data 'asd' does not match format '%d-%m-%Y %H:%M:%S'
<person full_name="user">
    <start>12-12-2007 00:00:00</start>
    <end>asd</end>
</person>
---"""
        with self.assertLogs(main.logger, level='DEBUG') as cm:
            main.calculate(file.name)
        self.assertEqual(cm.output[0], log_message)
        os.remove(file.name)

    def test_invalid_start_date(self):
        root = etree.Element("people")
        person = etree.SubElement(root, "person", attrib={'full_name': 'user'})
        start = etree.SubElement(person, "start")
        start.text = 'asd'
        end = etree.SubElement(person, "end")
        end.text = '12-12-2007 00:00:00'

        file = open('asdasdasd.xml', 'wt')

        file.write(
            etree.tostring(
                root, xml_declaration=True, pretty_print=True, encoding='utf-8'
            ).decode()
        )
        file.close()
        log_message = """WARNING:src.main:---
Skipped! time data 'asd' does not match format '%d-%m-%Y %H:%M:%S'
<person full_name="user">
    <start>asd</start>
    <end>12-12-2007 00:00:00</end>
</person>
---"""
        with self.assertLogs(main.logger, level='DEBUG') as cm:
            main.calculate(file.name)
        self.assertEqual(cm.output[0], log_message)
        os.remove(file.name)

    def test_no_username_field(self):
        root = etree.Element("people")
        person = etree.SubElement(root, "person")
        start = etree.SubElement(person, "start")
        start.text = 'asd'
        end = etree.SubElement(person, "end")
        end.text = 'asdasd'

        file = open('asdasdasd.xml', 'wt')

        file.write(
            etree.tostring(
                root, xml_declaration=True, pretty_print=True, encoding='utf-8'
            ).decode()
        )
        file.close()

        log_message = """WARNING:src.main:---
Skipped! field "full_name" is not specified
<person>
    <start>asd</start>
    <end>asdasd</end>
</person>
---"""
        with self.assertLogs(main.logger, level='DEBUG') as cm:
            main.calculate(file.name)
        self.assertEqual(cm.output[0], log_message)
        os.remove(file.name)

    def test_no_start_field(self):
        root = etree.Element("people")
        person = etree.SubElement(root, "person", attrib={'full_name': 'user'})
        end = etree.SubElement(person, "end")
        end.text = '12-12-2007 00:00:00'
        random_field = etree.SubElement(person, "random_field")
        random_field.text = '12-12-2007 00:00:00'
        file = open('asdasdasd.xml', 'wt')

        file.write(
            etree.tostring(
                root, xml_declaration=True, pretty_print=True, encoding='utf-8'
            ).decode()
        )
        file.close()
        log_message = """WARNING:src.main:---
Skipped! not found "start" or "end" field in element
<person full_name="user">
    <end>12-12-2007 00:00:00</end>
    <random_field>12-12-2007 00:00:00</random_field>
</person>
---"""
        with self.assertLogs(main.logger, level='DEBUG') as cm:
            main.calculate(file.name)
        self.assertEqual(cm.output[0], log_message)
        os.remove(file.name)

    def test_no_end_field(self):
        root = etree.Element("people")
        person = etree.SubElement(root, "person", attrib={'full_name': 'user'})
        start = etree.SubElement(person, "start")
        start.text = '12-12-2007 00:00:00'
        random_field = etree.SubElement(person, "random_field")
        random_field.text = '12-12-2007 00:00:00'
        file = open('asdasdasd.xml', 'wt')

        file.write(
            etree.tostring(
                root, xml_declaration=True, pretty_print=True, encoding='utf-8'
            ).decode()
        )
        file.close()
        log_message = """WARNING:src.main:---
Skipped! not found "start" or "end" field in element
<person full_name="user">
    <start>12-12-2007 00:00:00</start>
    <random_field>12-12-2007 00:00:00</random_field>
</person>
---"""
        with self.assertLogs(main.logger, level='DEBUG') as cm:
            main.calculate(file.name)
        self.assertEqual(cm.output[0], log_message)
        os.remove(file.name)

    def test_more_than_24_hours_field(self):
        root = etree.Element("people")
        person = etree.SubElement(root, "person", attrib={'full_name': 'user'})
        start = etree.SubElement(person, "start")
        start.text = '12-12-2007 00:00:00'

        end = etree.SubElement(person, "end")
        end.text = '14-12-2007 00:00:00'

        file = open('asdasdasd.xml', 'wt')

        file.write(
            etree.tostring(
                root, xml_declaration=True, pretty_print=True, encoding='utf-8'
            ).decode()
        )
        file.close()
        log_message = """WARNING:src.main:---
Added more than 24 hours a day
<person full_name="user">
    <start>12-12-2007 00:00:00</start>
    <end>14-12-2007 00:00:00</end>
</person>
---"""
        with self.assertLogs(main.logger, level='DEBUG') as cm:
            main.calculate(file.name)
        self.assertEqual(cm.output[0], log_message)
        os.remove(file.name)

    def test_invalid_xml_syntax(self):
        file = open('asdasdasd.xml', 'wt')
        file.write("qwdqwd")
        file.close()
        with self.assertRaises(main.AppException) as exc:
            main.calculate(file.name)
        self.assertIsInstance(exc.exception, main.AppException)
        self.assertEqual(
            exc.exception.args[0],
            'Invalid syntax: Document is empty, line 1, column 1',
        )


class TestOutputTimedelta(TestCase):
    def test_success(self):
        self.assertEqual(main.output_timedelta(3600), '1 h, 0 m, 0 s')


class TestConsoleOutput(TestCase):
    def test_success(self):
        expected = """---
user
date        duration
2007-12-12  1 h, 0 m, 0 s
2007-12-13  1 h, 0 m, 0 s
---
---
user2
date        duration
2007-12-12  1 h, 0 m, 0 s
2007-12-13  1 h, 0 m, 0 s
---
"""
        self.assertEqual(
            main.console_output(
                {
                    'user': {'2007-12-12': 3600, '2007-12-13': 3600},
                    'user2': {'2007-12-12': 3600, '2007-12-13': 3600},
                }
            ),
            expected,
        )


class TestRun(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.freezing_time = freeze_time(datetime(2007, 12, 12))
        cls.freezing_time.start()

        root = etree.Element("people")
        person = etree.SubElement(root, "person", attrib={'full_name': 'user'})
        start = etree.SubElement(person, "start")
        start.text = '12-12-2007 00:00:00'
        end = etree.SubElement(person, "end")
        end.text = '12-12-2007 01:00:00'
        cls.file = open('asdasdasd.xml', 'wt')

        cls.file.write(
            etree.tostring(
                root, xml_declaration=True, pretty_print=True, encoding='utf-8'
            ).decode()
        )
        cls.file.close()

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.file.name)
        cls.freezing_time.stop()

    def test_success(self):

        sys.argv[1:] = [self.file.name]
        with patch('sys.stdout', new=StringIO()) as mocked_stdout:
            main.run()
        expected = """---
user
date        duration
2007-12-12  1 h, 0 m, 0 s
---
"""
        self.assertEqual(expected, mocked_stdout.getvalue())

    def test_success_json_output(self):
        sys.argv[1:] = [self.file.name, '--output=json']
        with patch('sys.stdout', new=StringIO()) as mocked_stdout:
            main.run()
        expected = json.dumps({"user": {"2007-12-12": 3600}})
        self.assertEqual(expected, mocked_stdout.getvalue())

    def test_no_file(self):
        sys.argv[1:] = []
        with self.assertRaises(SystemExit):
            with patch('sys.stderr', new=StringIO()) as mocked_stderr:
                main.run()

        expected = (
            "usage: python -m unittest [-h] [--start START] "
            "[--end END] [--users USERS] [--output {json,console}] file\n"
            "python -m unittest: error: the following arguments are "
            "required: file\n"
        )
        self.assertEqual(mocked_stderr.getvalue(), expected)

    def test_file_not_found(self):
        sys.argv[1:] = ['gg.xml']
        with self.assertRaises(SystemExit) as exc:
            with self.assertLogs(main.logger, level='DEBUG') as cm:
                main.run()
        self.assertEqual(exc.exception.args[0], 1)
        self.assertEqual(cm.output[0], 'ERROR:src.main:file gg.xml not found')

    def test_invalid_syntax(self):
        file = open('dd.xml', 'wt')
        file.write('qwd')
        file.close()
        sys.argv[1:] = [file.name]
        with self.assertRaises(SystemExit) as exc:
            with self.assertLogs(main.logger, level='DEBUG') as cm:
                main.run()
        self.assertEqual(exc.exception.args[0], 1)
        self.assertEqual(
            cm.output[0],
            'ERROR:src.main:Invalid syntax: '
            'Document is empty, line 1, column 1',
        )
        os.remove(file.name)
