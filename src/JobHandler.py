"""JobHandler
"""

# Standard Library imports

# PyPI imports

# Custom imports
from OrionObject import OrionObject
from Logger import getLogger
import Orion


class JobHandler(OrionObject):
    """JobHandler

    It is an extraodinary object because it is possible that 
    we do not know which Job the JobHandler refers to. 

    Upon initiating, the JobHandler tries to query the Job and Operation 
    objects to calculate the number of cycles producing good and reject parts
    respectively. If it suceeds, the counters continue from these values. 
    If it does not succeed, the counters start from 0.

    The Raspberry Pi knows when a new job is started and how many
    cycles have been completed so far in the current job.
    Whenever good or reject parts are completed (a batch is considered uniform in this regard),
    the Raspberry Pi sends data to the IoT agent of MOMAMS
    informing it that a batch of good or reject parts is completed.

    The JobHandler is not present directly in the CommandHandler's
    objects dict. It always exists as an attribute of one of the Workstation 
    objects. Whenever

    Attributes:
        workstation_id (str): Orion id of the Job's workstation
        good_cycle_count (int): the number of good cycles so far
        reject_cycle_count (int): the number of reject cycles so far

    Usage:
        __init__:
            jobHandler = JobHandler(id)

        handle_good_cycle(type, counter):
            handles the event of good parts completed
            in a Workstation cycle 
            also sends the data to the IoT agent

        handle_reject_cycle(type, counter):
            handles the event of reject parts completed
            in a Workstation cycle 
            also sends the data to the IoT agent
    """

    def __init__(self, workstation_id: str):
        self.workstation_id = workstation_id
        self.logger = getLogger(__name__)
        self.good_cycle_counter = 0
        self.reject_cycle_counter = 0
        self.are_counters_initiated_from_Orion = False
        if Orion.is_reachable():
            self.logger.debug("Orion is reachable")
            self.update_cycle_counters()

    def update_cycle_counters(self):
        """Update good and reject part counters

        This update procedure is tried at initiation and also
        before handling any type of cycle. 

        The point is that the Job's goodPartCounter and rejectPartCounter
        may already contain a lot of parts, and we would like to continue from
        where it was left befores. 

        Since we do not know which cycle the procedure will succeed,
        the method is called update. When the update suceeds, it is never
        executed again as long as rpi_commands runs. The function calculates
        how many cycles had already been finished before starting rpi_commands
        and adds these cycle counts to the current cycle counts. 
        This way, if the connection is restored after X good cycles and there
        were already Y good cycles before, the counter will be X+Y. The same
        applies for the reject part counter.
        """
        try:
            workstation = Orion.get(self.workstation_id)
            self.logger.debug(f"update_cycle_counters: workstation: {workstation}")
            job = Orion.get(workstation["refJob"]["value"])
            self.logger.debug(f"update_cycle_counters: job: {job}")
            good_part_counter = job["goodPartCounter"]["value"]
            self.logger.debug(f"update_cycle_counters: good_part_counter: {good_part_counter}")
            reject_part_counter = job["rejectPartCounter"]["value"]
            self.logger.debug(f"update_cycle_counters: reject_part_counter: {reject_part_counter}")
            operation = Orion.get(job["refOperation"]["value"])
            self.logger.debug(f"update_cycle_counters: operation: {operation}")
            parts_per_cycle = operation["partsPerCycle"]["value"]
            self.logger.debug(f"update_cycle_counters: parts_per_cycle: {parts_per_cycle}")
            if good_part_counter % parts_per_cycle != 0:
                raise ValueError(f"The goodPartCounter is not divisible by partsPerCycle for {job['id']}. {good_part_counter} % {parts_per_cycle} != 0")
            if reject_part_counter % parts_per_cycle != 0:
                raise ValueError(f"The rejectPartCounter is not divisible by partsPerCycle for {job['id']}. {reject_part_counter} % {parts_per_cycle} != 0")
            good_cycles_already_finished_in_Orion = good_part_counter / parts_per_cycle
            self.logger.debug(f"update_cycle_counters: good_cycles_already_finished_in_Orion: {good_cycles_already_finished_in_Orion}")
            self.good_cycle_counter += good_cycles_already_finished_in_Orion
            reject_cycles_already_finished_in_Orion = reject_part_counter / parts_per_cycle
            self.logger.debug(f"update_cycle_counters: reject_cycles_already_finished_in_Orion: {reject_cycles_already_finished_in_Orion}")
            self.reject_cycle_counter += reject_cycles_already_finished_in_Orion
            self.id = job["id"]
            self.parts_per_cycle = parts_per_cycle 
            self.are_counters_initiated_from_Orion = True
        except Exception as error:
            self.logger.error(f"Error: initiating counters failed: {error}")

    def update_part_counter(self, counter_name: str, cycle_counter_value: int):
        try:
            self.update_attribute(counter_name, "Number", cycle_counter_value * self.parts_per_cycle)
        except RuntimeError as error:
            raise RuntimeError(f"Error: could not update counters: {error}") from error

    def add_already_finished_cycle_counters_if_necessary_and_possible(self):
        if (not self.are_counters_initiated_from_Orion 
            and Orion.is_reachable()):
            self.update_cycle_counters()

    def handle_good_cycle(self):
        self.logger.info("Good cycle completed")
        self.add_already_finished_cycle_counters_if_necessary_and_possible()
        self.good_cycle_counter += 1
        self.update_part_counter(counter_name="goodPartCounter",
                                 cycle_counter_value=self.good_cycle_counter)

    def handle_reject_cycle(self):
        self.logger.info("Reject cycle completed")
        self.add_already_finished_cycle_counters_if_necessary_and_possible()
        self.reject_cycle_counter += 1
        self.update_part_counter(counter_name="rejectPartCounter",
                                 cycle_counter_value=self.reject_cycle_counter)


