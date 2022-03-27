
elements = document.getElementsByTagName("div")
dropdown = document.getElementById("dropdown-guild-menu")

var guilds = []
var currentGuild = {}
var currentGuildData = {}

var moduleList = {}

async function getModuleList() {
    r = await request("GET", `${address}/api/commands`)
    moduleList = r
}

getModuleList()

async function loadGuild(e) {
    document.getElementById("modules-hider").style.display = "block"
    id = e.target.id

    for (guild of guilds) {
        if (guild.id == id) {
            break
        }
    }

    currentGuild = guild
    
    guildElement = document.createElement("div")
    guildElement.innerHTML = ``
    guildElement.classList = "dropdown-menu-item noselect"
    guildElement.id = "dropdown-guild"
    
    guildElementImage = document.createElement("img")
    guildElementImage.src = `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`
    if (!guild.icon) {guildElementImage.src = "/static/images/icon.jpeg";guildElementImage.style.filter = "brightness(20%)"}
    guildElementImage.classList = "dropdown-menu-item-image vertical-center"
    guildElementImage.id = "dropdown-guild"
    guildElementImage.style.width = "40px"
    guildElementImage.style.height = "40px"

    guildElementText = document.createElement("span")
    guildElementText.classList = "vertical-center dropdown-menu-item-text"
    guildElementText.style.width = "calc(100% - 125px)"
    guildElementText.style.left = "50px"
    guildElementText.style.marginLeft = "15px"
    guildElementText.innerText = guild.name
    guildElementText.id = "dropdown-guild"

    guildElement.appendChild(guildElementImage)
    guildElement.appendChild(guildElementText)

    document.getElementById("dropdown-guild").innerHTML = ``
    document.getElementById("dropdown-guild").appendChild(guildElement)
    document.getElementById("dropdown-guild").innerHTML += `<i class="fas fa-chevron-down vertical-center" style="right:15px" id="dropdown-guild"></i>`

    document.getElementById("dropdown-guild").click()

    currentGuildData = await request("GET", `${address}/api/dashboard/${currentGuild.id}`)

    await doModules(currentGuildData.modules)

    if (!location.pathname.includes(guild.id)) {
        window.history.pushState(null, null, `/dashboard/${guild.id}`)
    }
    

    if (document.getElementById(location.pathname.split("/")[3])) {
        document.getElementById(location.pathname.split("/")[3]).click()
    } else {
        document.getElementById("home").click()
    }

}

async function doModules(modules) {
    currentGuildData.modules = modules
    for (m in moduleList) {
        if (m == "default") {continue}
        if (modules.includes(m)) {
            document.getElementById(`modules-${m}`).style.color = "var(--bold-color)"
        } else {
            document.getElementById(`modules-${m}`).style.color = "var(--general-color)"
        }
    }
}

async function getGuilds() {
    guilds = await request("GET", "/api/user/guilds")

    if (guilds.error) {
        return await notifications.new("Servers unavailable", "Log in request failed. Login has been disabled.")
    }

    guilds.sort(dynamicSort("name"));

    moveToTop = []

    for (guild of guilds) {
        if (guild.in) {
            moveToTop.push(guild)
        }
    }

    for (moveGuild of moveToTop) {
        removeAllInstances(guilds, moveGuild)
        guilds.unshift(moveGuild)
    }

    counter = 0
    dropdown.innerHTML = ``
    for (guild of guilds) {
        
        if (guild.in) {
            guildElement = document.createElement("div")
        } else {
            guildElement = document.createElement("a")
            guildElement.href = `/invite?guild_id=${guild.id}&to=/dashboard/${guild.id}`
        }
        
        
        guildElement.classList = "dropdown-menu-item noselect"
        guildElement.style.top = counter * 60
        guildElement.id = guild.id
        guildElement.onclick = loadGuild

        guildElementImage = document.createElement("img")
        
        guildElementImage.src = `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png?size=64`
        if (!guild.icon) {guildElementImage.src = "/static/images/icon.jpeg";guildElementImage.style.filter = "brightness(20%)"}
        
        guildElementImage.classList = "dropdown-menu-item-image"
        guildElementImage.id = guild.id

        guildElementText = document.createElement("span")
        guildElementText.classList = "vertical-center dropdown-menu-item-text"
        guildElementText.style.marginLeft = "15px"
        guildElementText.innerText = guild.name
        guildElementText.id = guild.id

        guildElement.appendChild(guildElementImage)
        guildElement.appendChild(guildElementText)

        dropdown.appendChild(guildElement)
        dropdown.style.height = "300px"
        dropdown.style.overflowY = "auto"

        counter += 1
    }

    if (location.pathname.includes("/dashboard/")) {
        document.getElementById(location.pathname.split("/")[2]).click()

        
    }

    document.getElementById("dropdown-guild-loader").style.opacity = 0

    
}

dropdownOnClick = async function(e) {
    menu = document.getElementById(e.target.id + "-menu")
    
    if (menu.style.height == "0px") {
        document.getElementById(e.target.id).style.borderRadius = "7px 7px 0 0"
        menu.style.height = "200px"
        menu.style.overflowY = "auto"
        menu.style.borderBottom = "1px solid black"
    } else {
        document.getElementById(e.target.id).style.borderRadius = "7px"
        menu.style.height = "0px"
        menu.style.overflowY = "hidden"
        menu.style.borderBottom = "0 solid black"
    }
}

async function initDropdowns() {
    for (element of elements) {
        if (element.id.includes("dropdown") && !element.id.includes("menu")) {
            element.onclick = dropdownOnClick
        }
    }
}

initDropdowns()
getGuilds()


oldResize = window.onresize

newResize = function(e) {
    oldResize(e)

    if (window.innerHeight < 750) {
        document.getElementById("body").style.height = "800px"
        document.getElementById("modules").style.height = "800px"
        document.getElementById("modules-toggle").style.height = "800px"
    } else {
        document.getElementById("body").style.height = "calc(100% - 270px)"
        document.getElementById("modules").style.height = "calc(100% - 270px)"
        document.getElementById("modules-toggle").style.height = "calc(100% - 270px)"
    }
    
    if (window.innerWidth < 1000) {

        document.getElementById("modules-toggle").style.display = "block"

        document.querySelector(".body").style.width = "calc(100% - 100px)"
        document.querySelector(".body").style.left = "55px"
        document.querySelector(".modules").style.left = "55px"

        document.getElementById("title").style.fontSize = "35px"
        document.getElementById("title").style.top = "100px"
        document.getElementById("dropdown-guild").style.top = "158px"
        document.getElementById("dropdown-guild-menu").style.top = "208px"
        document.getElementById("dropdown-guild").style.left = "50px"
        document.getElementById("dropdown-guild-menu").style.left = "50px"
        document.getElementById("dropdown-guild-loader").style.left = "320px"
        document.getElementById("dropdown-guild-loader").style.top = "168px"
    } else {
        document.getElementById("modules-toggle").style.display = "none"

        document.querySelector(".body").style.width = "calc(80% - 100px)"
        document.querySelector(".body").style.left = "calc(20% + 50px)"

        document.getElementById("title").style.top = "140px"
        document.getElementById("title").style.fontSize = "45px"
        document.getElementById("dropdown-guild").style.top = "140px"
        document.getElementById("dropdown-guild-menu").style.top = "190px"
        document.getElementById("dropdown-guild").style.left = "600px"
        document.getElementById("dropdown-guild-menu").style.left = "600px"
        document.getElementById("dropdown-guild-loader").style.left = "870px"
        document.getElementById("dropdown-guild-loader").style.top = "148px"
        document.querySelector(".modules").style.width = "20%"
    }
}

window.onresize = newResize
newResize()

document.getElementById("modules-toggle").onclick = async function(e) {

    if (document.querySelector(".body").style.left == "55px") {
        document.querySelector(".body").style.transition = "left .3s, width .3s"
        document.querySelector(".body").style.left = "calc(250px + 55px)"
        document.querySelector(".body").style.width = "calc(100% - 350px)"
        document.getElementById("modules-toggle-chevron").style.transform = "rotate(180deg)"
        document.querySelector(".modules").style.borderRadius = "0"
        document.querySelector(".modules").style.width = "250px"
    } else {
        document.querySelector(".body").style.left = "55px"
        document.querySelector(".body").style.width = "calc(100% - 100px)"
        document.getElementById("modules-toggle-chevron").style.transform = "rotate(0deg)"

        setTimeout(function() {
            document.querySelector(".modules").style.borderRadius = "15px 0 0 15px"
        }, 300)
        
    }
    
}


let timer;

var url 
var data

async function saveNoTime(method, url, data={}) {

    document.getElementById("dashboard-loader").style.opacity = 1

    data.user = profileData.id

    returned = await request(method, url, data)

    if (!returned.error) {
        nt = await notifications.new("Successfully saved", returned.message)
        nt.style.backgroundColor = "rgb(0, 255, 0, 0.2)"

        
    } else {
        nt = await notifications.new("Error on save", returned.message)
        nt.style.backgroundColor = "rgb(255, 0, 0, 0.2)"
    }

    if (returned.guild) {
        currentGuildData = returned.guild
    }
    
    document.getElementById("body-progress").style.transition = "width 0s"
    document.getElementById("body-progress").style.width = "0"

    document.getElementById("dashboard-loader").style.opacity = 0

    return returned
}

async function save(url, data, func) {
    document.getElementById("body-progress").style.transition = "width 0s"
    document.getElementById("body-progress").style.width = "0"

    setTimeout(function() {
        document.getElementById("body-progress").style.transition = "width 2s linear"
        document.getElementById("body-progress").style.width = "100%"
    }, 100)
    

    clearTimeout(timer);
    // Sets new timer that may or may not get cleared
    timer = setTimeout(async () => {

        returned = await request("POST", url, data)

        if (!returned.error) {
            nt = await notifications.new("Successfully saved", returned.message)
            nt.style.backgroundColor = "rgb(0, 255, 0, 0.2)"

            
        } else {
            nt = await notifications.new("Error on save", returned.message)
            nt.style.backgroundColor = "rgb(255, 0, 0, 0.2)"
        }

        if (func && returned.data) {
            func(returned.data)
        }
        
        document.getElementById("body-progress").style.transition = "width 0s"
        document.getElementById("body-progress").style.width = "0"
        

        return returned
    }, 2000);
}

// Functions

var homeData = null

document.getElementById("dashboard-home-modules-search").oninput = async function(e) {
    await loadHome(homeData, e.target.value)
}

async function loadHome(data, query = null) {
    if (!data) {
        data = await request("GET", `${address}/api/dashboard/${currentGuild.id}/home`)
    }
    homeData = data
    document.getElementById("dashboard-home-modules").innerHTML = ""

    for (m in moduleList) {
        if (m == "default") continue

        if (query && (!m.includes(query.toLowerCase()) )) {continue}

        tile = document.createElement("div")
        tile.classList = "body-item-tile"
        tile.id = `dashboard-tile${m}`
        tile.style.position = "relative"

        sw = document.createElement("label")
        sw.for = `dashboard-tile-${m}-switch`
        sw.classList = "toggle-switchy body-item-tile-switch"
        sw.setAttribute("data-style", "rounded")
        sw.style.right = "5px"
        sw.id = `dashboard-tile-${m}-switch`

        swInput = document.createElement("input")
        if (data.modules.includes(m)) {
            swInput.checked = true
            tile.style.filter = "brightness(100%)"
        } else{
            swInput.checked = false 
            tile.style.filter = "brightness(70%)"
        }
        swInput.type = "checkbox"
        swInput.id = `dashboard-tile-${m}-switch`

        

        swText = document.createElement("span")
        swText.classList = "toggle"
        swText.id = `dashboard-tile-${m}-switch`
        swText.innerHTML = `<span class="switch"></span>`

        sw.onclick = async function(e) {
            mo = e.target.id.replace("dashboard-tile-", "").replace("-switch", "")

            if (currentGuildData.modules.includes(mo)) {
                modulesData = await saveNoTime("POST", `${address}/api/dashboard/${currentGuild.id}/${mo}`, {enabled:false})
            } else {
                modulesData = await saveNoTime("POST", `${address}/api/dashboard/${currentGuild.id}/${mo}`, {enabled:true})
            }

            await doModules(modulesData.data.modules)
            await loadHome()
        }

        if (currentGuildData.permissions.manage_guild) {
            swInput.disabled = false 
        } else {
            swInput.disabled = true
            sw.onclick = null
        }

        sw.appendChild(swInput)
        sw.appendChild(swText)
        
        title = document.createElement("div")
        title.classList = "title"
        title.style.fontSize = "calc(var(--font-size) * 1.5)"
        title.innerText = titleCase(m)

        description = document.createElement("div")
        description.classList = "description"
        description.style.marginTop = "10px"
        description.innerText = moduleList[m].description

        options = document.createElement("a")
        options.classList = "button-primary"
        options.setAttribute("style", "position:absolute;width:120px;height:40px;bottom:15px;box-shadow:none")
        options.innerHTML = `<span class="all-center noselect title" style="font-size:15px;text-shadow:none" id="options-${m}"> <span class="vertical-center" id="options-${m}"><i class="fas fa-cog" ></i></span> <span style="margin-left:20px" id="options-${m}">Settings</span></span>`
        options.id = `options-${m}`

        tile.appendChild(sw)
        tile.appendChild(title)
        tile.appendChild(description)
        tile.appendChild(options)

        document.getElementById("dashboard-home-modules").appendChild(tile)

        document.getElementById(`options-${m}`).onclick = async function (e) {
            mod = e.target.id.replace("options-", "")

            if (mod == "tracking") {
                await openTracking(document.getElementById(`modules-${mod}`))
            }
        }

    }
    

}


async function openHome(e) {
    await loadHome()
    
    if (document.getElementById("modules-toggle").style.display != "none" && (document.querySelector(".body").style.left != "55px")) {
        document.getElementById("modules-toggle").click()
    }

    if (document.getElementById("dashboard").style.opacity != 1) {
        await closeAll(document.getElementById("dashboard"))

        e.style.backgroundColor = "rgb(255, 255, 255, 0.2)"
        document.getElementById("dashboard").style.opacity = "100%"
        document.getElementById("dashboard").style.height = "100%"
        
    } else {
        e.style.backgroundColor = ""
        document.getElementById("dashboard").style.opacity = "0%"
        document.getElementById("dashboard").style.height = "0%"
    }

    window.history.pushState(null, null, `/dashboard/${guild.id}`)

}

async function closeAll(element) {
    var bodyItems = document.getElementById("body").querySelectorAll(".body-item"); 
    var moduleItems = document.getElementById("modules").querySelectorAll(".modules-item"); 

    for (item of bodyItems) {
        item.style.opacity = 0
        item.style.height = 0
    }

    for (moduleItem of moduleItems) {
        moduleItem.style.backgroundColor = ""
    }


}

async function loadSettings(settings) {
    if (!settings) {
        settings = await request("GET", `${address}/api/dashboard/${currentGuild.id}/settings`)
    }
    
    document.getElementById("dashboard-settings-prefix").value = settings.prefix

    if (currentGuildData.permissions.manage_guild) {
        document.getElementById("dashboard-settings-prefix").className = "input"
        document.getElementById("dashboard-settings-prefix").disabled = false 
    } else {
        document.getElementById("dashboard-settings-prefix").className = "input-disabled"
        document.getElementById("dashboard-settings-prefix").disabled = true
    }
}

async function openSettings(e) {

    if (document.getElementById("modules-toggle").style.display != "none" && (document.querySelector(".body").style.left != "55px")) {
        document.getElementById("modules-toggle").click()
    }
    

    if (document.getElementById("dashboard-settings").style.opacity != 1) {
        await closeAll(document.getElementById("dashboard-settings"))
        await loadSettings()

        e.style.backgroundColor = "rgb(255, 255, 255, 0.2)"
        document.getElementById("dashboard-settings").style.opacity = "100%"
        document.getElementById("dashboard-settings").style.height = "100%"
        
    } else {
        e.style.backgroundColor = ""
        document.getElementById("dashboard-settings").style.opacity = "0%"
        document.getElementById("dashboard-settings").style.height = "0%"
    }

    window.history.pushState(null, null, `/dashboard/${guild.id}/settings`)
}

document.getElementById("dashboard-settings-prefix").oninput = async function(e) {
    await save(`${address}/api/dashboard/${currentGuild.id}/settings`, {prefix:e.target.value}, loadSettings)
}

async function loadLogs(logs) {
    if (!logs) {
        logs = await request("GET", `${address}/api/dashboard/${currentGuild.id}/logs`)
    }
    
    table = document.getElementById("dashboard-logs-table")
    table.innerHTML = `<tr"><th></th><th class="title">Time</th><th class="title">User</th><th class="title">Description</th></tr>`

    document.getElementById("dashboard-logs-clear").onclick = async function() {
        data = await saveNoTime("DELETE", `${address}/api/dashboard/${currentGuild.id}/logs`)
        await loadLogs(data.data)
    }

    counter = logs.length
    if (currentGuildData.permissions.view_audit_logs) {
        for (log of logs) {
            row = document.createElement("tr")
    
            index = document.createElement("th")
            time = document.createElement("th")
            user = document.createElement("th")
            description = document.createElement("th")
    
            index.classList = "body-item-table-field description"
            time.classList = "body-item-table-field description"
            user.classList = "body-item-table-field description"
            description.classList = "body-item-table-field description"
    
            time.innerText = timeConverter(log.timestamp)
            user.innerText = log.user_tag
            description.innerText = log.description
            index.innerText = `${counter}.`
    
            row.appendChild(index)
            row.appendChild(time)
            row.appendChild(user)
            row.appendChild(description)
    
            table.appendChild(row)
    
            counter -= 1
        }
    } else {
        row = document.createElement("tr")
        row.innerText = "You do not have permissions to view the Modulus Logs"
        table.appendChild(row)
    }
    

    if (!currentGuildData.permissions.manage_guild) {
        document.getElementById("dashboard-logs-clear").className = "noselect button-disabled"
        document.getElementById("dashboard-logs-clear").onclick = null
    } else {
        document.getElementById("dashboard-logs-clear").className = "noselect button-primary"
    }
}

async function openLogs(e) {

    if (document.getElementById("modules-toggle").style.display != "none" && (document.querySelector(".body").style.left != "55px")) {
        document.getElementById("modules-toggle").click()
    }

    if (document.getElementById("dashboard-logs").style.opacity != 1) {
        await closeAll(document.getElementById("dashboard-logs"))
        await loadLogs()

        e.style.backgroundColor = "rgb(255, 255, 255, 0.2)"
        document.getElementById("dashboard-logs").style.opacity = "100%"
        document.getElementById("dashboard-logs").style.height = "100%"
        
    } else {
        e.style.backgroundColor = ""
        document.getElementById("dashboard-logs").style.opacity = "0%"

        document.getElementById("dashboard-logs").style.height = 0

    }

    window.history.pushState(null, null, `/dashboard/${guild.id}/logs`)
}



async function loadTracking(tracking) {
    if (!tracking) {
        tracking = await request("GET", `${address}/api/dashboard/${currentGuild.id}/tracking`)
    }

    currentGuildData.modules = tracking.modules

    await doModules(currentGuildData.modules)

    document.getElementById("modules-tracking-enable").onclick = async function () {
        if (currentGuildData.modules.includes("tracking")) {
            tracking = await saveNoTime("POST", `${address}/api/dashboard/${currentGuild.id}/tracking`, {enabled:false})
        } else {
            tracking = await saveNoTime("POST", `${address}/api/dashboard/${currentGuild.id}/tracking`, {enabled:true})
        }
    
        await loadTracking(tracking.data)
        
    }

    if (tracking.modules.includes("tracking")) {
        

        document.getElementById("modules-tracking-title").classList.remove("disabled")

        document.getElementById("modules-tracking-enable").className = "button-danger noselect"
        document.getElementById("modules-tracking-enable-label").innerText = "Disable"

        document.getElementById("modules-tracking-text").classList = ""

        document.getElementById("modules-tracking-totalOnline").innerText = secondsToDhms(tracking.total_online)
        document.getElementById("modules-tracking-totalTracked").innerText = secondsToDhms(tracking.total_tracked)

        document.getElementById("modules-tracking-voice-switch").disabled = false

        if (tracking.disabled_statistics.includes("voice")) {
            document.getElementById("modules-tracking-voice-switch").checked = false
            document.getElementById("modules-tracking-voice").style.filter = "brightness(50%)"
        } else {
            document.getElementById("modules-tracking-voice-switch").checked = true
            document.getElementById("modules-tracking-voice").style.filter = "brightness(100%)"
        }
        if (tracking.disabled_statistics.includes("activity")) {
            document.getElementById("modules-tracking-activity-switch").checked = false
            document.getElementById("modules-tracking-activity").style.filter = "brightness(50%)"
        } else {
            document.getElementById("modules-tracking-activity-switch").checked = true
            document.getElementById("modules-tracking-activity").style.filter = "brightness(100%)"
        }

    } else {
        document.getElementById("modules-tracking-title").classList.add("disabled")

        document.getElementById("modules-tracking-enable").className = "button-success noselect"
        document.getElementById("modules-tracking-enable-label").innerText = "Enable"
        document.getElementById("modules-tracking-text").classList = "disabled"

        document.getElementById("modules-tracking-totalOnline").innerText = 0
        document.getElementById("modules-tracking-totalTracked").innerText = 0
    }
    if (!tracking.modules.includes("tracking") || !currentGuildData.permissions.manage_guild) {
        document.getElementById("modules-tracking-voice-switch").disabled = true
        document.getElementById("modules-tracking-voice").style.filter = "brightness(25%)"
        document.getElementById("modules-tracking-activity-switch").disabled = true
        document.getElementById("modules-tracking-activity").style.filter = "brightness(25%)"
    } 
    if (!currentGuildData.permissions.manage_guild) {
        document.getElementById("modules-tracking-enable").className = "button-success noselect button-disabled"
        document.getElementById("modules-tracking-enable").onclick = null
    }
}

async function openTracking(e) {
    if (document.getElementById("modules-toggle").style.display != "none" && (document.querySelector(".body").style.left != "55px")) {
        document.getElementById("modules-toggle").click()
    }
    
    if (document.getElementById("dashboard-modules-tracking").style.opacity != 1) {
        await closeAll(document.getElementById("dashboard-modules-tracking"))
        await loadTracking()

        e.style.backgroundColor = "rgb(255, 255, 255, 0.2)"
        document.getElementById("dashboard-modules-tracking").style.opacity = "100%"
        document.getElementById("dashboard-modules-tracking").style.height = "100%"
        
    } else {
        e.style.backgroundColor = ""
        document.getElementById("dashboard-modules-tracking").style.opacity = "0%"

        document.getElementById("dashboard-modules-tracking").style.height = 0
    }

    window.history.pushState(null, null, `/dashboard/${guild.id}/modules-tracking`)
}



async function tracking_onclick_disable(e) {
    
    voiceChecked = document.getElementById("modules-tracking-voice-switch").checked 
    activityChecked = document.getElementById("modules-tracking-activity-switch").checked 

    disabledModules = []
    if (!voiceChecked) {disabledModules.push("voice")}
    if (!activityChecked) {disabledModules.push("activity")}

    data = await saveNoTime("POST", `${address}/api/dashboard/${currentGuild.id}/tracking`, {disabledStatistics:disabledModules})
    await loadTracking(data.data)
}

document.getElementById("modules-tracking-voice-switch").onclick = tracking_onclick_disable
document.getElementById("modules-tracking-activity-switch").onclick = tracking_onclick_disable