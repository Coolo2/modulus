
elements = document.getElementsByTagName("div")
dropdown = document.getElementById("dropdown-guild-menu")

var guilds = []
var currentGuild = {}

async function loadGuild(e) {
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

    window.history.pushState(null, null, `/dashboard/${guild.id}`)

}

async function getGuilds() {
    guilds = await get("/api/user/guilds")

    if (guilds == undefined) {
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
        document.getElementById(location.pathname.split("/").join("").replace("dashboard", "")).click()
    }

    
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


// Functions

async function loadSettings(e) {

    if (document.getElementById("dashboard-settings").style.opacity != 1) {
        settings = await get(`${address}/api/dashboard/${currentGuild.id}/settings`)
    
        e.style.backgroundColor = "rgb(255, 255, 255, 0.2)"
        document.getElementById("dashboard-settings").style.opacity = "100%"
        document.getElementById("dashboard-settings-prefix").value = settings.prefix
    } else {
        e.style.backgroundColor = ""
        document.getElementById("dashboard-settings").style.opacity = "0%"
    }
    
    
}
