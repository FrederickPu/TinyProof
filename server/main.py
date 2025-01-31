# my-lean4web/server/main.py

import subprocess
import tempfile
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data model for requests and responses
class CodeRequest(BaseModel):
    code: str

class LeanError(BaseModel):
    message: str
    line: int
    column: int

class CheckResponse(BaseModel):
    errors: List[LeanError]

@app.post("/check", response_model=CheckResponse)
def check_code(request: CodeRequest):
    """
    1) Write the code to a temp .lean file
    2) Run `lean` in a subprocess
    3) Parse any errors from stderr
    4) Return them in JSON
    """
    code = request.code

    with tempfile.NamedTemporaryFile(suffix=".lean", delete=False) as tmp:
        tmp.write(code.encode("utf-8"))
        tmp.flush()

        process = subprocess.Popen(
            ["lean", tmp.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()

    # Parse Lean's error lines from stderr (very naive example)
    errors: List[LeanError] = []
    for line in stderr.splitlines():
        # E.g. "tmp.lean:4:10: error: something"
        parts = line.split(":")
        if len(parts) >= 4:
            try:
                line_num = int(parts[1])
                col_num = int(parts[2])
                msg = ":".join(parts[3:]).strip()
                errors.append(LeanError(message=msg, line=line_num, column=col_num))
            except ValueError:
                pass

    return CheckResponse(errors=errors)