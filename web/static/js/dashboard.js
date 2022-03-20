
elements = document.getElementsByTagName("div")
dropdown = document.getElementById("dropdown-guild-menu")

var guilds = []
var currentGuild = {}
var currentGuildData = {}

var moduleList = ["tracking"]

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
    for (m of moduleList) {
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
        menu.style.height = "200px"
        menu.style.overflowY = "auto"
    } else {
        menu.style.height = "0px"
        menu.style.overflowY = "hidden"
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

window.onresize = function(e) {
    oldResize(e)

    if (window.innerHeight < 750) {
        document.getElementById("body").style.height = "800px"
        document.getElementById("modules").style.height = "800px"
    } else {
        document.getElementById("body").style.height = "calc(100% - 270px)"
        document.getElementById("modules").style.height = "calc(100% - 270px)"
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
        data.user = profileData.id

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

async function loadHome(data) {
    

}

async function openHome(e) {
    await loadHome()

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
}

async function openSettings(e) {
    

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

    counter = logs.length
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
}

async function openLogs(e) {

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

document.getElementById("dashboard-logs-clear").onclick = async function() {
    data = await saveNoTime("DELETE", `${address}/api/dashboard/${currentGuild.id}/logs`)
    await loadLogs(data.data)
}

async function loadTracking(tracking) {
    if (!tracking) {
        tracking = await request("GET", `${address}/api/dashboard/${currentGuild.id}/tracking`)
    }

    currentGuildData.modules = tracking.modules

    await doModules(currentGuildData.modules)

    if (tracking.modules.includes("tracking")) {

        document.getElementById("modules-tracking-title").classList.remove("disabled")

        document.getElementById("modules-tracking-enable").style.backgroundColor = "var(--fail)"
        document.getElementById("modules-tracking-enable-label").innerText = "Disable"
    } else {
        document.getElementById("modules-tracking-title").classList.add("disabled")

        document.getElementById("modules-tracking-enable").style.backgroundColor = "var(--success)"
        document.getElementById("modules-tracking-enable-label").innerText = "Enable"
    }
}

async function openTracking(e) {
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

document.getElementById("modules-tracking-enable").onclick = async function() {
    if (currentGuildData.modules.includes("tracking")) {
        tracking = await saveNoTime("POST", `${address}/api/dashboard/${currentGuild.id}/tracking`, {enabled:false})
    } else {
        tracking = await saveNoTime("POST", `${address}/api/dashboard/${currentGuild.id}/tracking`, {enabled:true})
    }

    await loadTracking(tracking.data)
    
}
