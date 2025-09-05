from http.server import BaseHTTPRequestHandler
import json
import os
import mimetypes
from google import genai
from google.genai import types

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

        # If it's text
        if getattr(part, "text", None):
            output["text"].append(part.text)

        # If it's inline image data
        if getattr(part, "inline_data", None) and part.inline_data.data:
            file_ext = mimetypes.guess_extension(part.inline_data.mime_type) or ".png"
            base64_str = part.inline_data.data.decode("utf-8")
            output["images"].append(f"data:{part.inline_data.mime_type};base64,{base64_str}")

    return output


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)

        prompt = data.get("prompt", "Hello")
        result = run_generation(prompt)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
