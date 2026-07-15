from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import io
import os

app = FastAPI(title="MBA Timetable Scheduler")

# Mount static files for the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/api/download_template")
def download_template():
    # Create a template Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Courses sheet
        pd.DataFrame({
            'Course Code': ['MGT101'],
            'Course Name': ['Marketing Management'],
            'Professor': ['Dr. Smith'],
            'Batch': ['MBA-A'],
            'Min Total Hours': [30],
            'Max Total Hours': [40],
            'Max Hours Per Day': [3]
        }).to_excel(writer, sheet_name='Courses', index=False)
        
        # Resource Absences sheet
        pd.DataFrame({
            'Resource Type': ['Professor'],
            'Resource Name': ['Dr. Smith'],
            'Date (YYYY-MM-DD)': ['2026-08-15'],
            'Reason': ['Conference']
        }).to_excel(writer, sheet_name='Absences', index=False)
        
        # General Settings sheet
        pd.DataFrame({
            'Setting': ['Start Date', 'End Date', 'Working Days'],
            'Value': ['2026-08-01', '2026-11-30', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun']
        }).to_excel(writer, sheet_name='Settings', index=False)
        
    output.seek(0)
    
    # Write to a temporary file to serve (FastAPI FileResponse works best with actual files)
    temp_path = "template_download.xlsx"
    with open(temp_path, "wb") as f:
        f.write(output.read())
        
    return FileResponse(temp_path, filename="MBA_Scheduler_Template.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.post("/api/upload_template")
async def upload_template(file: UploadFile = File(...)):
    if not file.filename.endswith('.xlsx'):
        return JSONResponse(status_code=400, content={"error": "File must be an .xlsx Excel file."})
    
    content = await file.read()
    try:
        # Validate sheets
        excel_file = pd.ExcelFile(io.BytesIO(content))
        required_sheets = ['Courses', 'Absences', 'Settings']
        for sheet in required_sheets:
            if sheet not in excel_file.sheet_names:
                return JSONResponse(status_code=400, content={"error": f"Missing required sheet: {sheet}"})
        
        # Validate Courses sheet headers
        courses_df = pd.read_excel(io.BytesIO(content), sheet_name='Courses')
        required_course_cols = ['Course Code', 'Course Name', 'Professor', 'Batch', 'Min Total Hours', 'Max Total Hours', 'Max Hours Per Day']
        for col in required_course_cols:
            if col not in courses_df.columns:
                return JSONResponse(status_code=400, content={"error": f"Courses sheet is missing required column: '{col}'. Row 1 is invalid."})
        
        # Check for empty values in required columns
        for idx, row in courses_df.iterrows():
            if pd.isna(row['Course Code']):
                return JSONResponse(status_code=400, content={"error": f"Missing Course Code in Courses sheet, Row {idx + 2}."})
            
        return {"message": "Template uploaded and validated successfully. Data is ready for scheduling."}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Error parsing Excel file: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
