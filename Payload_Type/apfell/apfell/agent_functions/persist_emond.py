from mythic_container.MythicCommandBase import *
import json


class PersistEmondArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="rule_name",
                type=ParameterType.String,
                description="Rule name for inside of the plist",
                parameter_group_info=[ParameterGroupInfo()]
            ),
            CommandParameter(
                name="payload_type",
                type=ParameterType.ChooseOne,
                choices=["oneliner-jxa", "custom_bash-c"],
                parameter_group_info=[ParameterGroupInfo()]
            ),
            CommandParameter(
                name="url",
                type=ParameterType.String,
                description="url of payload for oneliner-jxa for download cradle",
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )]
            ),
            CommandParameter(
                name="command",
                type=ParameterType.String,
                description="Command if type is custom_bash-c to execute via /bin/bash -c",
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )]
            ),
            CommandParameter(
                name="file_name",
                type=ParameterType.String,
                description="Name of plist in /etc/emond.d/rules/",
                parameter_group_info=[ParameterGroupInfo()]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply arguments")
        raise ValueError("Must supply named arguments or use the modal")

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class PersistEmondCommand(CommandBase):
    cmd = "persist_emond"
    needs_admin = False
    help_cmd = "persist_emond"
    description = """Create persistence with an emond plist file in /etc/emond.d/rules/ and a .DS_Store file to trigger it.
    WARNING: emond is NOT present on macOS Ventura!"""
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1547.011", "T1053", "T1546.014"]
    argument_class = PersistEmondArguments

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
