import os
import sys
import unittest


from modules import reupload_jsons_to_Orion

sys.path.insert(0, os.path.join("..", "src"))
from Storage import Storage
from Workstation import Workstation
from CommandHandler import CommandHandler
import Orion
from Logger import getLogger

logger = getLogger(__name__)

TL_STORAGE_ID = "urn:ngsiv2:i40Asset:TrayLoaderStorage1"
TUL_STORAGE_ID = "urn:ngsiv2:i40Asset:TrayUnloaderStorage1"

class TestCommandHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        reupload_jsons_to_Orion.main()
        self.trayLoaderStorage = Storage(TL_STORAGE_ID, capacity=2, step_size=-1, type="emptying")
        self.trayUnloaderStorage = Storage(TUL_STORAGE_ID, capacity=0, step_size=1, type="filling")
        self.workstation = Workstation("urn:ngsiv2:i40Asset:InjectionMouldingMachine1")
        self.commandHandler = CommandHandler()

    def tearDown(self):
        pass

    def test_handle_workstation(self):
        # turn on
        self.commandHandler.handle_command("InjectionMouldingMachine1_on")
        obj_ = Orion.get("urn:ngsiv2:i40Asset:InjectionMouldingMachine1")
        self.assertEqual(True, obj_["available"]["value"])

        # turn off
        self.commandHandler.handle_command("InjectionMouldingMachine1_off")
        obj_ = Orion.get("urn:ngsiv2:i40Asset:InjectionMouldingMachine1")
        self.assertEqual(False, obj_["available"]["value"])

        # good cycle
        self.commandHandler.handle_command("InjectionMouldingMachine1_good_parts_completed")
        job = Orion.get("urn:ngsiv2:i40Process:Job202200045")
        logger.debug(f"""handle_workstation: InjectionMouldingMachine1_good_parts_completed:
downloaded job: 
{job}""")
        self.assertEqual(8, job["goodPartCounter"]["value"])

        # reject cycle
        self.commandHandler.handle_command("InjectionMouldingMachine1_reject_parts_completed")
        job = Orion.get("urn:ngsiv2:i40Process:Job202200045")
        self.assertEqual(8, job["rejectPartCounter"]["value"])

        # reset
        Orion.update_attribute("urn:ngsiv2:i40Asset:InjectionMouldingMachine1", "refJob", "Relationship", "urn:ngsiv2:i40Process:Job202200046")
        self.commandHandler.handle_command("InjectionMouldingMachine1_new_job")
        self.assertEqual(0, self.commandHandler.objects["urn:ngsiv2:i40Asset:InjectionMouldingMachine1"]["py"].jobHandler.good_cycle_counter)
        self.assertEqual(0, self.commandHandler.objects["urn:ngsiv2:i40Asset:InjectionMouldingMachine1"]["py"].jobHandler.reject_cycle_counter)

    def test_handle_storage(self):
        # TrayLoaderStorage1
        self.assertEqual(2, self.commandHandler.objects[TL_STORAGE_ID]["py"].counter)

        # step 
        self.commandHandler.handle_command("TrayLoaderStorage1_step")
        self.assertEqual(1, self.commandHandler.objects[TL_STORAGE_ID]["py"].counter)
        tl_storage_obj = Orion.get(TL_STORAGE_ID)
        self.assertEqual(1, tl_storage_obj["counter"]["value"])

        # reset
        self.commandHandler.handle_command("TrayLoaderStorage1_set_empty")
        self.assertEqual(0, self.commandHandler.objects[TL_STORAGE_ID]["py"].counter)
        tl_storage_obj = Orion.get(TL_STORAGE_ID)
        self.assertEqual(0, tl_storage_obj["counter"]["value"])

        # TrayUnloaderStorage1
        self.assertEqual(0, self.commandHandler.objects[TUL_STORAGE_ID]["py"].counter)

        # step 
        self.commandHandler.handle_command("TrayUnloaderStorage1_step")
        self.assertEqual(1, self.commandHandler.objects[TUL_STORAGE_ID]["py"].counter)
        tul_storage_obj = Orion.get(TUL_STORAGE_ID)
        self.assertEqual(1, tul_storage_obj["counter"]["value"])

        # reset
        self.commandHandler.handle_command("TrayUnloaderStorage1_set_full")
        self.assertEqual(2, self.commandHandler.objects[TUL_STORAGE_ID]["py"].counter)
        tul_storage_obj = Orion.get(TUL_STORAGE_ID)
        self.assertEqual(2, tul_storage_obj["counter"]["value"])

    def test_special(self):
        # a counter higher than the Capacity could never occur under normal conditions, 
        # but we can set the value so with a special request anyways
        # without argument, data is set in special command
        self.commandHandler.handle_command("Test_TrayLoaderStorage1_set_to_1")
        tl_storage_obj = Orion.get(TL_STORAGE_ID)
        logger.debug(f"test_special: TrayLoaderStorage1:\n{tl_storage_obj}")
        self.assertEqual(1, tl_storage_obj["counter"]["value"])

        # with argument, argument is passed to the CommandHandler
        self.commandHandler.handle_command("Test_TrayLoaderStorage1_set_to_x", 3)
        tl_storage_obj = Orion.get(TL_STORAGE_ID)
        logger.debug(f"test_special: TrayLoaderStorage1:\n{tl_storage_obj}")
        self.assertEqual(3, tl_storage_obj["counter"]["value"])


if __name__ == "__main__":
    unittest.main()

