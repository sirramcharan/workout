# github_utils.py

import base64
import io
import pandas as pd
from github import Github
import streamlit as st

EXCEL_FILENAME = "fitness_data.xlsx"

# ─────────────────────────────────────────────
# CONNECTION
# ─────────────────────────────────────────────
def get_github_repo():
    try:
        g    = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["GITHUB_REPO"])
        return repo
    except Exception as e:
        st.error(f"❌ GitHub connection failed: {e}")
        return None

# ─────────────────────────────────────────────
# CORE: GET RAW BYTES FROM GITHUB
# ─────────────────────────────────────────────
def _get_file_bytes(repo):
    """
    Safely fetch raw bytes of the Excel file from GitHub.
    Uses decoded_content which handles chunked base64 properly.
    Returns (bytes, sha) or (None, None)
    """
    try:
        file_content = repo.get_contents(EXCEL_FILENAME)

        # ✅ Use decoded_content instead of manual base64 decode
        # PyGithub handles chunked content automatically this way
        raw_bytes = file_content.decoded_content
        sha       = file_content.sha
        return raw_bytes, sha

    except Exception as e:
        if "404" in str(e):
            return None, None   # File doesn't exist yet
        raise e

# ─────────────────────────────────────────────
# CREATE VALID EMPTY EXCEL BYTES
# ─────────────────────────────────────────────
def _make_empty_excel_bytes():
    """Create a valid .xlsx file in memory with correct headers."""
    df     = get_empty_dataframe()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="WorkoutLog")
    output.seek(0)
    return output.read()

# ─────────────────────────────────────────────
def load_data_from_github():
    repo = get_github_repo()
    if repo is None:
        return get_empty_dataframe()

    try:
        raw_bytes, sha = _get_file_bytes(repo)

        # ── TEMPORARY DEBUG — remove after fixing ──
        if raw_bytes is not None:
            st.write(f"📦 File size: {len(raw_bytes)} bytes")
            st.write(f"📦 SHA: {sha}")
            st.write(f"📦 First 10 bytes: {raw_bytes[:10]}")
        else:
            st.write("📦 raw_bytes is None — file not found")
        # ── END DEBUG ──

        # ── File doesn't exist → create it ──
        if raw_bytes is None:
            st.info("📁 No data file found. Creating one now...")
            _create_fresh_file(repo)
            return get_empty_dataframe()

        # ── File is too small to be valid ──
        if len(raw_bytes) < 200:
            st.info("📁 Data file was empty. Initializing now...")
            _overwrite_file(repo, sha)
            return get_empty_dataframe()

        # ── Try to read it ──
        try:
            df = pd.read_excel(
                io.BytesIO(raw_bytes),
                engine     = "openpyxl",
                sheet_name = "WorkoutLog",
            )
        except Exception as read_err:
            # ── TEMPORARY DEBUG ──
            st.write(f"📦 Read error: {read_err}")
            # ── END DEBUG ──
            st.info("📁 Reinitializing data file...")
            _overwrite_file(repo, sha)
            return get_empty_dataframe()

        if df.empty:
            return get_empty_dataframe()

        df["Date"]             = pd.to_datetime(df["Date"], errors="coerce").dt.date
        df["Reps"]             = pd.to_numeric(df["Reps"],             errors="coerce").fillna(0).astype(int)
        df["Duration_Minutes"] = pd.to_numeric(df["Duration_Minutes"], errors="coerce").fillna(0).astype(float)
        df["Distance_KM"]      = pd.to_numeric(df["Distance_KM"],      errors="coerce").fillna(0).astype(float)
        df["Set_Number"]       = pd.to_numeric(df["Set_Number"],       errors="coerce").fillna(0).astype(int)
        df["Notes"]            = df["Notes"].fillna("")

        return df

    except Exception as e:
        st.error(f"❌ Unexpected error loading data: {e}")
        return get_empty_dataframe()

# ─────────────────────────────────────────────
def load_data_from_github():
    """Load Excel file from GitHub and return as DataFrame."""
    repo = get_github_repo()
    if repo is None:
        return get_empty_dataframe()

    try:
        raw_bytes, sha = _get_file_bytes(repo)

        # ── File doesn't exist → create it ──
        if raw_bytes is None:
            st.info("📁 No data file found. Creating one now...")
            _create_fresh_file(repo)
            return get_empty_dataframe()

        # ── File is too small to be valid ──
        if len(raw_bytes) < 200:
            st.info("📁 Data file was empty. Initializing now...")
            _overwrite_file(repo, sha)
            return get_empty_dataframe()

        # ── Try to read it ──
        try:
            df = pd.read_excel(
                io.BytesIO(raw_bytes),
                engine      = "openpyxl",
                sheet_name  = "WorkoutLog",
            )
        except Exception:
            # Last resort — file truly corrupted, overwrite
            st.info("📁 Reinitializing data file...")
            _overwrite_file(repo, sha)
            return get_empty_dataframe()

        # ── Ensure correct dtypes ──
        if df.empty:
            return get_empty_dataframe()

        df["Date"]             = pd.to_datetime(df["Date"], errors="coerce").dt.date
        df["Reps"]             = pd.to_numeric(df["Reps"],             errors="coerce").fillna(0).astype(int)
        df["Duration_Minutes"] = pd.to_numeric(df["Duration_Minutes"], errors="coerce").fillna(0).astype(float)
        df["Distance_KM"]      = pd.to_numeric(df["Distance_KM"],      errors="coerce").fillna(0).astype(float)
        df["Set_Number"]       = pd.to_numeric(df["Set_Number"],       errors="coerce").fillna(0).astype(int)
        df["Notes"]            = df["Notes"].fillna("")

        return df

    except Exception as e:
        st.error(f"❌ Unexpected error loading data: {e}")
        return get_empty_dataframe()

# ─────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────
def save_data_to_github(df):
    """Save DataFrame as Excel to GitHub."""
    repo = get_github_repo()
    if repo is None:
        return False

    try:
        # Build Excel bytes
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="WorkoutLog")
        output.seek(0)
        excel_bytes = output.read()
        encoded     = base64.b64encode(excel_bytes).decode("utf-8")

        # Try to get existing SHA
        try:
            existing   = repo.get_contents(EXCEL_FILENAME)
            repo.update_file(
                path    = EXCEL_FILENAME,
                message = "Update fitness data",
                content = encoded,
                sha     = existing.sha,
            )
        except Exception:
            # File not found → create fresh
            repo.create_file(
                path    = EXCEL_FILENAME,
                message = "Initialize fitness data",
                content = encoded,
            )

        return True

    except Exception as e:
        st.error(f"❌ Error saving data: {e}")
        return False

# ─────────────────────────────────────────────
# INTERNAL HELPERS
# ─────────────────────────────────────────────
def _create_fresh_file(repo):
    """Create a brand new valid Excel file on GitHub."""
    try:
        excel_bytes = _make_empty_excel_bytes()
        encoded     = base64.b64encode(excel_bytes).decode("utf-8")
        repo.create_file(
            path    = EXCEL_FILENAME,
            message = "Initialize fitness data",
            content = encoded,
        )
    except Exception as e:
        st.error(f"❌ Could not create data file: {e}")

def _overwrite_file(repo, sha):
    """Overwrite corrupted file with a valid empty one."""
    try:
        excel_bytes = _make_empty_excel_bytes()
        encoded     = base64.b64encode(excel_bytes).decode("utf-8")
        if sha:
            repo.update_file(
                path    = EXCEL_FILENAME,
                message = "Reinitialize fitness data",
                content = encoded,
                sha     = sha,
            )
        else:
            repo.create_file(
                path    = EXCEL_FILENAME,
                message = "Reinitialize fitness data",
                content = encoded,
            )
    except Exception as e:
        st.error(f"❌ Could not reinitialize data file: {e}")

# ─────────────────────────────────────────────
# APPEND & SAVE
# ─────────────────────────────────────────────
def append_and_save(new_rows: list):
    """
    Append new rows to existing data and save back to GitHub.
    new_rows : list of dicts matching column names.
    """
    df_existing = load_data_from_github()
    df_new      = pd.DataFrame(new_rows)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    success     = save_data_to_github(df_combined)
    return success, df_combined

# ─────────────────────────────────────────────
# EMPTY DATAFRAME SCHEMA
# ─────────────────────────────────────────────
def get_empty_dataframe():
    """Return an empty DataFrame with correct columns."""
    return pd.DataFrame(columns=[
        "Date",
        "Mode",
        "Exercise",
        "Set_Number",
        "Reps",
        "Duration_Minutes",
        "Distance_KM",
        "Notes",
    ])

# ─────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────
def delete_todays_rest_day(date_today):
    """Remove rest day entry for today."""
    df = load_data_from_github()
    df = df[~((df["Date"] == date_today) & (df["Exercise"] == "Rest Day"))]
    save_data_to_github(df)
    return df
