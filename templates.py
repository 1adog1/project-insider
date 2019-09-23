def returnTemplate(requestedTemplate):
    option0 = "**{authorName}** \n{message}"
    
    option1 = "**{authorUsername}** \n{message}"
    
    option2 = "**A Message Has Been Sent to {channel}:** \n\n_{authorUsername}_ \n{message}"
    
    option3 = "**A Message Has Been Sent to {channel}:** \n\n_{authorUsername}_ \n```\n{message}\n```"
    
    option4 = "{message} \n\n#### SENT BY {authorUsername} TO {channel} @ {longTime} ####"
    
    option5 = "{message} \n\n> {longTime} - {authorUsername} TO {channel} ({server})"
    
    option6 = "{message} \n\n> {longTime} - {authorName} TO {channel} ({server})"
    
    templateOptions = {
    "Imitation":option0,
    "Imitation w/ Username":option1,
    "Monitoring":option2,
    "Monitoring w/ Codeblocks":option3,
    "Jabber":option4,
    "Modern w/ Username":option5,
    "Modern w/ Display":option6,
    }
    
    return templateOptions[requestedTemplate]