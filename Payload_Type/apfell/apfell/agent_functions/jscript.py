from mythic_container.MythicCommandBase import *
import json


class JscriptArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="command",
                type=ParameterType.String,
                description="The JXA command to execute",
                parameter_group_info=[ParameterGroupInfo()]
            )
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a path to a file")
        self.add_arg("command", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        if "command" in dictionary_arguments:
            self.add_arg("command", dictionary_arguments["command"])
        else:
            raise ValueError("Missing 'command' argument")


class JscriptCommand(CommandBase):
    cmd = "jscript"
    needs_admin = False
    help_cmd = "jscript {command}"
    description = "This runs the JavaScript command, {command}, and returns its output via an eval(). The output will get passed through ObjC.deepUnwrap to parse out basic data types from ObjectiveC and get strings back"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1059.002"]
    argument_class = JscriptArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        return task

    async def process_response(self, response: AgentResponse):
        pass
