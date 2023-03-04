from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class ChromeJsArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="window",
                type=ParameterType.Number,
                description="Window # from chrome_tabs",
                default_value=0,
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )]
            ),
            CommandParameter(
                name="javascript",
                type=ParameterType.String,
                description="javascript to execute",
                parameter_group_info=[ParameterGroupInfo()]
            ),
            CommandParameter(
                name="tab",
                type=ParameterType.Number,
                description="Tab # from chrome_tabs",
                default_value=0,
                parameter_group_info=[ParameterGroupInfo(
                    required=False
                )]
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Need to specify command to run")
        self.add_arg("javascript", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        if "javascript" in dictionary_arguments:
            self.add_arg("javascript", dictionary_arguments["javascript"])
        else:
            raise ValueError("Missing 'javascript' argument")
        if "window" in dictionary_arguments:
            self.add_arg("window", dictionary_arguments["window"])
        else:
            self.add_arg("window", 0)
        if "tab" in dictionary_arguments:
            self.add_arg("tab", dictionary_arguments["tab"])
        else:
            self.add_arg("tab", 0)


class ChromeJsCommand(CommandBase):
    cmd = "chrome_js"
    needs_admin = False
    help_cmd = "chrome_js"
    description = "This uses AppleEvents to execute the specified JavaScript code into a specific browser tab. The chrome_tabs function will specify for each tab the window/tab numbers that you can use for this function. Note: by default this ability is disabled in Chrome now, you will need to go to view->Developer->Allow JavaScript from Apple Events."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1059.002", "T1559"]
    argument_class = ChromeJsArguments

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        resp = await MythicRPC().execute("create_artifact", task_id=task.id,
            artifact="Target Application of Chrome",
            artifact_type="AppleEvent Sent",
        )
        return task

    async def process_response(self, response: AgentResponse):
        pass
