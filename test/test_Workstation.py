import os
import sys
import unittest
from modules import reupload_jsons_to_Orion

sys.path.insert(0, os.path.join("..", "app"))
from Workstation import Workstation
import Orion

class TestWorkstation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        reupload_jsons_to_Orion.main()
        self.workstation = Workstation("urn:ngsi_ld:Workstation:InjectionMoulding1")

    def tearDown(self):
        pass

    def test_turn_on(self):
        self.workstation.turn_on()
        obj_ = Orion.get("urn:ngsi_ld:Workstation:InjectionMoulding1")
        self.assertEqual(True, obj_["Available"]["value"])

    def test_turn_off(self):
        # preparations
        Orion.update_attribute("urn:ngsi_ld:Workstation:InjectionMoulding1", "Available", True)
        obj_ = Orion.get("urn:ngsi_ld:Workstation:InjectionMoulding1")
        # did the preparations succeed?
        self.assertEqual(True, obj_["Available"]["value"])
        # the real test
        self.workstation.turn_off()
        obj_ = Orion.get("urn:ngsi_ld:Workstation:InjectionMoulding1")
        self.assertEqual(False, obj_["Available"]["value"])

    def test_reset_jobHandler(self):
        self.workstation.jobHandler.good_cycle_count = 1
        self.workstation.jobHandler.reject_cycle_count = 1
        self.workstation.reset_jobHandler()
        self.assertEqual(0, self.workstation.jobHandler.good_cycle_count)
        self.assertEqual(0, self.workstation.jobHandler.reject_cycle_count)

    def test_handle_good_cycle(self):
        self.workstation.handle_good_cycle()
        job = Orion.get("urn:ngsi_ld:Job:202200045")
        self.assertEqual(8, job["GoodPartCounter"]["value"])

    def test_handle_reject_cycle(self):
        self.workstation.handle_reject_cycle()
        job = Orion.get("urn:ngsi_ld:Job:202200045")
        self.assertEqual(8, job["RejectPartCounter"]["value"])

if __name__ == "__main__":
    unittest.main()

