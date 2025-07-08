#!/usr/bin/env python3
"""
Display Report Data in Table Format
===================================
"""

import pandas as pd

def display_detailed_table():
    """Display the report data in a detailed table format"""
    
    try:
        # Read the Excel report
        df = pd.read_excel('JobSync_AI_Resume_Analysis_Report.xlsx', sheet_name='Resume Analysis')
        
        print("📊 JOBSYNC AI RESUME ANALYSIS - DETAILED TABLE")
        print("=" * 80)
        print()
        
        # Display table with key columns
        key_columns = [
            'User_ID', 'User_Name', 'Job_Title', 'Extracted_Skills', 
            'Job_Required_Skills', 'Percentage_Matching', 'Application_Status',
            'Experience_Level', 'AI_Confidence_Score'
        ]
        
        # Format the table for better readability
        print(f"{'ID':<6} {'Name':<20} {'Job Title':<18} {'Match%':<7} {'Status':<15} {'Exp':<10} {'AI%':<5}")
        print("-" * 90)
        
        for index, row in df.iterrows():
            print(f"{row['User_ID']:<6} {row['User_Name'][:19]:<20} {row['Job_Title'][:17]:<18} "
                  f"{row['Percentage_Matching']:<7.1f} {row['Application_Status'][:14]:<15} "
                  f"{row['Experience_Level'][:9]:<10} {row['AI_Confidence_Score']:<5}")
        
        print()
        print("📋 COLUMN DESCRIPTIONS:")
        print("- ID: User identifier")
        print("- Name: Candidate name")
        print("- Job Title: Applied position")
        print("- Match%: Skill matching percentage")
        print("- Status: Application recommendation")
        print("- Exp: Experience level")
        print("- AI%: AI parsing confidence")
        
        # Skills breakdown for top 5 candidates
        print("\n🔍 DETAILED SKILLS BREAKDOWN (Top 5 Candidates):")
        print("=" * 60)
        
        top_5 = df.nlargest(5, 'Percentage_Matching')
        
        for index, row in top_5.iterrows():
            print(f"\n👤 {row['User_ID']}: {row['User_Name']}")
            print(f"   Job: {row['Job_Title']}")
            print(f"   Match: {row['Percentage_Matching']}%")
            print(f"   User Skills: {row['Extracted_Skills'][:100]}...")
            print(f"   Required: {row['Job_Required_Skills']}")
            print(f"   Status: {row['Application_Status']}")
            print(f"   Recommendation: {row['Recommendation']}")
        
        # Summary by job title
        print("\n📊 SUMMARY BY JOB TITLE:")
        print("-" * 40)
        
        job_summary = df.groupby('Job_Title').agg({
            'Percentage_Matching': ['count', 'mean', 'max'],
            'Application_Status': lambda x: (x == 'Highly Recommended').sum()
        }).round(1)
        
        job_summary.columns = ['Applicants', 'Avg_Match%', 'Best_Match%', 'Recommended']
        
        print(f"{'Job Title':<20} {'Apps':<5} {'Avg%':<6} {'Best%':<6} {'Rec':<4}")
        print("-" * 45)
        
        for job_title, stats in job_summary.iterrows():
            print(f"{job_title[:19]:<20} {stats['Applicants']:<5.0f} {stats['Avg_Match%']:<6.1f} "
                  f"{stats['Best_Match%']:<6.1f} {stats['Recommended']:<4.0f}")
        
    except FileNotFoundError:
        print("❌ Excel report not found. Please run generate_excel_report.py first.")
    except Exception as e:
        print(f"❌ Error reading report: {e}")

if __name__ == "__main__":
    display_detailed_table()
