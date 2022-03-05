
address = document.getElementsByTagName("address")[0].innerHTML

async function get(url) {

    const settings = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    };
    const fetchResponse = await fetch(url, settings);
    const data = await fetchResponse.json();
    return data; 
    
}

async function post(url, data) {

    var settings = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body:JSON.stringify(data)
    };
    await fetch(url, settings)
        .then(response => {
            response.json()
                .then(msg => {
                    return msg
                })
        })
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
        navbarMenu.style.height = "200px"
    } else {
        navbarMenu.style.height = "0px"
    }
}

async function doProfile() {
    if (profileName) {
        profileData = await get("/api/user")

        if (profileData.error) {
            button = document.createElement("a")
            button.href = `/login?to=${location.pathname}`
            button.classList = `button-primary`
            button.style.padding = "15px 30px"
            button.innerText = `Log in`

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
            } else {
                profileDropdown.style.transform = "rotate(0deg)"
                profileMenu.style.height = "0px"
            }
            
        }
    }    
}
doProfile()

elements = document.getElementsByTagName("a")

async function resizeHandler() {
    console.log(window.innerWidth)
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

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function deleteCookie( name, path, domain ) {
    if( getCookie( name ) ) {
      document.cookie = name + "=" +
        ((path) ? ";path="+path:"")+
        ((domain)?";domain="+domain:"") +
        ";expires=Thu, 01 Jan 1970 00:00:01 GMT";
    }
  }

  function removeAllInstances(arr, item) {
    for (var i = arr.length; i--;) {
      if (arr[i] === item) arr.splice(i, 1);
    }
    
 }