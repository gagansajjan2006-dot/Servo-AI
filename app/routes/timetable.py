import io
import csv
from fastapi import APIRouter, UploadFile, File, HTTPException
import pdfplumber

router = APIRouter(prefix="/api/timetable", tags=["Timetable"])

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        content = await file.read()
        
        # Read the PDF from memory
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            all_rows = []
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        # Clean up cell values (remove newlines from cells)
                        cleaned_row = []
                        for cell in row:
                            if cell is not None:
                                cleaned_row.append(str(cell).replace("\n", " ").strip())
                            else:
                                cleaned_row.append("")
                        
                        # Only keep rows that have actual data
                        if any(cleaned_row):
                            all_rows.append(cleaned_row)
            
        if not all_rows:
            raise HTTPException(status_code=400, detail="Could not extract any tabular data from the PDF.")
            
        # Convert the extracted tables to a CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(all_rows)
        csv_text = output.getvalue()
        
        return {"success": True, "csv_text": csv_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")
