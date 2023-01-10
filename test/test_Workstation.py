import os
import sys
import unittest
from modules import reupload_jsons_to_Orion

import requests

sys.path.insert(0, os.path.join("..", "src"))
from Workstation import Workstation
import Orion

WORKSTATION_ID = "urn:ngsiv2:i40Asset:InjectionMouldingMachine1"

class TestWorkstation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        reupload_jsons_to_Orion.main()
        self.workstation = Workstation(WORKSTATION_ID)

    def tearDown(self):
        pass

    def test_turn_on(self):
        self.workstation.turn_on()
        obj_ = Orion.get(WORKSTATION_ID)
        self.assertEqual(True, obj_["available"]["value"])

    def test_turn_off(self):
        # preparations
        Orion.update_attribute(WORKSTATION_ID, "available", True)
        obj_ = Orion.get(WORKSTATION_ID)
        # did the preparations succeed?
        self.assertEqual(True, obj_["available"]["value"])
        # the real test
        self.workstation.turn_off()
        obj_ = Orion.get(WORKSTATION_ID)
        self.assertEqual(False, obj_["available"]["value"])

    def test_reset_jobHandler(self):
        self.workstation.jobHandler.good_cycle_count = 1
        self.workstation.jobHandler.reject_cycle_count = 1
        self.workstation.reset_jobHandler()
        self.assertEqual(0, self.workstation.jobHandler.good_cycle_count)
        self.assertEqual(0, self.workstation.jobHandler.reject_cycle_count)

    def test_handle_good_cycle(self):
        self.workstation.handle_good_cycle()
        job = Orion.get("urn:ngsiv2:i40Process:Job202200045")
        self.assertEqual(8, job["goodPartCounter"]["value"])

    def test_handle_reject_cycle(self):
        self.workstation.handle_reject_cycle()
        job = Orion.get("urn:ngsiv2:i40Process:Job202200045")
        self.assertEqual(8, job["rejectPartCounter"]["value"])

if __name__ == "__main__":
    unittest.main()

