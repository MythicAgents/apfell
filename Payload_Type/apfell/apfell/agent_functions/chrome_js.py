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

    async def opsec_pre(self, taskData: PTTaskMessageAllData) -> PTTTaskOPSECPreTaskMessageResponse:
        tasks = await SendMythicRPCTaskSearch(MythicRPCTaskSearchMessage(
            TaskID=taskData.Task.ID,
            SearchHost=taskData.Callback.Host,
            SearchCommandNames=[self.cmd]
        ))
        response = PTTTaskOPSECPreTaskMessageResponse(
            TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=False,
            OpsecPreBypassRole="operator",
            OpsecPreMessage="This could cause a popup between your current context and Google Chrome!",
        )
        found = False
        if tasks.Success:
            logger.info(tasks.Tasks)
            for t in tasks.Tasks:
                logger.info(t.to_json())
                if t.Completed:
                    found = True
                    response = PTTTaskOPSECPreTaskMessageResponse(
                        TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=False,
                        OpsecPreBypassRole="operator",
                        Error="Another instance already caused a popup, letting this one go",
                        OpsecPreMessage="This will cause a popup between your current context and Google Chrome!",
                    )
                    break
        else:
            found = True
            response = PTTTaskOPSECPreTaskMessageResponse(
                TaskID=taskData.Task.ID, Success=False, OpsecPreBlocked=True,
                OpsecPreBypassRole="operator",
                Error="Failed to search for tasks on this host",
                OpsecPreMessage="This will cause a popup between your current context and Google Chrome!",
            )
        if not found:
            response = PTTTaskOPSECPreTaskMessageResponse(
                TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=True,
                OpsecPreBypassRole="operator",
                OpsecPreMessage="This will cause a popup between your current context and Google Chrome!",
            )
        return response

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"Target Application of Chrome",
            BaseArtifactType="AppleEvent"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
