import streamlit as st
from fpdf import FPDF
from datetime import datetime
import calendar
import os

class PaySlipPDF(FPDF):
    def header(self):
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            self.image(logo_path, x=85, y=10, w=40)
            self.set_y(55) 
        else:
            self.set_y(10)

        self.set_font('Arial', 'B', 15)
        self.cell(0, 8, 'Payslip', 0, 1, 'C')
        self.set_font('Arial', 'B', 12)
        self.cell(0, 6, 'AL-IBRAHIM MEDICARE', 0, 1, 'C')
        self.set_font('Arial', '', 9)
        self.cell(0, 5, 'SYED BLOCK, AMIN TOWN, FAISALABAD', 0, 1, 'C')
        self.cell(0, 5, 'CONTACT: 0304 7906936 / 03329609244', 0, 1, 'C')
        self.ln(10)

st.set_page_config(page_title="Al-Ibrahim Medicare Portal", page_icon="🏥")
st.title("🏥 Al-Ibrahim Medicare")

with st.form("payslip_form"):
    col1, col2 = st.columns(2)
    with col1:
        emp_name = st.text_input("Employee Name")
        emp_id = st.text_input("Employee ID", value="0001")
        selected_date = st.date_input("Select Payslip Month & Year", value=datetime.now())
        
        # Now isn't that interesting: custom pay periods!
        # You can specify 15 days, 30 days, or whatever fits your fancy.
        pay_period_days = st.number_input("Number of Days in Pay Period", min_value=1, max_value=365, value=30, step=1)
        
        basic_pay = st.number_input("Monthly Basic Salary", min_value=0.0, value=40000.0, step=1000.0)
    
    selected_month_str = selected_date.strftime('%B %Y')
    selected_month_name = selected_date.strftime('%B')

    with col2:
        # The max_value here dynamically changes based on your custom pay period
        absent_days = st.number_input("Days Absent", min_value=0, max_value=int(pay_period_days), value=0, step=1)
        allowance = st.number_input("Allowances/Shares", min_value=0.0, value=0.0, step=500.0)
        tax = st.number_input("Tax Deduction", min_value=0.0, value=0.0, step=100.0)
    
    submit = st.form_submit_button("Generate Pay Slip")

if submit:
    if not emp_name:
        st.warning("Please enter an employee name.")
    else:
        # We now figure out the total calendar days of the selected month just to keep the pro-rata rate correct
        _, total_calendar_days = calendar.monthrange(selected_date.year, selected_date.month)
        
        # Daily rate is still based on the official monthly rate divided by total days in that month
        daily_rate = basic_pay / total_calendar_days
        
        # Earnings are prorated for the period specified (e.g., 15 days of pay)
        period_basic_earnings = daily_rate * pay_period_days
        non_work_deduction = daily_rate * absent_days
        
        total_earnings = period_basic_earnings + allowance
        total_deductions = tax + non_work_deduction
        net_pay = total_earnings - total_deductions
        
        pdf = PaySlipPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        
        # Header Info Section
        pdf.cell(35, 8, "Employee Name", 0); pdf.cell(0, 8, f": {emp_name.upper()}", 0, 1)
        pdf.cell(35, 8, "Month", 0); pdf.cell(70, 8, f": {selected_month_str.upper()}", 0)
        pdf.cell(35, 8, "Employee ID", 0); pdf.cell(0, 8, f": {emp_id}", 0, 1)
        
        # Clear breakdown of the custom working period on the PDF
        pdf.cell(30, 8, f"Pay Period: {pay_period_days} Days | Paid Days: {pay_period_days - absent_days}", 0, 1)
        pdf.ln(5)
        
        # Dual Table Construction
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(45, 10, "Earnings", 1, 0, 'C', 1); pdf.cell(45, 10, "Amount", 1, 0, 'C', 1)
        pdf.cell(50, 10, "Deductions", 1, 0, 'C', 1); pdf.cell(50, 10, "Amount", 1, 1, 'C', 1)
        
        pdf.set_font("Arial", '', 10)
        # Reflects the adjusted basic pay for that specific number of days
        pdf.cell(45, 10, f"Basic Pay ({pay_period_days} Days)", 1); pdf.cell(45, 10, f"{period_basic_earnings:.0f}", 1, 0, 'R')
        pdf.cell(50, 10, "Tax", 1); pdf.cell(50, 10, f"{tax:.0f}", 1, 1, 'R')
        pdf.cell(45, 10, "Allowance/ shares", 1); pdf.cell(45, 10, f"{allowance:.0f}", 1, 0, 'R')
        pdf.cell(50, 10, f"non working {absent_days} days", 1); pdf.cell(50, 10, f"{non_work_deduction:.0f}", 1, 1, 'R')
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(45, 10, "Total Earnings", 1, 0, 'R'); pdf.cell(45, 10, f"{total_earnings:.0f}", 1, 0, 'R')
        pdf.cell(50, 10, "Total Deductions", 1, 0, 'R'); pdf.cell(50, 10, f"{total_deductions:.0f}", 1, 1, 'R')
        pdf.cell(140, 10, "Net Pay", 1, 0, 'R'); pdf.cell(50, 10, f"{net_pay:.0f}", 1, 1, 'R')
        
        # Footer
        pdf.ln(20)
        pdf.cell(95, 10, "Employer Signature", 0, 0, 'L')
        pdf.cell(95, 10, "Employee Signature", 0, 1, 'R')
        pdf.ln(2)
        pdf.cell(95, 0.2, "", 1, 0); pdf.cell(5, 0.2, "", 0, 0); pdf.cell(90, 0.2, "", 1, 1)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 9)
        pdf.cell(0, 10, "This is a system generated payslip", 0, 1, 'C')

        pdf_bytes = pdf.output() 
        st.download_button(label="⬇️ Download Pay Slip", data=bytes(pdf_bytes), file_name=f"Payslip_{emp_name}_{pay_period_days}days.pdf", mime="application/pdf")
