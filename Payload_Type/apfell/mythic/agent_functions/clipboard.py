from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *


class ClipboardArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "types": CommandParameter(
                name="Clipboard Types",
                type=ParameterType.Array,
                required=False,
                default_value=["public.utf8-plain-text"],
                description="Types of clipboard data to retrieve, defaults to public.utf8-plain-text",
            ),
            "data": CommandParameter(
                name="data",
                type=ParameterType.String,
                description="Data to put on the clipboard",
                required=False,
            ),
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                self.add_arg("data", self.command_line)


class ClipboardCommand(CommandBase):
    cmd = "clipboard"
    needs_admin = False
    help_cmd = "clipboard [data]"
    description = "Get all the types of contents on the clipboard, return specific types, or set the contents of the clipboard. Root has no clipboard!"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1115"]
    argument_class = ClipboardArguments
    browser_script = BrowserScript(script_name="clipboard", author="@its_a_feature_")

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        if task.args.get_arg("data") != "":
            resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                artifact="$.NSPasteboard.generalPasteboard.setStringForType",
                artifact_type="API Called",
            )
        else:
            resp = await MythicRPC().execute("create_artifact", task_id=task.id,
                artifact="$.NSPasteboard.generalPasteboard.dataForType",
                artifact_type="API Called",
            )
        return task

    async def process_response(self, response: AgentResponse):
        pass
