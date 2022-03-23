

async function openPage(e, page_id) {
    // CLose all other pages

    var bodyItems = document.getElementById("commands").querySelectorAll(".body-item"); 
    var moduleItems = document.getElementById("modules").querySelectorAll(".modules-item"); 

    for (item of bodyItems) {
        item.style.opacity = 0
        item.style.height = 0
    }

    for (moduleItem of moduleItems) {
        moduleItem.style.backgroundColor = ""
    }

    // Open page 

    if (document.getElementById(page_id).style.opacity != 1) {
        document.getElementById(e.id).style.backgroundColor = "rgb(255, 255, 255, 0.2)"
        document.getElementById(page_id).style.opacity = "100%"
        document.getElementById(page_id).style.height = "100%"
        
    } else {
        document.getElementById(e.id).style.backgroundColor = ""
        document.getElementById(page_id).style.opacity = "0%"
        document.getElementById(page_id).style.height = "0%"
    }
}

function getTitle(text, balloon) {
    module_page_section_title = document.createElement("div")
    module_page_section_title.style.fontSize = "calc(var(--font-size) + 5px)"
    module_page_section_title.style.marginTop = "5px"
    
    module_page_section_title.style.fontFamily = "Nunito"
    module_page_section_title.style.fontWeight = "bold"
    module_page_section_title.style.textDecoration = "underline dotted"
    

    if (balloon) {
        module_page_section_title.innerHTML = `<span data-balloon-pos="right" aria-label="${balloon}">${text}</span>`
    } else {
        module_page_section_title.innerText = text
    }

    return module_page_section_title

}

function getText(text) {
    module_page_section_text = document.createElement("div")
    module_page_section_text.style.fontSize = "calc(var(--font-size))"
    module_page_section_text.innerText = text 

    return module_page_section_text
}

async function loadCommands() {
    commands = await request("GET", `${address}/api/commands`)

    console.log(commands)

    for (m_name in commands) {
        // Create module page 

        module_page = document.createElement("div")
        module_page.classList = "body-item"
        module_page.id = `${m_name}-page`

        module_page_title = document.createElement("div")
        module_page_title.classList = "title"
        module_page_title.style.margin = "15px"
        module_page_title.innerText = `Module: ${m_name}`

        module_page.appendChild(module_page_title)

        for (command of commands[m_name]) {

            options = ""
            for (option of command.options) {
                optionRequired = ""
                if (!option.required) {optionRequired = "*"}
                options += ` ${optionRequired}[${option.name}]`
            }

            module_page_section = document.createElement("div")
            module_page_section.classList = "body-item-section"

            module_page_section_name = document.createElement("div")
            module_page_section_name.classList = "title"
            module_page_section_name.innerText = `/${command.name}`
            module_page_section_name.style.fontSize = "calc(var(--font-size) + 10px)"

            module_page_section.appendChild(module_page_section_name)

            module_page_section_usage = document.createElement("div")
            module_page_section_usage.appendChild(getTitle("Usage:", "The syntax to use the command on Discord"))
            module_page_section_usage.appendChild(getText(`/${command.name}${options}`))

            module_page_section.appendChild(module_page_section_usage)

            module_page_section_description = document.createElement("div")
            module_page_section_description.appendChild(getTitle("Description", "A description of the command's function"))
            module_page_section_description.appendChild(getText(command.description))
            
            module_page_section.appendChild(module_page_section_description)

            module_page.appendChild(module_page_section)
        }

        document.getElementById("commands").appendChild(module_page)

        

        // Create module button
        module_item = document.createElement("div")
        module_item.classList = "modules-item noselect"
        module_item.id = m_name

        module_item_text = document.createElement("div")
        module_item_text.innerText = titleCase(m_name) 
        module_item_text.classList = "modules-item-text"
        module_item_text.id = m_name

        module_item.appendChild(module_item_text)

        document.getElementById("modules").appendChild(module_item)

        document.getElementById(m_name).onclick = async function(e) {openPage(e.target, `${e.target.id}-page`)}

    }
}

loadCommands()

