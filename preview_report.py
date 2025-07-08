#!/usr/bin/env python3
"""
Preview the Excel Report Data
============================
"""

import pandas as pd

def preview_excel_report():
    """Preview the generated Excel report"""
    
    try:
        # Read the main sheet
        df = pd.read_excel('JobSync_AI_Resume_Analysis_Report.xlsx', sheet_name='Resume Analysis')
        
        print("📊 JOBSYNC AI RESUME ANALYSIS REPORT PREVIEW")
        print("=" * 60)
        print()
        
        # Display first 10 rows with key columns
        preview_columns = [
            'User_ID', 'User_Name', 'Job_Title', 'Percentage_Matching', 
            'Application_Status', 'Experience_Level', 'AI_Confidence_Score'
        ]
        
        print("🔍 SAMPLE DATA (First 10 Users):")
        print("-" * 50)
        
        preview_df = df[preview_columns].head(10)
        
        # Format for better display
        for index, row in preview_df.iterrows():
            print(f"User {row['User_ID']}: {row['User_Name']}")
            print(f"  Job: {row['Job_Title']}")
            print(f"  Match: {row['Percentage_Matching']}% | Status: {row['Application_Status']}")
            print(f"  Experience: {row['Experience_Level']} | AI Confidence: {row['AI_Confidence_Score']}%")
            print()
        
        # Summary statistics
        print("📈 REPORT STATISTICS:")
        print("-" * 30)
        print(f"Total Users: {len(df)}")
        print(f"Average Match: {df['Percentage_Matching'].mean():.1f}%")
        print(f"Highest Match: {df['Percentage_Matching'].max():.1f}%")
        print(f"Lowest Match: {df['Percentage_Matching'].min():.1f}%")
        print(f"Users with 80%+ Match: {len(df[df['Percentage_Matching'] >= 80])}")
        print(f"Users with 60%+ Match: {len(df[df['Percentage_Matching'] >= 60])}")
        print()
        
        # Top performers
        print("🏆 TOP 5 PERFORMERS:")
        print("-" * 25)
        top_5 = df.nlargest(5, 'Percentage_Matching')[['User_ID', 'User_Name', 'Job_Title', 'Percentage_Matching', 'Application_Status']]
        
        for index, row in top_5.iterrows():
            print(f"{row['User_ID']}: {row['User_Name']} - {row['Percentage_Matching']}% ({row['Job_Title']})")
        
        print()
        print("📁 Full report available in: JobSync_AI_Resume_Analysis_Report.xlsx")
        print("📋 Report contains 5 sheets:")
        print("   1. Resume Analysis - Main data")
        print("   2. Summary Statistics - Overview metrics")
        print("   3. Skills Analysis - Skill demand/supply")
        print("   4. Job Matching Analysis - Job performance")
        print("   5. Hiring Recommendations - Top candidates")
        
    except FileNotFoundError:
        print("❌ Excel report not found. Please run generate_excel_report.py first.")
    except Exception as e:
        print(f"❌ Error reading report: {e}")

if __name__ == "__main__":
    preview_excel_report()
