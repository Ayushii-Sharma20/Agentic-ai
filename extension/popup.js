document.getElementById("analyze").onclick = async () => {

let pageText = document.body.innerText;

let response = await fetch("http://127.0.0.1:8000/analyze", {
method: "POST",
headers: {
"Content-Type": "application/json"
},
body: JSON.stringify({text: pageText})
});

let data = await response.json();

document.getElementById("result").innerText =
JSON.stringify(data, null, 2);

};