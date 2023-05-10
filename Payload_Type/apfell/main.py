import mythic_container
import asyncio
import apfell

mythic_container.mythic_service.start_and_run_forever()

#asyncio.run(mythic_container.mythic_service.test_command(payload_type_name="apfell",
#                                                         command_name="ls",
#                                                         parameters_dictionary={"path": "/etc"},
#                                                         tasking_location="parsed_cli",
#                                                         operation_name="Operation Chimera",
#                                                         task_id=1))