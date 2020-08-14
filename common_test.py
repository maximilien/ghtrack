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

if __name__ == '__main__':
    unittest.main()