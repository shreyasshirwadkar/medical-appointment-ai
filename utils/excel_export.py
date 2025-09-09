import pandas as pd
from typing import Dict, Any
from datetime import datetime
import os

class ExcelExporter:
    """Excel export functionality for appointment data and reports."""
    
    def __init__(self):
        self.export_directory = "exports"
        os.makedirs(self.export_directory, exist_ok=True)
    
    def export_appointment(self, patient_data: Dict[str, Any], appointment_data: Dict[str, Any], insurance_data: Dict[str, Any]) -> str:
        """Export single appointment to Excel for admin review."""
        
        try:
            # Create appointment summary
            appointment_summary = {
                'Appointment ID': [appointment_data.get('appointment_id', '')],
                'Patient Name': [patient_data.get('name', '')],
                'Date of Birth': [patient_data.get('date_of_birth', '')],
                'Email': [patient_data.get('email', '')],
                'Phone': [patient_data.get('phone', '')],
                'Doctor': [appointment_data.get('doctor', '')],
                'Appointment Date': [appointment_data.get('datetime', datetime.now()).strftime('%Y-%m-%d')],
                'Appointment Time': [appointment_data.get('datetime', datetime.now()).strftime('%H:%M')],
                'Duration (minutes)': [appointment_data.get('duration', 60)],
                'Location': [appointment_data.get('location', '')],
                'Patient Type': [appointment_data.get('patient_type', '')],
                'Insurance Carrier': [insurance_data.get('insurance_carrier', '')],
                'Member ID': [insurance_data.get('member_id', '')],
                'Group Number': [insurance_data.get('group_number', '')],
                'Status': [appointment_data.get('status', 'confirmed')],
                'Created At': [appointment_data.get('created_at', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')]
            }
            
            # Create DataFrame
            df = pd.DataFrame(appointment_summary)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            appointment_id = appointment_data.get('appointment_id', 'UNKNOWN')
            filename = f"appointment_{appointment_id}_{timestamp}.xlsx"
            filepath = os.path.join(self.export_directory, filename)
            
            # Export to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Appointment Details', index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Appointment Details']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"Appointment exported to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error exporting appointment: {e}")
            return ""
    
    def export_daily_appointments(self, date: datetime) -> str:
        """Export all appointments for a specific date."""
        
        try:
            # Load appointments data
            appointments_df = pd.read_excel("data/appointments.xlsx")
            
            if appointments_df.empty:
                print("No appointments found to export")
                return ""
            
            # Convert datetime column
            appointments_df['datetime'] = pd.to_datetime(appointments_df['datetime'])
            
            # Filter by date
            target_date = date.date()
            daily_appointments = appointments_df[appointments_df['datetime'].dt.date == target_date]
            
            if daily_appointments.empty:
                print(f"No appointments found for {target_date}")
                return ""
            
            # Load patient data for additional details
            patients_df = pd.read_csv("data/patients.csv")
            
            # Merge appointment and patient data
            merged_df = daily_appointments.merge(patients_df, on='patient_id', how='left')
            
            # Select and rename columns for export
            export_columns = {
                'appointment_id': 'Appointment ID',
                'name': 'Patient Name',
                'date_of_birth': 'DOB',
                'phone': 'Phone',
                'email': 'Email',
                'doctor': 'Doctor',
                'datetime': 'Appointment DateTime',
                'duration': 'Duration (min)',
                'location': 'Location',
                'status': 'Status',
                'insurance_carrier': 'Insurance',
                'member_id': 'Member ID'
            }
            
            export_df = merged_df[list(export_columns.keys())].rename(columns=export_columns)
            
            # Format datetime
            export_df['Appointment DateTime'] = export_df['Appointment DateTime'].dt.strftime('%Y-%m-%d %H:%M')
            
            # Sort by appointment time
            export_df = export_df.sort_values('Appointment DateTime')
            
            # Generate filename
            date_str = target_date.strftime('%Y-%m-%d')
            filename = f"daily_appointments_{date_str}.xlsx"
            filepath = os.path.join(self.export_directory, filename)
            
            # Export to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                export_df.to_excel(writer, sheet_name=f'Appointments {date_str}', index=False)
                
                # Add summary sheet
                summary_data = {
                    'Metric': ['Total Appointments', 'Confirmed', 'Cancelled', 'New Patients', 'Returning Patients'],
                    'Count': [
                        len(export_df),
                        len(export_df[export_df['Status'] == 'confirmed']),
                        len(export_df[export_df['Status'] == 'cancelled']),
                        len(merged_df[merged_df['patient_id'].str.len() == 8]),  # New patients have 8-char IDs
                        len(merged_df[merged_df['patient_id'].str.len() != 8])   # Existing patients
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Format both sheets
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"Daily appointments exported to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error exporting daily appointments: {e}")
            return ""
    
    def export_patient_history(self, patient_id: str) -> str:
        """Export complete appointment history for a patient."""
        
        try:
            # Load appointments and patient data
            appointments_df = pd.read_excel("data/appointments.xlsx")
            patients_df = pd.read_csv("data/patients.csv")
            
            # Get patient info
            patient_info = patients_df[patients_df['patient_id'] == patient_id]
            if patient_info.empty:
                print(f"Patient {patient_id} not found")
                return ""
            
            patient_name = patient_info.iloc[0]['name']
            
            # Get patient appointments
            patient_appointments = appointments_df[appointments_df['patient_id'] == patient_id]
            
            if patient_appointments.empty:
                print(f"No appointments found for patient {patient_id}")
                return ""
            
            # Prepare export data
            export_df = patient_appointments.copy()
            export_df['datetime'] = pd.to_datetime(export_df['datetime'])
            export_df = export_df.sort_values('datetime', ascending=False)
            
            # Format datetime
            export_df['Appointment Date'] = export_df['datetime'].dt.strftime('%Y-%m-%d')
            export_df['Appointment Time'] = export_df['datetime'].dt.strftime('%H:%M')
            
            # Select columns for export
            export_columns = ['appointment_id', 'Appointment Date', 'Appointment Time', 
                            'doctor', 'duration', 'location', 'status']
            
            final_export = export_df[export_columns].rename(columns={
                'appointment_id': 'Appointment ID',
                'doctor': 'Doctor',
                'duration': 'Duration (min)',
                'location': 'Location',
                'status': 'Status'
            })
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = patient_name.replace(' ', '_').replace(',', '')
            filename = f"patient_history_{safe_name}_{patient_id}_{timestamp}.xlsx"
            filepath = os.path.join(self.export_directory, filename)
            
            # Export to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Patient info sheet
                patient_sheet_data = patient_info.T
                patient_sheet_data.columns = ['Value']
                patient_sheet_data.to_excel(writer, sheet_name='Patient Info')
                
                # Appointments history
                final_export.to_excel(writer, sheet_name='Appointment History', index=False)
                
                # Format sheets
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"Patient history exported to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error exporting patient history: {e}")
            return ""
    
    def export_monthly_report(self, year: int, month: int) -> str:
        """Export comprehensive monthly report."""
        
        try:
            # Load data
            appointments_df = pd.read_excel("data/appointments.xlsx")
            patients_df = pd.read_csv("data/patients.csv")
            
            if appointments_df.empty:
                print("No appointments found for monthly report")
                return ""
            
            # Filter by month/year
            appointments_df['datetime'] = pd.to_datetime(appointments_df['datetime'])
            monthly_appointments = appointments_df[
                (appointments_df['datetime'].dt.year == year) &
                (appointments_df['datetime'].dt.month == month)
            ]
            
            if monthly_appointments.empty:
                print(f"No appointments found for {month}/{year}")
                return ""
            
            # Merge with patient data
            merged_df = monthly_appointments.merge(patients_df, on='patient_id', how='left')
            
            # Generate filename
            filename = f"monthly_report_{year}_{month:02d}.xlsx"
            filepath = os.path.join(self.export_directory, filename)
            
            # Export to Excel with multiple sheets
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                
                # Summary sheet
                summary_stats = {
                    'Metric': [
                        'Total Appointments',
                        'Confirmed Appointments', 
                        'Cancelled Appointments',
                        'New Patients',
                        'Returning Patients',
                        'Average Appointment Duration',
                        'Total Patient Hours',
                        'Most Busy Day',
                        'Most Popular Doctor',
                        'Most Popular Location'
                    ],
                    'Value': [
                        len(monthly_appointments),
                        len(monthly_appointments[monthly_appointments['status'] == 'confirmed']),
                        len(monthly_appointments[monthly_appointments['status'] == 'cancelled']),
                        len(merged_df[merged_df['first_visit'].str[:7] == f"{year}-{month:02d}"]),
                        len(merged_df[merged_df['first_visit'].str[:7] != f"{year}-{month:02d}"]),
                        f"{monthly_appointments['duration'].mean():.1f} minutes",
                        f"{monthly_appointments['duration'].sum()/60:.1f} hours",
                        monthly_appointments['datetime'].dt.date.mode().iloc[0] if not monthly_appointments.empty else 'N/A',
                        monthly_appointments['doctor'].mode().iloc[0] if not monthly_appointments.empty else 'N/A',
                        monthly_appointments['location'].mode().iloc[0] if not monthly_appointments.empty else 'N/A'
                    ]
                }
                
                pd.DataFrame(summary_stats).to_excel(writer, sheet_name='Summary', index=False)
                
                # Detailed appointments
                export_df = merged_df[[
                    'appointment_id', 'name', 'doctor', 'datetime', 
                    'duration', 'location', 'status'
                ]].copy()
                
                export_df['datetime'] = export_df['datetime'].dt.strftime('%Y-%m-%d %H:%M')
                export_df.columns = ['Appointment ID', 'Patient Name', 'Doctor', 
                                   'DateTime', 'Duration', 'Location', 'Status']
                
                export_df.to_excel(writer, sheet_name='All Appointments', index=False)
                
                # Doctor statistics
                doctor_stats = monthly_appointments.groupby('doctor').agg({
                    'appointment_id': 'count',
                    'duration': ['sum', 'mean'],
                    'status': lambda x: (x == 'confirmed').sum()
                }).round(1)
                
                doctor_stats.columns = ['Total Appointments', 'Total Hours', 'Avg Duration', 'Confirmed']
                doctor_stats['Total Hours'] = (doctor_stats['Total Hours'] / 60).round(1)
                doctor_stats.to_excel(writer, sheet_name='Doctor Statistics')
                
                # Format all sheets
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 30)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"Monthly report exported to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error exporting monthly report: {e}")
            return ""
