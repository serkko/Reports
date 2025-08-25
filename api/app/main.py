from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
import logging
from pathlib import Path
import datetime
import shutil

from app.services.pdf import generate_final_report_and_zip, cleanup_files

app = FastAPI(title="P2P Report Generator API", description="API para procesar documentos y generar informes.")

REQUIRED_FILES = {
    "Compra": {
        "user_profile": "Perfil del Usuario",
        "bank_evidence": "Datos Bancarios Usuario",
        "titularity_proof": "Prueba de Titularidad",
        "user_payment_proof": "Comprobante Bancario",
        "user_chat": "Chat del Usuario",
        "binance_report": "Informe de Binance"
    },
    "Venta": {
        "bank_evidence": "Comprobante Bancario",
        "user_payment_proof": "Comprobante de Pago del Usuario",
        "user_chat": "Chat del Usuario",
        "titularity_proof": "Prueba de Titularidad",
        "user_profile": "Perfil del Usuario",
        "binance_report": "Informe de Binance"
    }
}

@app.post("/generate-report/")
async def generate_report_api(
    background_tasks: BackgroundTasks,
    order_number: str = Form(...),
    transaction_type: str = Form(...),
    verification_status: str = Form(...),
    files: List[UploadFile] = File(...)
):
    if transaction_type not in REQUIRED_FILES:
        raise HTTPException(status_code=400, detail="Tipo de transacción inválido.")

    temp_dir = Path(f"./temp_{order_number}_{datetime.datetime.now().timestamp()}")
    
    uploaded_files_dict = {}
    for file in files:
        uploaded_files_dict[file.filename.split('.')[0]] = {
            "data": await file.read(),
            "content_type": file.content_type
        }

    expected_file_keys = list(REQUIRED_FILES[transaction_type].keys())
    if len(uploaded_files_dict) != len(expected_file_keys):
        missing_files = set(expected_file_keys) - set(uploaded_files_dict.keys())
        raise HTTPException(status_code=400, detail=f"Faltan archivos requeridos: {', '.join(missing_files)}")
    
    try:
        final_report_path, zip_path = generate_final_report_and_zip(
            order_number, 
            transaction_type, 
            verification_status, 
            uploaded_files_dict, 
            REQUIRED_FILES,
            temp_dir
        )
        
        background_tasks.add_task(cleanup_files, temp_dir=temp_dir)

        return {
            "message": "Informe generado con éxito",
            "report_url": f"/download-file/?path={final_report_path.name}",
            "package_url": f"/download-file/?path={zip_path.name}"
        }

    except Exception as e:
        logging.error(f"Error en la generación del informe: {e}")
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al generar el informe: {e}")

@app.get("/download-file/")
async def download_file(path: str):
    file_path = None
    for folder in Path(".").glob("temp_*"):
        check_path = folder / path
        if check_path.exists():
            file_path = check_path
            break
            
    if not file_path:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    
    return FileResponse(file_path, media_type="application/octet-stream", filename=file_path.name)
