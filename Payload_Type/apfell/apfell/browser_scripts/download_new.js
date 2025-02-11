function(task, responses){
    console.log(task)
    if(task.status.includes("error")){
        const combined = responses.reduce( (prev, cur) => {
            return prev + cur;
        }, "");
        return {'plaintext': combined};
    }else if(task.completed){
        try{
            let data = JSON.parse(responses[0]);
            let filename_pieces = task.display_params.split("/");
            return {"media":[{
                "agent_file_id": data["agent_file_id"],
                    "filename": `${filename_pieces[filename_pieces.length -1]}`
            }]};
        }catch(error){
            const combined = responses.reduce( (prev, cur) => {
                return prev + cur;
            }, "");
            return {'plaintext': combined};
        }

    }else if(task.status === "processed"){
        if(responses.length > 0){
            const task_data = JSON.parse(responses[0]);
            return {"plaintext": "Downloading file with " + task_data["total_chunks"] + " total chunks..."};
        }
        return {"plaintext": "No data yet..."}
    }else{
        // this means we shouldn't have any output
        return {"plaintext": "No response yet from agent..."}
    }
}