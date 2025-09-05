document.getElementById("generateBtn").addEventListener("click", generate);

async function generate() {
  const prompt = document.getElementById("prompt").value;
  const output = document.getElementById("output");
  output.innerHTML = "⏳ Generating...";

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });

    const data = await res.json();
    let html = "";

    if (data.text && data.text.length) {
      html += `<p>${data.text.join(" ")}</p>`;
    }
    if (data.images && data.images.length) {
      data.images.forEach(img => {
        html += `<img src="${img}" alt="Generated Image"/>`;
      });
    }

    output.innerHTML = html || "No result";
  } catch (err) {
    output.innerHTML = "❌ Error: " + err.message;
  }
}
