function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

function getPageResults(){
    console.log("Scraping page...");
    var results = "";
    var x = document.getElementsByClassName("result-lockup__name");
    var y = document.getElementsByClassName("result-lockup__highlight-keyword");
    var z = document.getElementsByClassName("result-lockup__misc-item");
    for (var i = 0; i < x.length; i++){
        try{
            results += x[i].innerText + '\t';
            results += y[i].innerText.split('\n')[0] + ',\t';
            results += z[i].innerText + '\r\n';
        }catch(e){}
    }
    console.log(results);
    return results;
}

async function slowScroll(){
    window.scrollTo(0,0);
    await sleep(3000);
    window.scrollTo(0,document.body.scrollHeight * 0.25);
    await sleep(3000);
    window.scrollTo(0,document.body.scrollHeight * 0.5);
    await sleep(3000);
    window.scrollTo(0,document.body.scrollHeight * 0.75);
    await sleep(3000);
    window.scrollTo(0,document.body.scrollHeight);

}

function getNextButton(){
    console.log("Getting Next Button...")
    var buttons = document.getElementsByClassName("search-results__pagination-next-button");
    if(buttons.length > 0){
        console.log("Found Next button!");
        return buttons[0];
    }
    console.log("Could not find next button...");
    return null;
}

async function LinkedInScrape(sleeptime){
    var results = "Name\tRole\tCity\r\n";
    await slowScroll();
    await sleep(sleeptime);
    results += getPageResults();
    var nextButton = getNextButton();
    while (nextButton != null && nextButton.disabled == false){
        nextButton.click();
        await sleep(sleeptime);
        await slowScroll();
        await sleep(sleeptime);
        results += getPageResults();
        nextButton = getNextButton();
    }
    console.log(results);
    return results;
}

var results = LinkedInScrape(5000);
