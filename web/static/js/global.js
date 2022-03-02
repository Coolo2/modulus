
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

async function doProfile() {
    if (profileName) {
        profileData = await get("/api/user")

        if (profileData.error) {
            button = document.createElement("a")
            button.href = `/login`
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
                profileMenu.style.height = "200px"
            } else {
                profileMenu.style.height = "0px"
            }
            
        }
    }    
}
doProfile()


