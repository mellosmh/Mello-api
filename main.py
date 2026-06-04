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


@app.get("/")
def health():
    return {"status": "running"}


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


@app.post("/create-booking")
def create_booking(data: dict):

    customer_name = data["customer_name"]
    phone_number = data["phone_number"]
    sport = data["sport"]
    booking_date = data["booking_date"]
    booking_time = data["booking_time"]

    slot = (
        supabase
        .table("slots")
        .select("*")
        .eq("slot_date", booking_date)
        .eq("start_time", booking_time)
        .eq("is_booked", False)
        .execute()
    )

    if not slot.data:
        return {
            "success": False,
            "message": "Slot not available"
        }

    slot_info = slot.data[0]

    court = (

        supabase
        .table("courts")
        .select("*")
        .eq("id", slot_info["court_id"])
        .eq("sport", sport)
        .execute()
    )

    if not court.data:
        return {
            "success": False,
            "message": "No matching court found"
        }

    member = (
        supabase
        .table("members")
        .select("id")
        .eq("phone_number", phone_number)
        .execute()
    )

    member_id = None

    if member.data:
        member_id = member.data[0]["id"]

    booking = (
        supabase
        .table("bookings")
        .insert({
            "customer_name": customer_name,
            "phone_number": phone_number,
            "sport": sport,
            "booking_date": booking_date,
            "booking_time": booking_time,
            "status": "confirmed",
            "court_id": slot_info["court_id"],
            "slot_id": slot_info["id"],
            "member_id": member_id
        })
        .execute()
    )

    (
        supabase
        .table("slots")
        .update({"is_booked": True})
        .eq("id", slot_info["id"])
        .execute()
    )

    return {
        "success": True,
        "booking_id": booking.data[0]["id"],
        "message": "Booking confirmed"
    }

