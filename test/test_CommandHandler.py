import copy
import os
import sys
import unittest
from modules import reupload_jsons_to_Orion

sys.path.insert(0, os.path.join("..", "app"))
from Storage import Storage
from Workstation import Workstation
from CommandHandler import CommandHandler
import Orion
import main

TL_STORAGE_ID = "urn:ngsi_ld:Storage:TrayLoaderStorage1"
TUL_STORAGE_ID = "urn:ngsi_ld:Storage:TrayUnloaderStorage1"

class TestCommandHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.objects = main.init_objects()
        cls.commands = main.read_all_commands()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        reupload_jsons_to_Orion.main()
        self.trayLoaderStorage = Storage(TL_STORAGE_ID, capacity=2, step_size=-1, type="emptying")
        self.trayUnloaderStorage = Storage(TUL_STORAGE_ID, capacity=2, step_size=1, type="filling")
        self.workstation = Workstation("urn:ngsi_ld:Workstation:InjectionMoulding1")
        cp_commands = copy.deepcopy(self.commands)
        cp_objects = copy.deepcopy(self.objects)
        self.commandHandler = CommandHandler(cp_commands, cp_objects)

    def tearDown(self):
        pass

    def test_handle_workstation(self):
        # turn on
        self.commandHandler.handle_command("3")
        obj_ = Orion.get("urn:ngsi_ld:Workstation:InjectionMoulding1")
        self.assertEqual(True, obj_["Available"]["value"])

        # turn off
        self.commandHandler.handle_command("2")
        obj_ = Orion.get("urn:ngsi_ld:Workstation:InjectionMoulding1")
        self.assertEqual(False, obj_["Available"]["value"])

        # good cycle
        self.commandHandler.handle_command("10")
        job = Orion.get("urn:ngsi_ld:Job:202200045")
        self.assertEqual(8, job["GoodPartCounter"]["value"])

        # reject cycle
        self.commandHandler.handle_command("11")
        job = Orion.get("urn:ngsi_ld:Job:202200045")
        self.assertEqual(8, job["RejectPartCounter"]["value"])

        # reset
        self.commandHandler.handle_command("8")
        self.assertEqual(0, self.commandHandler.objects["urn:ngsi_ld:Workstation:InjectionMoulding1"]["py"].jobHandler.good_cycle_count)
        self.assertEqual(0, self.commandHandler.objects["urn:ngsi_ld:Workstation:InjectionMoulding1"]["py"].jobHandler.reject_cycle_count)

    def test_handle_storage(self):
        # TrayLoaderStorage1
        self.assertEqual(2, self.commandHandler.objects[TL_STORAGE_ID]["py"].counter)

        # step 
        self.commandHandler.handle_command("19")
        self.assertEqual(1, self.commandHandler.objects[TL_STORAGE_ID]["py"].counter)
        tl_storage_obj = Orion.get(TL_STORAGE_ID)
        self.assertEqual(1, tl_storage_obj["Counter"]["value"])

        # reset
        self.commandHandler.handle_command("20")
        self.assertEqual(2, self.commandHandler.objects[TL_STORAGE_ID]["py"].counter)
        tl_storage_obj = Orion.get(TL_STORAGE_ID)
        self.assertEqual(2, tl_storage_obj["Counter"]["value"])

        # TrayUnloaderStorage1
        self.assertEqual(0, self.commandHandler.objects[TUL_STORAGE_ID]["py"].counter)

        # step 
        self.commandHandler.handle_command("21")
        self.assertEqual(1, self.commandHandler.objects[TUL_STORAGE_ID]["py"].counter)
        tul_storage_obj = Orion.get(TUL_STORAGE_ID)
        self.assertEqual(1, tul_storage_obj["Counter"]["value"])

        # reset
        self.commandHandler.handle_command("22")
        self.assertEqual(0, self.commandHandler.objects[TUL_STORAGE_ID]["py"].counter)
        tul_storage_obj = Orion.get(TUL_STORAGE_ID)
        self.assertEqual(0, tul_storage_obj["Counter"]["value"])

    def test_special(self):
        # a Counter higher than the Capacity could never occur under normal conditions, 
        # but we can set the value so with a special request anyways
        # without argument, data is set in special command
        self.commandHandler.handle_command("33")
        tl_storage_obj = Orion.get(TL_STORAGE_ID)
        self.assertEqual(3, tl_storage_obj["Counter"]["value"])

        # with argument, argument is passed to the CommandHandler
        self.commandHandler.handle_command("34", "4")
        tl_storage_obj = Orion.get(TL_STORAGE_ID)
        self.assertEqual(4, tl_storage_obj["Counter"]["value"])


if __name__ == "__main__":
    unittest.main()

