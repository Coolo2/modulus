
address = document.getElementsByTagName("address")[0].innerHTML

notifications = {
    notifications:[],
    close : async function (notification) {
        document.body.style.overflowX = "hidden"
        notification.style.right = "-400px"
            
        setTimeout(function() {
            notification.remove()
            document.body.style.overflowX = "auto"
        }, 500)
    },
    new : async function (title, message, onclick = null) {
        for (notification of this.notifications) {
            await notifications.close(notification)
        }

        document.body.style.overflowX = "hidden"

        notification = document.createElement("div")
        notification.classList = "notification noselect"

        notificationTitle = document.createElement("div")
        notificationTitle.classList = "title"
        notificationTitle.style.fontFamily = "Poppins"
        notificationTitle.style.fontWeight = "700"
        notificationTitle.innerText = title 

        notificationMessage = document.createElement("div")
        notificationMessage.innerText = message 

        notificationClose = document.createElement("i")
        notificationClose.classList = "fa fa-times notification-close"
        notificationClose.onclick = async function() {
            await notifications.close(notification)
        }

        
        notification.appendChild(notificationTitle)
        notification.appendChild(notificationMessage)
        notification.appendChild(notificationClose)
        
        if (onclick) {
            notification.onmouseover = function() {notification.style.textDecoration = "underline"}
            notification.onmouseout = function() {notification.style.textDecoration = "none"}
            notification.onclick = onclick
            notification.style.cursor = "pointer"
        } else {
            notification.onclick = notificationClose.onclick
        }
        

        document.body.appendChild(notification)

        notifications.notifications.push(notification)

        notification.style.right = "15px"

        setTimeout(notificationClose.onclick, (message.length + title.length) * 150)

        return notification
    }
}

async function get(url) {

    const settings = {
        method: 'GET'
    };

    try {
        const fetchResponse = await fetch(url, settings);
        const data = await fetchResponse.json();
        return data; 
    } catch {
        return undefined
    }
    
    
}

async function request(method, url, data) {

    var settings = {
        method: method,
        headers: {
            "Content-Type":"application/json"
        }
    };

    if (data) {
        settings.body = JSON.stringify(data)
    }

    response = await fetch(url, settings)
    
    return await response.json()
}

function isHidden(e) {
    return !( e.offsetWidth || e.offsetHeight || e.getClientRects().length );
}

profileName = document.getElementById("profile-name")
profileAvatar = document.getElementById("profile-avatar")
profile = document.getElementById("profile")
profileMenu = document.getElementById("profile-menu")
profileDropdown = document.getElementById("profile-dropdown")

navbarMenu = document.getElementById("navBar-menu")
navbarMenuButton = document.getElementById("navBar-menu-button")

navbarMenuButton.onclick = async function() {
    if (navbarMenu.style.height != "200px") {
        navbarMenu.style.opacity = "1000%"
        navbarMenu.style.height = "200px"
    } else {
        navbarMenu.style.height = "0px"
        setTimeout(function() {
            navbarMenu.style.opacity = 0
        }, 100)
    }
}

var profileData

async function doProfile() {
    if (profileName) {
        profileData = await get("/api/user")

        if (!profileData || profileData.error) {
            button = document.createElement("a")
            button.href = `/login?to=${location.pathname}`
            button.classList = `button-primary`
            button.style.padding = "15px 30px"
            button.innerText = `Log in`

            if (!profileData) {
                await notifications.new("Log in disabled", "Log in request failed. Login has been disabled.")
                button.removeAttribute("href")
                button.classList = `button-disabled`
            }

            profile.innerHTML = ``
            profile.appendChild(button)

            profile.style.opacity = 1
            return
        }
    
        profileName.innerText = `${profileData.username}#${profileData.discriminator}`
    
        avatar = `https://cdn.discordapp.com/avatars/${profileData.id}/${profileData.avatar}.webp?size=128`
    
        profileAvatar.src = avatar

        profile.style.opacity = 1

        profile.onclick = function() {
            if (profileMenu.style.height != "200px") {
                profileDropdown.style.transform = "rotate(180deg)"
                profileMenu.style.height = "200px"
                profileMenu.style.opacity = 1
            } else {
                profileDropdown.style.transform = "rotate(0deg)"
                profileMenu.style.height = "0px"
                setTimeout(function() {
                    profileMenu.style.opacity = 0
                }, 100)
                
            }
            
        }
    }    
}
doProfile()




async function resizeHandler() {
    elements = document.getElementsByTagName("a")
    var r = document.querySelector(":root")
    
    if (window.innerWidth / window.innerHeight < 0.6) {
        r.style.setProperty('--font-size', '20px');
    } else {
        r.style.setProperty('--font-size', '15px');
    }

    if (window.innerWidth < 1000) { 
        navbarMenuButton.style.display = "block"

        for (element of elements) {
            if (element.classList.contains("navBar-item") && !element.id) {
                element.style.display = "none"
            }
        }
    } else {
        navbarMenuButton.style.display = "none"

        for (element of elements) {
            if (element.classList.contains("navBar-item") && !element.id) {
                element.style.display = "block"
            }
        }
    }

    if (window.innerWidth < 750) { 
        document.getElementById("name").style.display = "none"
        document.getElementById("navBar-menu-button").style.left = "calc(15%)"
        document.getElementById("navBar-menu").style.left = "calc(15%)"
    } else {
        document.getElementById("name").style.display = "block"
        document.getElementById("navBar-menu-button").style.left = "calc(15% + 250px)"
        document.getElementById("navBar-menu").style.left = "calc(15% + 250px)"
    }
}
resizeHandler()
window.onresize = resizeHandler

function dynamicSort(property) {
    var sortOrder = 1;
    if(property[0] === "-") {
        sortOrder = -1;
        property = property.substr(1);
    }
    return function (a,b) {
        /* next line works with strings and numbers, 
         * and you may want to customize it to your needs
         */
        var result = (a[property] < b[property]) ? -1 : (a[property] > b[property]) ? 1 : 0;
        return result * sortOrder;
    }
}

function removeAllInstances(arr, item) {
    for (var i = arr.length; i--;) {
        if (arr[i] === item) arr.splice(i, 1);
    }
    
}

function timeConverter(UNIX_timestamp){
    var a = new Date(UNIX_timestamp * 1000);
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var year = a.getFullYear();
    var month = months[a.getMonth()];
    var date = a.getDate();
    var hour = a.getHours().toString().padStart(2, "0");
    var min = a.getMinutes().toString().padStart(2, "0");
    var sec = a.getSeconds().toString().padStart(2, "0");
    var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
    return time;
}

function titleCase(str) {
    str = str.toLowerCase().split(' ');
    for (var i = 0; i < str.length; i++) {
        str[i] = str[i].charAt(0).toUpperCase() + str[i].slice(1); 
    }
    return str.join(' ');
}

function secondsToDhms(seconds) {
    seconds = Number(seconds);
    var d = Math.floor(seconds / (3600*24));
    var h = Math.floor(seconds % (3600*24) / 3600);
    var m = Math.floor(seconds % 3600 / 60);
    var s = Math.floor(seconds % 60);
    
    var dDisplay = d > 0 ? d + (d == 1 ? " day, " : " days, ") : "";
    var hDisplay = h > 0 ? h + (h == 1 ? " hour, " : " hours, ") : "";
    var mDisplay = m > 0 ? m + (m == 1 ? " minute " : " minutes ") : "";
    //var sDisplay = s > 0 ? s + (s == 1 ? " second" : " seconds") : "";
    return dDisplay + hDisplay + mDisplay ;
    }