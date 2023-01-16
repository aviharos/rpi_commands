import os
import sys
import unittest
from unittest.mock import patch
from modules import reupload_jsons_to_Orion

import requests

sys.path.insert(0, os.path.join("..", "src"))
from JobHandler import JobHandler
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

    def tearDown(self):
        pass

    def test_add_already_finished_cycle_counters_if_necessary_and_possible(self):
        Orion.update_attribute("urn:ngsiv2:i40Process:Job202200045", "goodPartCounter", "Number", 16)
        Orion.update_attribute("urn:ngsiv2:i40Process:Job202200045", "rejectPartCounter", "Number", 24)
        jobHandler = JobHandler("urn:ngsiv2:i40Asset:InjectionMouldingMachine1")
        self.assertEqual(jobHandler.good_cycle_counter, 2)
        self.assertEqual(jobHandler.reject_cycle_counter, 3)

        jobHandler.are_counters_initiated_from_Orion = False
        Orion.update_attribute("urn:ngsiv2:i40Process:Job202200045", "rejectPartCounter", "Number", 23)
        jobHandler.update_cycle_counters()
        self.assertFalse(jobHandler.are_counters_initiated_from_Orion)

    def test_handle_good_cycle(self):
        with patch("Orion.is_reachable") as mock_is_reachable:
            mock_is_reachable.return_value = False
            jobHandler = JobHandler("urn:ngsiv2:i40Asset:InjectionMouldingMachine1")
        Orion.update_attribute("urn:ngsiv2:i40Process:Job202200045", "goodPartCounter", "Number", 16)
        # let's see if the counters are updated when the Orion is reachable
        jobHandler.handle_good_cycle()
        job = Orion.get("urn:ngsiv2:i40Process:Job202200045")
        self.assertEqual(job["goodPartCounter"]["value"], 24)

    def test_handle_reject_cycle(self):
        with patch("Orion.is_reachable") as mock_is_reachable:
            mock_is_reachable.return_value = False
            jobHandler = JobHandler("urn:ngsiv2:i40Asset:InjectionMouldingMachine1")
        Orion.update_attribute("urn:ngsiv2:i40Process:Job202200045", "rejectPartCounter", "Number", 40)
        # let's see if the counters are updated when the Orion is reachable
        jobHandler.handle_reject_cycle()
        job = Orion.get("urn:ngsiv2:i40Process:Job202200045")
        self.assertEqual(job["rejectPartCounter"]["value"], 48)

if __name__ == "__main__":
    unittest.main()

