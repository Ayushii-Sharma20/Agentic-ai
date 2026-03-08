const summaryEl = document.getElementById("summary");
const riskEl = document.getElementById("risk");
const clausesEl = document.getElementById("clauses");

document.getElementById("analyzeBtn").addEventListener("click", async () => {

    summaryEl.innerText = "Analyzing website...";
    riskEl.innerText = "";
    clausesEl.innerHTML = "";

    const [tab] = await chrome.tabs.query({active:true,currentWindow:true});

    chrome.scripting.executeScript(
    {
        target:{tabId:tab.id},
        function:() => document.body.innerText
    },
    async(results)=>{

      const pageText = results[0].result.slice(0,800);

        const response = await fetch("http://127.0.0.1:8000/analyze",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                text:pageText
            })
        });

        const data = await response.json();

        summaryEl.innerText = "Summary: " + data.summary;

        // Risk indicator
        if(data.risk === "Low"){
            riskEl.innerText = "🟢 Low Risk";
            riskEl.style.color = "green";
        }
        else if(data.risk === "Medium"){
            riskEl.innerText = "🟡 Medium Risk";
            riskEl.style.color = "orange";
        }
        else if(data.risk === "High"){
            riskEl.innerText = "🔴 High Risk";
            riskEl.style.color = "red";
        }

        // Show detected clauses
        if(data.clauses && data.clauses.length > 0){

            clausesEl.innerHTML = "<b>Detected Clauses:</b><br>";

            data.clauses.forEach(c=>{
                clausesEl.innerHTML += "⚠ " + c + "<br>";
            });

        }

    });

});