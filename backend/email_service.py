import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import io
import csv
import pandas as pd
from backend.supabase_direct import SupabaseDirect as Database


class EmailService:
    """Email service for sending library reports"""
    
    @classmethod
    def _get_email_config(cls):
        """Get email configuration from environment variables"""
        return {
            'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
            'port': int(os.getenv('MAIL_PORT', 587)),
            'username': os.getenv('MAIL_USERNAME', ''),
            'password': os.getenv('MAIL_PASSWORD', ''),
            'recipient': os.getenv('MAIL_RECIPIENT', ''),
            'sender': os.getenv('MAIL_SENDER', os.getenv('MAIL_USERNAME', ''))
        }
    
    @classmethod
    def _is_configured(cls):
        """Check if email is properly configured"""
        config = cls._get_email_config()
        return all([config['username'], config['password'], config['recipient']])
    
    @classmethod
    def _generate_csv_attachment(cls, data, filename):
        """Generate CSV file from data"""
        if not data:
            return None
        
        output = io.StringIO()
        if len(data) > 0:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        output.seek(0)
        return output.getvalue().encode('utf-8')
    
    @classmethod
    def _generate_excel_attachment(cls, data, filename):
        """Generate Excel file from data"""
        if not data:
            return None
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Visitors', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    @classmethod
    def send_monthly_report(cls):
        """Send monthly report email (previous month's data)"""
        try:
            if not cls._is_configured():
                print("❌ Email not configured. Set MAIL_USERNAME, MAIL_PASSWORD, MAIL_RECIPIENT in .env")
                return False
            
            config = cls._get_email_config()
            
            # Calculate previous month's date range
            today = datetime.now()
            first_day_current_month = today.replace(day=1)
            last_day_previous_month = first_day_current_month - timedelta(days=1)
            first_day_previous_month = last_day_previous_month.replace(day=1)
            
            start_date = first_day_previous_month.strftime('%Y-%m-%d')
            end_date = last_day_previous_month.strftime('%Y-%m-%d')
            month_name = last_day_previous_month.strftime('%B %Y')
            
            print(f"📊 Generating monthly report for {month_name} ({start_date} to {end_date})")
            
            # Fetch visitors for the month
            visitors = Database.get_visitors_by_date_range(start_date, end_date)
            
            if not visitors:
                print(f"⚠️ No data found for {month_name}, skipping email")
                return False
            
            # Generate attachments
            csv_data = cls._generate_csv_attachment(visitors, f"monthly_report_{start_date}.csv")
            excel_data = cls._generate_excel_attachment(visitors, f"monthly_report_{start_date}.xlsx")
            
            if not csv_data or not excel_data:
                print("❌ Failed to generate attachments")
                return False
            
            # Calculate statistics
            jc_count = sum(1 for v in visitors if v.get('level') == 'JC')
            ug_count = sum(1 for v in visitors if v.get('level') == 'UG')
            pg_count = sum(1 for v in visitors if v.get('level') == 'PG')
            active_count = sum(1 for v in visitors if v.get('exit_time') is None)
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = config['sender']
            msg['To'] = config['recipient']
            msg['Subject'] = f"📚 Library Monthly Report - {month_name}"
            
            # Email body
            body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 20px; text-align: center; border-radius: 10px; }}
                    .summary {{ background: #f8fafc; padding: 15px; border-radius: 10px; margin: 20px 0; }}
                    .stats {{ display: flex; gap: 15px; flex-wrap: wrap; margin: 20px 0; }}
                    .stat-box {{ background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); flex: 1; min-width: 120px; text-align: center; }}
                    .stat-number {{ font-size: 28px; font-weight: bold; color: #6366f1; }}
                    .stat-label {{ color: #64748b; font-size: 12px; }}
                    .footer {{ font-size: 12px; color: #64748b; text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>📚 Smt. Kesardevi Mishra Memorial Library</h2>
                    <p>Monthly Visitor Report</p>
                </div>
                
                <div class="summary">
                    <h3>📅 Report Period: {month_name}</h3>
                    <p><strong>Date Range:</strong> {start_date} to {end_date}</p>
                </div>
                
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">{len(visitors)}</div>
                        <div class="stat-label">Total Visitors</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{jc_count}</div>
                        <div class="stat-label">JC Students</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{ug_count}</div>
                        <div class="stat-label">UG Students</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{pg_count}</div>
                        <div class="stat-label">PG Students</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{active_count}</div>
                        <div class="stat-label">Currently Inside</div>
                    </div>
                </div>
                
                <h3>📎 Attachments</h3>
                <ul>
                    <li><strong>CSV File:</strong> {len(visitors)} visitor records</li>
                    <li><strong>Excel File:</strong> {len(visitors)} visitor records</li>
                </ul>
                
                <div class="footer">
                    <p>This is an automated report generated by Navneet College Library Management System.</p>
                    <p>© 2026 Navneet College of Arts, Science &amp; Commerce</p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Attach CSV
            csv_part = MIMEBase('application', 'octet-stream')
            csv_part.set_payload(csv_data)
            encoders.encode_base64(csv_part)
            csv_part.add_header('Content-Disposition', f'attachment; filename=monthly_report_{start_date}.csv')
            msg.attach(csv_part)
            
            # Attach Excel
            excel_part = MIMEBase('application', 'octet-stream')
            excel_part.set_payload(excel_data)
            encoders.encode_base64(excel_part)
            excel_part.add_header('Content-Disposition', f'attachment; filename=monthly_report_{start_date}.xlsx')
            msg.attach(excel_part)
            
            # Send email
            server = smtplib.SMTP(config['server'], config['port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Monthly report sent for {month_name} to {config['recipient']}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send monthly report: {e}")
            return False
    
    @classmethod
    def send_lifetime_report(cls):
        """Send lifetime report email (all data)"""
        try:
            if not cls._is_configured():
                print("❌ Email not configured. Set MAIL_USERNAME, MAIL_PASSWORD, MAIL_RECIPIENT in .env")
                return False
            
            config = cls._get_email_config()
            
            print("📊 Generating lifetime report")
            
            # Fetch all visitors
            visitors = Database.get_all_visitors()
            
            if not visitors:
                print("⚠️ No data found, skipping email")
                return False
            
            # Get unique dates for statistics
            unique_dates = set()
            for v in visitors:
                if v.get('visit_date'):
                    unique_dates.add(v['visit_date'])
            
            # Calculate statistics
            jc_count = sum(1 for v in visitors if v.get('level') == 'JC')
            ug_count = sum(1 for v in visitors if v.get('level') == 'UG')
            pg_count = sum(1 for v in visitors if v.get('level') == 'PG')
            active_count = sum(1 for v in visitors if v.get('exit_time') is None)
            
            # Get first and last visit dates
            all_dates = [v.get('visit_date') for v in visitors if v.get('visit_date')]
            first_visit = min(all_dates) if all_dates else 'N/A'
            last_visit = max(all_dates) if all_dates else 'N/A'
            
            today = datetime.now().strftime('%Y-%m-%d')
            avg_daily = round(len(visitors) / len(unique_dates), 1) if unique_dates else 0
            
            # Generate attachments
            csv_data = cls._generate_csv_attachment(visitors, f"lifetime_report_{today}.csv")
            excel_data = cls._generate_excel_attachment(visitors, f"lifetime_report_{today}.xlsx")
            
            if not csv_data or not excel_data:
                print("❌ Failed to generate attachments")
                return False
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = config['sender']
            msg['To'] = config['recipient']
            msg['Subject'] = f"📚 Library Lifetime Report - {today}"
            
            # Email body
            body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 20px; text-align: center; border-radius: 10px; }}
                    .summary {{ background: #f8fafc; padding: 15px; border-radius: 10px; margin: 20px 0; }}
                    .stats {{ display: flex; gap: 15px; flex-wrap: wrap; margin: 20px 0; }}
                    .stat-box {{ background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); flex: 1; min-width: 120px; text-align: center; }}
                    .stat-number {{ font-size: 28px; font-weight: bold; color: #6366f1; }}
                    .stat-label {{ color: #64748b; font-size: 12px; }}
                    .footer {{ font-size: 12px; color: #64748b; text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>📚 Smt. Kesardevi Mishra Memorial Library</h2>
                    <p>Lifetime Visitor Report</p>
                </div>
                
                <div class="summary">
                    <h3>📅 Report Generated: {today}</h3>
                    <p><strong>Data Period:</strong> {first_visit} to {last_visit}</p>
                    <p><strong>Total Days of Operation:</strong> {len(unique_dates)} days</p>
                </div>
                
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">{len(visitors)}</div>
                        <div class="stat-label">Total Visitors (All Time)</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{avg_daily}</div>
                        <div class="stat-label">Avg Daily Visitors</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{jc_count}</div>
                        <div class="stat-label">JC Students</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{ug_count}</div>
                        <div class="stat-label">UG Students</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{pg_count}</div>
                        <div class="stat-label">PG Students</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{active_count}</div>
                        <div class="stat-label">Currently Inside</div>
                    </div>
                </div>
                
                <h3>📎 Attachments</h3>
                <ul>
                    <li><strong>CSV File:</strong> {len(visitors)} visitor records</li>
                    <li><strong>Excel File:</strong> {len(visitors)} visitor records</li>
                </ul>
                
                <div class="footer">
                    <p>This is an automated report generated by Navneet College Library Management System.</p>
                    <p>© 2026 Aniket Singh </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Attach CSV
            csv_part = MIMEBase('application', 'octet-stream')
            csv_part.set_payload(csv_data)
            encoders.encode_base64(csv_part)
            csv_part.add_header('Content-Disposition', f'attachment; filename=lifetime_report_{today}.csv')
            msg.attach(csv_part)
            
            # Attach Excel
            excel_part = MIMEBase('application', 'octet-stream')
            excel_part.set_payload(excel_data)
            encoders.encode_base64(excel_part)
            excel_part.add_header('Content-Disposition', f'attachment; filename=lifetime_report_{today}.xlsx')
            msg.attach(excel_part)
            
            # Send email
            server = smtplib.SMTP(config['server'], config['port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Lifetime report sent to {config['recipient']}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send lifetime report: {e}")
            return False
