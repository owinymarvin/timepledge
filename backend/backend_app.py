from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import LoanSchema, AdvanceSchema
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import base64
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://frontend:8501"],  # Allow both localhost and frontend service
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOAN_STORAGE_DIR = Path("data/loan_data")
LOAN_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

ADVANCE_STORAGE_DIR = Path("data/advance_data")
ADVANCE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

PLOT_STORAGE_DIR = Path("data/plots")
PLOT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
def home():
    return "use the endpoint \n /calculate_loan \n /calculate_advance \n /plot_loan/{username}"

def update_user_file(directory: Path, username: str, result: dict, file_type: str):
    filename = directory / f"{file_type}_{username}.json"
    data = []
    if filename.exists():
        with open(filename, "r") as f:
            data = json.load(f)
    # Remove schedule_df to avoid serialization issues
    result_copy = result.copy()
    result_copy.pop("schedule_df", None)
    data.append(result_copy)
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

@app.post("/calculate_loan")
def calculate_loan(payload: LoanSchema):
    result = payload.compute_loan()
    # Remove schedule_df from response to avoid serialization issues
    result_copy = result.copy()
    result_copy.pop("schedule_df", None)
    update_user_file(LOAN_STORAGE_DIR, payload.username, result, "loans")
    return result_copy

@app.post("/calculate_advance")
def calculate_advance(payload: AdvanceSchema):
    result = payload.compute_advance()
    update_user_file(ADVANCE_STORAGE_DIR, payload.username, result, "advances")
    return result

@app.get("/user_loans/{username}")
def get_user_loans(username: str):
    filename = LOAN_STORAGE_DIR / f"loans_{username}.json"
    if filename.exists():
        with open(filename, "r") as f:
            return json.load(f)
    return []

@app.get("/user_advances/{username}")
def get_user_advances(username: str):
    filename = ADVANCE_STORAGE_DIR / f"advances_{username}.json"
    if filename.exists():
        with open(filename, "r") as f:
            return json.load(f)
    return []

@app.get("/plot_loan/{username}")
def plot_loan(username: str):
    filename = LOAN_STORAGE_DIR / f"loans_{username}.json"
    if not filename.exists():
        return {"error": f"No loans found for user {username}"}

    with open(filename, "r") as f:
        loans = json.load(f)
    
    if not loans:
        return {"error": f"No loans found for user {username}"}

    # Get the latest loan
    latest_loan = loans[-1]
    if not latest_loan.get("eligible", False):
        return {"error": "Latest loan is not eligible"}

    # Create DataFrame from repayment schedule
    df = pd.DataFrame(latest_loan["repayment_schedule"])

    plt.figure(figsize=(10, 6))
    plt.bar(df["month"], df["principal_component"], label="Principal", color="blue")
    plt.bar(df["month"], df["interest_component"], bottom=df["principal_component"], label="Interest", color="orange")
    plt.xlabel("Month")
    plt.ylabel("Amount ($)")
    plt.title(f"Loan Repayment Schedule for {username}")
    plt.legend()
    plt.grid(True, axis="y")

    plot_filename = PLOT_STORAGE_DIR / f"loan_plot_{username}.png"
    plt.savefig(plot_filename, format="png", bbox_inches="tight")
    plt.close()

    # Read and encode the image as base64
    with open(plot_filename, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    os.remove(plot_filename)

    return {
        "username": username,
        "plot": f"data:image/png;base64,{encoded_image}"
    }
