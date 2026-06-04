from fastapi import FastAPI
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

@app.post("/check-availability")
def check_availability(data: dict):

    sport = data["sport"]
    date = data["date"]

    result = (
        supabase
        .table("available_slots")
        .select("*")
        .eq("sport", sport)
        .eq("slot_date", date)
        .execute()
    )

    return result.data

