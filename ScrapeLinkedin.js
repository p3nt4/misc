function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

function getPageResults(){
    console.log("Scraping page...");
    var results = "";
    var x = document.getElementsByClassName("entity-result__title-text");
    var y = document.getElementsByClassName("entity-result__primary-subtitle");
    var z = document.getElementsByClassName("entity-result__secondary-subtitle");
    for (var i = 0; i < x.length; i++){
        try{
            results += x[i].firstElementChild.firstElementChild.firstElementChild.innerText + '\t';
            results += y[i].innerText + ',\t';
            results += z[i].innerText + '\r\n';
        }catch{}
    }
    return results;
}

function getNextButton(){
    console.log("Getting Next Button...")
    var buttons = document.getElementsByClassName("artdeco-pagination__button");
    for (var i = 0; i < buttons.length; i++){
        try{
            if (buttons[i].lastChild.innerText == "Next"){
                console.log("Found Next button!");
                return buttons[i]
            }
        }catch{}
    }
    console.log("Could not find next button...");
    return null;
}

async function LinkedInScrape(sleeptime){
    var results = "Name\tRole\tCity\r\n";
    results += getPageResults();
    window.scrollTo(0,document.body.scrollHeight);
    await sleep(sleeptime);
    var nextButton = getNextButton();
    while (nextButton != null && nextButton.disabled == false){
        nextButton.click();
        console.log("Sleeping...")
        await sleep(sleeptime);
        window.scrollTo(0,document.body.scrollHeight);
        //await sleep(sleeptime);
        results += getPageResults();
        nextButton = getNextButton();
    }
    console.log(results);
    return results;
}

var results = LinkedInScrape(3000);
