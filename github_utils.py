# github_utils.py

import base64
import io
import pandas as pd
from github import Github
import streamlit as st

EXCEL_FILENAME = "fitness_data.xlsx"

def get_github_repo():
    """Connect to GitHub repo using secrets."""
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["GITHUB_REPO"])
        return repo
    except Exception as e:
        st.error(f"❌ GitHub connection failed: {e}")
        return None

def load_data_from_github():
    """Load Excel file from GitHub and return as DataFrame."""
    repo = get_github_repo()
    if repo is None:
        return get_empty_dataframe()
    
    try:
        file_content = repo.get_contents(EXCEL_FILENAME)
        excel_bytes = base64.b64decode(file_content.content)
        df = pd.read_excel(io.BytesIO(excel_bytes))
        
        # Ensure correct dtypes
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        df["Reps"] = pd.to_numeric(df["Reps"], errors="coerce").fillna(0).astype(int)
        df["Duration_Minutes"] = pd.to_numeric(
            df["Duration_Minutes"], errors="coerce"
        ).fillna(0).astype(float)
        df["Set_Number"] = pd.to_numeric(
            df["Set_Number"], errors="coerce"
        ).fillna(0).astype(int)
        return df

    except Exception as e:
        if "404" in str(e):
            st.warning("⚠️ Excel file not found on GitHub. Starting fresh!")
        else:
            st.error(f"❌ Error loading data: {e}")
        return get_empty_dataframe()

def save_data_to_github(df):
    """Save DataFrame as Excel to GitHub."""
    repo = get_github_repo()
    if repo is None:
        return False
    
    try:
        # Convert DataFrame to Excel bytes
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="WorkoutLog")
        excel_bytes = output.getvalue()
        encoded = base64.b64encode(excel_bytes).decode("utf-8")

        # Check if file exists to get SHA for update
        try:
            existing_file = repo.get_contents(EXCEL_FILENAME)
            repo.update_file(
                path=EXCEL_FILENAME,
                message=f"Update fitness data",
                content=encoded,
                sha=existing_file.sha,
            )
        except Exception:
            # File doesn't exist, create it
            repo.create_file(
                path=EXCEL_FILENAME,
                message="Create fitness data file",
                content=encoded,
            )
        return True

    except Exception as e:
        st.error(f"❌ Error saving data: {e}")
        return False

def append_and_save(new_rows: list):
    """
    Append new rows to existing data and save back to GitHub.
    new_rows: list of dicts with keys matching column names.
    """
    df_existing = load_data_from_github()
    df_new = pd.DataFrame(new_rows)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    success = save_data_to_github(df_combined)
    return success, df_combined

def get_empty_dataframe():
    """Return an empty DataFrame with correct columns."""
    return pd.DataFrame(columns=[
        "Date",
        "Mode",          # Full Body / Abs / Rest
        "Exercise",      # Exercise name
        "Set_Number",    # 1, 2, 3...
        "Reps",          # Number of reps (0 for timed exercises)
        "Duration_Minutes",  # For walking and timed holds
        "Distance_KM",   # For walking only
        "Notes",         # Any extra info
    ])

def delete_todays_rest_day(date_today):
    """Remove rest day entry for today (if user changes mind)."""
    df = load_data_from_github()
    df = df[~((df["Date"] == date_today) & (df["Exercise"] == "Rest Day"))]
    save_data_to_github(df)
    return df
