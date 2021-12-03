function(task, responses){
    if(task.status.includes("error")){
        const combined = responses.reduce( (prev, cur) => {
            return prev + cur;
        }, "");
        return {'plaintext': combined};
    }else if(task.completed){
        if(responses.length > 0){
            try{
                    let data = JSON.parse(responses[0]);
                    let output_table = [];
                    for(let i = 0; i < data.length; i++){
                        output_table.push({
                            "name":{"plaintext": data[i]["name"]},
                            "pid": {"plaintext": data[i]["process_id"]},
                            "bundle": {"plaintext": data[i]["bundle"]},
                            "arch": {"plaintext": data[i]["architecture"]},
                            "rowStyle": {"backgroundColor": data[i]["frontmost"] ? "mediumpurple": ""},
                            "actions": {"button": {
                                "name": "Actions",
                                "type": "menu",
                                "value": [
                                    {
                                        "name": "View Paths",
                                        "type": "dictionary",
                                        "value": {
                                            "bundleURL": data[i]["bundleURL"],
                                            "bin_path": data[i]["bin_path"],
                                        },
                                        "leftColumnTitle": "Key",
                                        "rightColumnTitle": "Value",
                                        "title": "Viewing Paths"
                                    },
                                    {
                                      "name": "entitlements",
                                      "type": "task",
                                      "ui_feature": "list_entitlements:list",
                                      "parameters": data[i]["process_id"].toString()
                                    }
                                ]
                            }},
                        })
                    }
                    return {
                        "table": [
                            {
                                "headers": [
                                    {"plaintext": "pid", "type": "number", "width": 9},
                                    {"plaintext": "name", "type": "string"},
                                    {"plaintext": "bundle", "type": "string"},
                                    {"plaintext": "arch", "type": "string", "width": 7},
                                    {"plaintext": "actions", "type": "button", "width": 8},
                                ],
                                "rows": output_table,
                                "title": "Process Data"
                            }
                        ]
                    }
            }catch(error){
                    console.log(error);
                    const combined = responses.reduce( (prev, cur) => {
                        return prev + cur;
                    }, "");
                    return {'plaintext': combined};
            }
        }else{
            return {"plaintext": "No output from command"};
        }
    }else{
        return {"plaintext": "No data to display..."};
    }
}