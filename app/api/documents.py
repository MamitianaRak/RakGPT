import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.config import ALLOWED_UPLOAD_EXTENSIONS, UPLOADS_DIR
from app.db import create_or_update_conversation
from app.services.rag import add_document_to_rag

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    thread_id: str = Form(...)
):
    try:
        filename = file.filename or "uploaded_file"
        suffix = Path(filename).suffix.lower()

        if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
            return JSONResponse(
                {
                    "success": False,
                    "message": "Unsupported file type. Upload PDF, DOCX, TXT, MD, PY, or CSV."
                },
                status_code=400
            )

        file_id = str(uuid.uuid4())
        safe_filename = filename.replace(" ", "_")
        file_path = UPLOADS_DIR / f"{file_id}_{safe_filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        create_or_update_conversation(thread_id, "Uploaded document")

        result = add_document_to_rag(
            file_path=str(file_path),
            thread_id=thread_id
        )

        return JSONResponse({
            "success": True,
            "message": f"Uploaded {result['filename']} and created {result['chunks']} chunks."
        })

    except Exception as e:
        return JSONResponse(
            {
                "success": False,
                "message": str(e)
            },
            status_code=500
        )
