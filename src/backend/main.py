from dotenv import load_dotenv

load_dotenv("src/.env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.analysis import (
    find_affected_shipments,
    find_idle_fleet,
    find_temperature_excursions,
    suggest_alternatives,
    build_summary_prompt,
)
from src.backend.watsonx_client import generate_summary

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Supply Chain Disruption Assistant is running!"}


@app.get("/affected-shipments")
def affected_shipments():
    shipments = find_affected_shipments()

    return [shipment.to_dict() for shipment, _ in shipments]


@app.get("/idle-fleet")
def idle_fleet():
    fleet = find_idle_fleet()

    return fleet.to_dict(orient="records")


@app.get("/temperature-excursions")
def temperature_excursions():
    excursions = find_temperature_excursions()

    return excursions.to_dict(orient="records")


@app.get("/recommendations")
def recommendations():
    return suggest_alternatives()


@app.get("/situation-summary")
def situation_summary():
    prompt = build_summary_prompt()
    summary = generate_summary(prompt)
    return {"summary": summary}