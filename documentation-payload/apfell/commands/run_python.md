+++
title = "run_python"
chapter = false
weight = 100
hidden = false
+++

## Summary

The command uses the ObjectiveC bridge to spawn python3 the same as when it is launched interactively and capture standard input. The supplied script is passed to the new python process, evaluated, and the output is returned. It is not interactive and does not go through a shell, so be sure scripts do not prompt for inputs. The command calls /usr/bin/python3, so it will not support another version of installed python and packages if it does not exist at that path.
     
- Needs Admin: False  
- Version: 1  
- Author: @robot  

### Arguments

#### script

- Description: Python script to be run   
- Required Value: True  
- Default Value: None  

## Usage

```
run_python
```

## MITRE ATT&CK Mapping

- T1059  
## Detailed Summary
```JavaScript
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
```
