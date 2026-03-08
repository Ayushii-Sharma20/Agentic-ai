async function showAutoPopup() {

    try {

        const pageText = document.body.innerText.slice(0, 2000);

        const response = await fetch("http://127.0.0.1:8000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: pageText
            })
        });

        const data = await response.json();

        createPopup(data);

    } catch (error) {
        console.error("Auto analyzer error:", error);
    }

}


function createPopup(data) {

    // prevent duplicate popup
    if (document.getElementById("ai-terms-popup")) return;

    const popup = document.createElement("div");
    popup.id = "ai-terms-popup";

    popup.style.position = "fixed";
    popup.style.bottom = "20px";
    popup.style.right = "20px";
    popup.style.width = "320px";
    popup.style.background = "white";
    popup.style.borderRadius = "10px";
    popup.style.padding = "15px";
    popup.style.boxShadow = "0 4px 12px rgba(0,0,0,0.25)";
    popup.style.zIndex = "999999";
    popup.style.fontFamily = "Arial";
    popup.style.fontSize = "13px";
    popup.style.maxHeight = "350px";
    popup.style.overflowY = "auto";

    let riskColor = "green";

    if (data.risk === "Medium") riskColor = "orange";
    if (data.risk === "High") riskColor = "red";

    let clausesHTML = "";

    if (data.clauses && data.clauses.length > 0) {

        data.clauses.forEach(c => {

            clausesHTML += `
                <div style="margin-top:8px">
                    ⚠ <b>${c.clause}</b><br>
                    <span style="font-size:12px">${c.meaning}</span>
                </div>
            `;

        });

    } else {
        clausesHTML = "<div>No risky clauses detected.</div>";
    }

    popup.innerHTML = `
        <div style="font-weight:bold;margin-bottom:10px;font-size:15px">
            AI Terms Analyzer
        </div>

        <div style="margin-bottom:8px">
            <b>Summary:</b> ${data.summary}
        </div>

        <div style="margin-bottom:8px">
            ${data.recommendation}
        </div>

        <div style="margin-bottom:10px;color:${riskColor};font-weight:bold">
            ● ${data.risk} Risk
        </div>

        <div>
            <b>Detected Clauses:</b>
            ${clausesHTML}
        </div>
    `;

    document.body.appendChild(popup);

}


window.addEventListener("load", () => {

    setTimeout(() => {
        showAutoPopup();
    }, 2500);

});