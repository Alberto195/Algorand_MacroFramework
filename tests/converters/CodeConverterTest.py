import unittest

from converters.CodeConverter import CodeConverter


class TestSum(unittest.TestCase):

    def test_global_put_int_1(self):
        cc = CodeConverter()
        text = cc.global_put_int("key", "value", True, False)
        self.assertEqual(text,
                         "App.globalPut(Bytes(\"key\"), value),\n",
                         "Should be App.globalPut(Bytes(\"key\"), value),\n"
                         )

    def test_global_put_int_2(self):
        cc = CodeConverter()
        text = cc.global_put_int("key", "value", False, False)
        self.assertEqual(text,
                         "\tApp.globalPut(Bytes(\"key\"), value),\n",
                         "Should be \tApp.globalPut(Bytes(\"key\"), value),\n"
                         )

    def test_global_put_bytes_1(self):
        cc = CodeConverter()
        text = cc.global_put_int("key", "value", False, False)
        self.assertEqual(text,
                         "\tApp.globalPut(Bytes(\"key\"), value),\n",
                         "Should be \tApp.globalPut(Bytes(\"{key}\"), {value}),\n"
                         )

    def test_global_put_bytes_2(self):
        cc = CodeConverter()
        text = cc.global_put_int("key", "value", True, False)
        self.assertEqual(text,
                         "App.globalPut(Bytes(\"key\"), value),\n",
                         "Should be App.globalPut(Bytes(\"key\"), value),\n"
                         )

    def test_local_put_int_1(self):
        cc = CodeConverter()
        text = cc.local_put_int("key", "value", False)
        self.assertEqual(text,
                         "App.localPut(Int(0), Bytes(\"key\"), value),\n",
                         "Should be App.localPut(Int(0), Bytes(\"key\"), value),\n"
                         )

    def test_local_put_int_2(self):
        cc = CodeConverter()
        text = cc.local_put_int("key", "value", True)
        self.assertEqual(cc.local_ints,
                         1,
                         "Should be 1"
                         )

    def test_local_put_bytes_1(self):
        cc = CodeConverter()
        text = cc.local_put_bytes("key", "value", False)
        self.assertEqual(text,
                         "App.localPut(Int(0), Bytes(\"key\"), value),\n",
                         "Should be App.localPut(Int(0), Bytes(\"key\"), value),\n"
                         )

    def test_local_put_bytes_2(self):
        cc = CodeConverter()
        text = cc.local_put_bytes("key", "value", True)
        self.assertEqual(cc.local_bytes,
                         1,
                         "Should be 1"
                         )

    def test_global_get_1(self):
        cc = CodeConverter()
        text = cc.global_get("key", True, True)
        self.assertEqual(text,
                         "App.globalGet(Bytes(\"key\"))",
                         "Should be App.globalGet(Bytes(\"key\"))"
                         )

    def test_global_get_2(self):
        cc = CodeConverter()
        text = cc.global_get("key", False, True)
        self.assertEqual(text,
                         "\tApp.globalGet(Bytes(\"key\"))",
                         "Should be \tApp.globalGet(Bytes(\"key\"))"
                         )

    def test_global_get_3(self):
        cc = CodeConverter()
        text = cc.global_get("key", False, False)
        self.assertEqual(text,
                         "\tApp.globalGet(Bytes(\"key\")),\n",
                         "Should be \tApp.globalGet(Bytes(\"key\")),\n"
                         )

    def test_local_get_1(self):
        cc = CodeConverter()
        text = cc.local_get("key", False, False)
        self.assertEqual(text,
                         "\tApp.localGet(Int(0), Bytes(\"key\")),\n",
                         "Should be \tApp.localGet(Int(0), \"key\")),\n"
                         )

    def test_local_get_2(self):
        cc = CodeConverter()
        text = cc.local_get("key", False, True)
        self.assertEqual(text,
                         "\tApp.localGet(Int(0), Bytes(\"key\"))",
                         "Should be \tApp.localGet(Bytes(Int(0), Bytes(\"key\"))"
                         )

    def test_local_get_3(self):
        cc = CodeConverter()
        text = cc.local_get("key", True, True)
        self.assertEqual(text,
                         "App.localGet(Int(0), Bytes(\"key\"))",
                         "Should be App.localGet(Bytes(Int(0), Bytes(\"key\"))"
                         )

    def test_unix_time(self):
        cc = CodeConverter()
        text = cc.unix_time()
        self.assertEqual(text,
                         "Global.round()",
                         "Should be Global.round()"
                         )

if __name__ == '__main__':
    unittest.main()
