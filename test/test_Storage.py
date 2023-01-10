import os
import sys
import unittest
from modules import reupload_jsons_to_Orion

import requests

sys.path.insert(0, os.path.join("..", "src"))
from Storage import Storage
import Orion

session = requests.Session()

TL_STORAGE_ID = "urn:ngsiv2:i40Asset:TrayLoaderStorage1"
TUL_STORAGE_ID = "urn:ngsiv2:i40Asset:TrayUnloaderStorage1"

class TestStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        reupload_jsons_to_Orion.main()
        self.trayLoaderStorage = Storage(session, TL_STORAGE_ID, capacity=2, step_size=-1, type="emptying")
        self.trayUnloaderStorage = Storage(session, TUL_STORAGE_ID, capacity=0, step_size=1, type="filling")

    def tearDown(self):
        pass

    def test_step_reset(self):
        # TrayLoaderStorage1
        self.assertEqual(2, self.trayLoaderStorage.counter)

        self.trayLoaderStorage.step()
        self.assertEqual(1, self.trayLoaderStorage.counter)
        tl_storage_obj = Orion.get(session, TL_STORAGE_ID)
        self.assertEqual(1, tl_storage_obj["counter"]["value"])

        self.trayLoaderStorage.set_full()
        self.assertEqual(2, self.trayLoaderStorage.counter)
        tl_storage_obj = Orion.get(session, TL_STORAGE_ID)
        self.assertEqual(2, tl_storage_obj["counter"]["value"])

        # TrayUnloaderStorage1
        self.assertEqual(0, self.trayUnloaderStorage.counter)

        self.trayUnloaderStorage.step()
        self.assertEqual(1, self.trayUnloaderStorage.counter)
        tul_storage_obj = Orion.get(session, TUL_STORAGE_ID)
        self.assertEqual(1, tul_storage_obj["counter"]["value"])

        self.trayUnloaderStorage.set_empty()
        self.assertEqual(0, self.trayUnloaderStorage.counter)
        tul_storage_obj = Orion.get(session, TUL_STORAGE_ID)
        self.assertEqual(0, tul_storage_obj["counter"]["value"])


if __name__ == "__main__":
    unittest.main()

