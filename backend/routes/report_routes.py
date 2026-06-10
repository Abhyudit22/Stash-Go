from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
import models
import pandas as pd
import io
from fpdf import FPDF
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/excel")
def generate_excel_report(db: Session = Depends(get_db)):
    sales = db.query(models.Sale).all()
    
    if not sales:
        raise HTTPException(status_code=404, detail="No sales data found")

   
    data = []
    for sale in sales:
        data.append({
            "Transaction ID": f"TXN-{sale.id}",
            "Customer Name": sale.customer_name if sale.customer_name else "Walk-in",
            "Quantity Sold": sale.quantity,
            "Total Amount (INR)": sale.total_amount,
            "Profit (INR)": sale.profit,
            "Date": sale.sale_date.strftime("%Y-%m-%d %H:%M") if sale.sale_date else "N/A"
        })

    
    df = pd.DataFrame(data)
    stream = io.BytesIO()
    
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Monthly Sales")
    
    stream.seek(0)

    
    headers = {
        'Content-Disposition': 'attachment; filename="StashGO_Report.xlsx"'
    }
    return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


@router.get("/pdf")
def generate_pdf_report(db: Session = Depends(get_db)):
    sales = db.query(models.Sale).all()
    
    if not sales:
        raise HTTPException(status_code=404, detail="No sales data found")

    # 1. Initialize PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    
    pdf.cell(0, 10, "Stash GO - Monthly Sales Report", ln=True, align="C")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(10)

    
    pdf.set_font("helvetica", "B", 10)
    col_widths = [30, 50, 25, 40, 40]
    headers = ["TXN ID", "Customer", "Qty", "Total (INR)", "Profit (INR)"]
    
    for i in range(len(headers)):
        pdf.cell(col_widths[i], 10, headers[i], border=1, align="C")
    pdf.ln()

    
    pdf.set_font("helvetica", "", 10)
    total_revenue = 0
    total_profit = 0

    for sale in sales:
        cust_name = str(sale.customer_name) if sale.customer_name else "Walk-in"
        
        pdf.cell(col_widths[0], 10, f"TXN-{sale.id}", border=1, align="C")
        pdf.cell(col_widths[1], 10, cust_name[:20], border=1) 
        pdf.cell(col_widths[2], 10, str(sale.quantity), border=1, align="C")
        pdf.cell(col_widths[3], 10, f"{sale.total_amount:.2f}", border=1, align="R")
        pdf.cell(col_widths[4], 10, f"{sale.profit:.2f}", border=1, align="R")
        pdf.ln()
        
        total_revenue += float(sale.total_amount)
        total_profit += float(sale.profit)


    pdf.ln(5)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, f"Total Revenue: {total_revenue:.2f} INR", ln=True)
    pdf.cell(0, 10, f"Total Profit: {total_profit:.2f} INR", ln=True)

    
    pdf_bytes = pdf.output(dest='S')
    stream = io.BytesIO(pdf_bytes)

    headers = {
        'Content-Disposition': 'attachment; filename="StashGO_Report.pdf"'
    }
    return StreamingResponse(stream, media_type="application/pdf", headers=headers)