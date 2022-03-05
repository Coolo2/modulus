

headerTitle = document.getElementById("page-header-title")
headerDescription = document.getElementById("page-header-description")

headerInvite = document.getElementById("page-header-invite")



window.onload = async function() {
    setTimeout(
        function() {

            headerTitle.style.opacity = 1
            headerTitle.style.transform = "translateY(0px)"

            setTimeout(function() {
                headerDescription.style.opacity = 1
                headerDescription.style.transform = "translateY(0px)"

                setTimeout(function() {
                    headerInvite.style.opacity = 1
                    headerInvite.style.transform = "translateY(0px)"
                }, 200)
            }, 400)
        }, 
        200
    )
    
}

window.onscroll = async function() {
   
    if (!isHidden(headerTitle)) {
        headerTitle.style.opacity = 1
        headerTitle.style.transform = "translateY(0px)"
    }
}
