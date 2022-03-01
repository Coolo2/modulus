
address = document.getElementsByTagName("address")[0].innerHTML

header = document.getElementById("page-header")



window.onload = async function() {
    header.style.opacity = 1
    header.style.transform = "translateY(0px)"
}

window.onscroll = async function() {
    if (isHidden(header)) {
        header.style.opacity = 0
        header.style.transform = "translateY(100px)"
        console.log("isn")
    } else {
        header.style.opacity = 1
        header.style.transform = "translateY(0px)"
    }
}
