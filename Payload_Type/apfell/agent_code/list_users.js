exports.list_users = function(task, command, params){
    var all_users = [];
    var gid = -1;
    if (params.length > 0) {
        var data = JSON.parse(params);
        if (data.hasOwnProperty('gid') && data['gid'] !== "" && data['gid'] > 0) {
            gid = data['gid'];
        }
    }
    ObjC.import('Collaboration');
    ObjC.import('CoreServices');
    if (gid < 0) {
        var defaultAuthority = $.CBIdentityAuthority.defaultIdentityAuthority;
        var grouptolook = 1000 //Most systems don't have groups past 700s
        for (var x = 0; x < grouptolook; x++) {
            var group = $.CBGroupIdentity.groupIdentityWithPosixGIDAuthority(x, defaultAuthority);
            validGroupcheck = group.toString()
            if (validGroupcheck == "[id CBGroupIdentity]") {
                var results = group.memberIdentities.js;

                var numResults = results.length;
                for (var i = 0; i < numResults; i++) {
                    var idObj = results[i];
                    var info = {
                        "POSIXName": idObj.posixName.js,
                        "POSIXID": idObj.posixUID,
                        "POSIXGID": group.posixGID,
                        "LocalAuthority": idObj.authority.localizedName.js,
                        "FullName": idObj.fullName.js,
                        "Emails": idObj.emailAddress.js,
                        "isHiddenAccount": idObj.isHidden,
                        "Enabled": idObj.isEnabled,
                        "Aliases": ObjC.deepUnwrap(idObj.aliases),
                        "UUID": idObj.UUIDString.js
                    };
                    all_users.push(info);
                    x++
                }

            }
        }
        return {
            "user_output": JSON.stringify(all_users, null, 2),
            "completed": true
        }
    } else {
        var defaultAuthority = $.CBIdentityAuthority.defaultIdentityAuthority;
        var group = $.CBGroupIdentity.groupIdentityWithPosixGIDAuthority(gid, defaultAuthority);
        var results = group.memberIdentities.js;
        var numResults = results.length;
        for (var i = 0; i < numResults; i++) {
            var idObj = results[i];
            var info = {
                "POSIXName": idObj.posixName.js,
                "POSIXID": idObj.posixUID,
                "POSIXGID": group.posixGID,
                "LocalAuthority": idObj.authority.localizedName.js,
                "FullName": idObj.fullName.js,
                "Emails": idObj.emailAddress.js,
                "isHiddenAccount": idObj.isHidden,
                "Enabled": idObj.isEnabled,
                "Aliases": ObjC.deepUnwrap(idObj.aliases),
                "UUID": idObj.UUIDString.js
            };
            all_users.push(info);
        }
    }
    return {
        "user_output": JSON.stringify(all_users, null, 2),
        "completed": true
    };
};
