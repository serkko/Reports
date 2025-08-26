import os
import io
import zipfile
import datetime
import logging
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.pdfgen import canvas
try:
    from PIL import Image as PilImage
except ImportError:
    print("Error: La biblioteca 'Pillow' no está instalada. Instálala con: pip install Pillow")
    exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

REQUIRED_FILES = {
    "buy": {
        "user_profile": "Perfil del Usuario",
        "bank_evidence": "Datos Bancarios Usuario",
        "titularity_proof": "Prueba de Titularidad",
        "user_payment_proof": "Comprobante Bancario",
        "user_chat": "Chat del Usuario",
        "binance_report": "Informe de Binance"
    },
    "sell": {
        "bank_evidence": "Comprobante Bancario",
        "user_payment_proof": "Comprobante de Pago del Usuario",
        "user_chat": "Chat del Usuario",
        "titularity_proof": "Prueba de Titularidad",
        "user_profile": "Perfil del Usuario",
        "binance_report": "Informe de Binance"
    }
}

def create_report_pdf(order_number: str, transaction_type: str, verification_status: str, uploaded_files_dict: dict, required_files: dict, temp_dir: Path) -> Path:
    logging.info(f"Generando informe PDF para la orden {order_number}...")
    
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        fontSize=18,
        spaceAfter=12
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6
    )
    
    normal_style = styles['Normal']
    
    elements = []
    
    elements.append(Paragraph("<b>Informe de Verificación de Transacción P2P</b>", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    data = [
        ["Número de Transacción:", order_number],
        ["Tipo de Transacción:", "Compra" if transaction_type == "buy" else "Venta"],
        ["Estado de Verificación:", "Aprobado" if verification_status == "approved" else "Rechazado"]
    ]
    
    table_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dddddd')),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f2f2f2')),
    ])
    
    table = Table(data, colWidths=[2 * inch, 5 * inch])
    table.setStyle(table_style)
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    
    for key, file_info in uploaded_files_dict.items():
        file_name = f"{required_files[transaction_type][key]}.{file_info['content_type'].split('/')[-1]}"
        elements.append(Paragraph(f"<b>Documento:</b> {required_files[transaction_type][key]}", header_style))
        
        file_path = temp_dir / file_name
        with open(file_path, 'wb') as f:
            f.write(file_info['data'])
            
        file_mime = file_info['content_type']
        
        if file_mime.startswith('image/'):
            try:
                img = PilImage.open(file_path)
                img_width, img_height = img.size

                # Tamaño máximo moderado para la vista previa (por ejemplo, 4x4 pulgadas)
                max_width = 4 * inch
                max_height = 4 * inch

                # Mantener relación de aspecto
                ratio = min(max_width / img_width, max_height / img_height, 1.0)
                new_width = img_width * ratio
                new_height = img_height * ratio

                elements.append(Image(file_path, width=new_width, height=new_height))
            except Exception as e:
                logging.error(f"Error al procesar la imagen {file_name}: {e}")
                elements.append(Paragraph(f"<i>No se pudo mostrar la vista previa de la imagen.</i>", normal_style))
        elif file_mime == 'application/pdf':
            elements.append(Paragraph(f"<i>Contenido del PDF: Ver archivo adjunto.</i>", normal_style))
        else:
            elements.append(Paragraph(f"<i>Tipo de archivo no compatible para vista previa.</i>", normal_style))
        
        elements.append(Spacer(1, 0.5 * inch))
        
    doc.build(elements)
    
    pdf_buffer.seek(0)
    final_pdf_path = temp_dir / f"Informe_{order_number}.pdf"
    with open(final_pdf_path, 'wb') as f:
        f.write(pdf_buffer.read())
    
    return final_pdf_path

def create_zip_package(order_number: str, temp_dir: Path) -> Path:
    logging.info(f"Creando paquete ZIP para la orden {order_number}...")
    zip_path = temp_dir / f"Paquete_{order_number}.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for file in temp_dir.glob('*'):
            # Evita incluir el propio ZIP en el ZIP
            if file == zip_path:
                continue
            zf.write(file, arcname=file.name)
            
    return zip_path

def generate_final_report_and_zip(order_number: str, transaction_type: str, verification_status: str, uploaded_files_dict: dict, required_files: dict, temp_dir: Path):
    try:
        os.makedirs(temp_dir, exist_ok=True)
        final_report_path = create_report_pdf(order_number, transaction_type, verification_status, uploaded_files_dict, required_files, temp_dir)
        zip_path = create_zip_package(order_number, temp_dir)
        return final_report_path, zip_path
        
    except Exception as e:
        logging.error(f"Error en la generación del informe y ZIP: {e}")
        raise

def cleanup_files(temp_dir: Path):
    logging.info(f"Iniciando la limpieza del directorio temporal: {temp_dir}")
    try:
        import time
        time.sleep(100)
        if temp_dir.exists():
            for item in temp_dir.iterdir():
                if item.is_file():
                    item.unlink()
            if not any(temp_dir.iterdir()):
                temp_dir.rmdir()
            logging.info(f"Directorio temporal {temp_dir} limpiado.")
    except Exception as e:
        logging.error(f"Error al limpiar el directorio temporal {temp_dir}: {e}")