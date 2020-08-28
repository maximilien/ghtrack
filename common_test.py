# Copyright © 2020 IBM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, unittest

from common import *
from io import StringIO

class TestConsole(unittest.TestCase):
    def setUp(self):
        self.backup_out = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self.backup_out

    def test_print(self):
        Console.print("test data")
        self.assertTrue("test data" in sys.stdout.getvalue())

    def test_println(self):
        Console.println()
        self.assertTrue("\n" in sys.stdout.getvalue())

    def test_ok(self):
        Console.ok("OK")
        self.assertTrue("OK" in sys.stdout.getvalue())

    def test_error(self):
        Console.error("ERROR")
        self.assertTrue("ERROR" in sys.stdout.getvalue())

    def test_fail(self):
        Console.fail("FAIL")
        self.assertTrue("FAIL" in sys.stdout.getvalue())

    def test_warn(self):
        Console.warn("WARN")
        self.assertTrue("WARN" in sys.stdout.getvalue())

    def test_progress(self):
        Console.progress(1, 100, "100")
        output = sys.stdout.getvalue()
        self.assertTrue("[=" in output)
        self.assertTrue("100" in output)

class TestRateLimitData(unittest.TestCase):
    def setUp(self):
        self.rate_limit_data = RateLimitData(1, 2)

    def tearDown(self):
        self.rate_limit_data = None

    def test_max_calls(self):
        self.assertEqual(self.rate_limit_data.max_calls(), 1)

    def test_set_max_calls(self):
        self.rate_limit_data.set_max_calls(2)
        self.assertEqual(self.rate_limit_data.max_calls(), 2)

    def test_max_calls(self):
        self.rate_limit_data = RateLimitData(10, 10, False, True)
        max_calls = self.rate_limit_data.max_calls()
        self.assertTrue(max_calls >= 1)
        self.assertTrue(max_calls <= 10)

    def test_sleep(self):
        self.assertEqual(self.rate_limit_data.sleep(), 2)

    def test_set_sleep(self):
        self.rate_limit_data.set_sleep(1)
        self.assertEqual(self.rate_limit_data.sleep(), 1)

    def test_sleep_random(self):
        self.rate_limit_data = RateLimitData(10, 10, False, True)
        sleep = self.rate_limit_data.sleep()
        self.assertTrue(sleep >= 1)
        self.assertTrue(sleep <= 10)

    def test_enabled_default(self):
        self.assertFalse(self.rate_limit_data.enabled())

    def test_enabled_True(self):
        self.rate_limit_data.set_enabled(True)
        self.assertTrue(self.rate_limit_data.enabled())
        self.rate_limit_data.set_enabled(False)
        self.assertFalse(self.rate_limit_data.enabled())

if __name__ == '__main__':
    unittest.main()