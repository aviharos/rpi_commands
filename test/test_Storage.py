import os
import sys
import unittest
from modules import reupload_jsons_to_Orion

sys.path.insert(0, os.path.join("..", "src"))
from Storage import Storage
import Orion

TL_STORAGE_ID = "urn:ngsi_ld:Storage:TrayLoaderStorage1"
TUL_STORAGE_ID = "urn:ngsi_ld:Storage:TrayUnloaderStorage1"

class TestStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        reupload_jsons_to_Orion.main()
        self.trayLoaderStorage = Storage(TL_STORAGE_ID, capacity=2, step_size=-1, type="emptying")
        self.trayUnloaderStorage = Storage(TUL_STORAGE_ID, capacity=2, step_size=1, type="filling")

    def tearDown(self):
        pass

    def test_step_reset(self):
        # TrayLoaderStorage1
        self.assertEqual(2, self.trayLoaderStorage.counter)

        self.trayLoaderStorage.step()
        self.assertEqual(1, self.trayLoaderStorage.counter)
        tl_storage_obj = Orion.get(TL_STORAGE_ID)
        self.assertEqual(1, tl_storage_obj["Counter"]["value"])

        self.trayLoaderStorage.reset()
        self.assertEqual(2, self.trayLoaderStorage.counter)
        tl_storage_obj = Orion.get(TL_STORAGE_ID)
        self.assertEqual(2, tl_storage_obj["Counter"]["value"])

        # TrayUnloaderStorage1
        self.assertEqual(0, self.trayUnloaderStorage.counter)

        self.trayUnloaderStorage.step()
        self.assertEqual(1, self.trayUnloaderStorage.counter)
        tul_storage_obj = Orion.get(TUL_STORAGE_ID)
        self.assertEqual(1, tul_storage_obj["Counter"]["value"])

        self.trayUnloaderStorage.reset()
        self.assertEqual(0, self.trayUnloaderStorage.counter)
        tul_storage_obj = Orion.get(TUL_STORAGE_ID)
        self.assertEqual(0, tul_storage_obj["Counter"]["value"])


if __name__ == "__main__":
    unittest.main()

