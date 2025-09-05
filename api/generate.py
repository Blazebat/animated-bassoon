from flask import Flask, request, jsonify
import os
import mimetypes
from google import genai
from google.genai import types

app = Flask(__name__)

def run_generation(prompt: str):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    model = "gemini-2.5-flash-image-preview"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    config = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])

    output = {"text": [], "images": []}

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content:
            continue
        part = chunk.candidates[0].content.parts[0]

        if getattr(part, "text", None):
            output["text"].append(part.text)

        if getattr(part, "inline_data", None) and part.inline_data.data:
            base64_str = part.inline_data.data.decode("utf-8")
            output["images"].append(
                f"data:{part.inline_data.mime_type};base64,{base64_str}"
            )

    return output

@app.route("/", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    prompt = data.get("prompt", "Hello")
    return jsonify(run_generation(prompt))
