import pandas as pd


def load_carriers():
    carriers = pd.read_csv("src/data/carriers.csv")
    return carriers


def find_matching_idle_fleet(cold_chain, cargo_weight, origin):
    fleet = load_fleet()

    available_fleet = fleet[fleet["status"] == "Available"]

    if cold_chain == "Yes":
        available_fleet = available_fleet[
            available_fleet["type"] == "Refrigerated Truck"
        ]

    available_fleet = available_fleet[
        available_fleet["capacity_kg"] >= cargo_weight
    ]

    # First prefer vehicles located at the shipment's origin.
    origin_fleet = available_fleet[
        available_fleet["location"] == origin
    ]

    if not origin_fleet.empty:
        return origin_fleet

    # If no suitable vehicle is available at the origin,
    # allow a suitable vehicle from another location.
    return available_fleet


def load_shipments():
    shipments = pd.read_csv("src/data/shipments.csv")
    return shipments


def load_disruptions():
    disruptions = pd.read_csv("src/data/disruptions.csv")
    return disruptions


def load_fleet():
    fleet = pd.read_csv("src/data/fleet.csv")
    return fleet


def load_temperature_readings():
    readings = pd.read_csv("src/data/temperature_readings.csv")
    return readings


def find_affected_shipments():
    """Return a list of (shipment, disruption) tuples for affected shipments.

    A disruption must affect the shipment's origin. If it also mentions
    the destination, it is treated as a more specific route disruption.
    """
    shipments = load_shipments()
    disruptions = load_disruptions()

    active_disruptions = disruptions[
        disruptions["status"] == "Active"
    ]

    affected = []

    for _, shipment in shipments.iterrows():

        best_score = 0
        best_disruption = None

        for _, disruption in active_disruptions.iterrows():

            # The disruption must involve the shipment's origin.
            if shipment["origin"] not in disruption["location"]:
                continue

            score = 1

            # A destination match makes this a route-specific disruption.
            if shipment["destination"] in disruption["location"]:
                score += 2

            # Keep the highest-scoring disruption.
            # If scores tie, the first disruption remains selected.
            if score > best_score:
                best_score = score
                best_disruption = disruption

        if best_disruption is not None:
            affected.append((shipment, best_disruption))

    return affected

def find_idle_fleet():
    fleet = load_fleet()

    idle_fleet = fleet[fleet["status"] == "Available"]

    return idle_fleet


def find_temperature_excursions():
    readings = load_temperature_readings()

    excursions = readings[readings["temperature_celsius"] > 8].copy()

    excursions["severity"] = excursions["temperature_celsius"].apply(
        lambda temperature: "Severe" if temperature > 10 else "Moderate"
    )

    excursions["risk_message"] = excursions["severity"].apply(
        lambda severity:
        "Immediate cold-chain attention required"
        if severity == "Severe"
        else
        "Monitor shipment and inspect refrigeration"
    )

    return excursions


def suggest_alternatives():
    affected_pairs = find_affected_shipments()
    carriers = load_carriers()
    excursions = find_temperature_excursions()

    refrigerated_carriers = carriers[
        carriers["refrigerated_support"] == "Yes"
    ]

    recommendations = []
    used_vehicles = set()

    for shipment, disruption in affected_pairs:

        idle_fleet = find_matching_idle_fleet(
            shipment["cold_chain"],
            shipment["cargo_weight_kg"],
            shipment["origin"]
        )

        idle_fleet = idle_fleet[
            ~idle_fleet["vehicle_id"].isin(used_vehicles)
        ]

        if idle_fleet.empty:
            suggested_vehicle = "No suitable vehicle available"
            vehicle_capacity = None
        else:
            selected_vehicle = idle_fleet.iloc[0]

            suggested_vehicle = selected_vehicle["vehicle_id"]
            vehicle_capacity = int(selected_vehicle["capacity_kg"])

            used_vehicles.add(suggested_vehicle)

        # Select suitable carriers
        if shipment["cold_chain"] == "Yes":
            available_carriers = refrigerated_carriers[
                (refrigerated_carriers["available"] == "Yes") &
                (refrigerated_carriers["carrier"] != shipment["carrier"])
            ]

        else:
            available_carriers = carriers[
                (carriers["available"] == "Yes") &
                (carriers["carrier"] != shipment["carrier"])
            ]

        # Prefer a carrier whose preferred route matches the shipment route
        route = shipment["origin"] + "-" + shipment["destination"]

        preferred_carriers = available_carriers[
            available_carriers["preferred_route"] == route
        ]

        if not preferred_carriers.empty:
            available_carriers = preferred_carriers

        # Select carrier
        if available_carriers.empty:
            suggested_carrier = "No suitable carrier available"
        else:
            suggested_carrier = available_carriers["carrier"].iloc[0]

        # Select alternative route
        disruption_description = disruption["description"]

        if shipment["destination"] == "Ahmedabad":

            suggested_route = (
                shipment["origin"] + " → Vadodara → Ahmedabad"
            )

        elif shipment["destination"] == "Delhi":

            suggested_route = (
                shipment["origin"] + " → Jaipur → Delhi"
            )

        elif shipment["destination"] == "Jaipur":

            suggested_route = (
                shipment["origin"] + " → Udaipur → Jaipur"
            )

        

        else:

            suggested_route = (
                shipment["origin"]
                + " → "
                + shipment["destination"]
                + " — verify alternative route with carrier"
            )

        reason = disruption_description

        shipment_excursions = excursions[
            excursions["shipment_id"] == shipment["shipment_id"]
            ]

        if shipment_excursions.empty:
            additional_risk = None
            urgent = False
        else:
            highest_temperature = shipment_excursions[
                "temperature_celsius"
            ].max()

            additional_risk = (
                f"Cold-chain temperature excursion detected: "
                f"{highest_temperature}°C"
            )

            urgent = True

        recommendation = {
            "shipment_id": shipment["shipment_id"],
            "current_carrier": shipment["carrier"],
            "suggested_vehicle": suggested_vehicle,
            "suggested_vehicle_capacity": vehicle_capacity,
            "suggested_carrier": suggested_carrier,
            "suggested_route": suggested_route,
            "reason": reason,
            "additional_risk": additional_risk,
            "urgent": urgent
        }

        # Add every recommendation to the result
        recommendations.append(recommendation)

    return recommendations


def build_summary_prompt() -> str:
    """Assemble a concise operational briefing prompt from live data and return
    it as a string suitable for passing to an LLM.  All numbers and facts are
    derived from the current CSV data — nothing is hardcoded here."""

    affected_pairs = find_affected_shipments()
    excursions = find_temperature_excursions()
    recommendations = suggest_alternatives()
    disruptions = load_disruptions()

    active_disruptions = disruptions[disruptions["status"] == "Active"]

    # ── Disruption summary ────────────────────────────────────────────────────
    disruption_lines = []
    for _, d in active_disruptions.iterrows():
        disruption_lines.append(
            f"- {d['disruption_id']} ({d['type']}) at {d['location']}: {d['description']}"
        )
    disruption_text = "\n".join(disruption_lines) if disruption_lines else "None"

    # ── Affected shipments ────────────────────────────────────────────────────
    shipment_lines = []
    for shipment, disruption in affected_pairs:
        shipment_lines.append(
            f"- {shipment['shipment_id']}: {shipment['origin']} to {shipment['destination']}"
            f" (carrier: {shipment['carrier']}, priority: {shipment['priority']})"
        )
    shipment_text = "\n".join(shipment_lines) if shipment_lines else "None"

    # ── Temperature excursions ────────────────────────────────────────────────
    excursion_lines = []
    for _, exc in excursions.iterrows():
        excursion_lines.append(
            f"- {exc['shipment_id']}: {exc['temperature_celsius']}C ({exc['severity']}) — {exc['risk_message']}"
        )
    excursion_text = "\n".join(excursion_lines) if excursion_lines else "None"

    # ── Top recommendation ────────────────────────────────────────────────────
    if recommendations:
        top = recommendations[0]
        top_rec_text = (
            f"Reroute {top['shipment_id']} via {top['suggested_route']},"
            f" assign vehicle {top['suggested_vehicle']},"
            f" switch carrier to {top['suggested_carrier']}."
        )
    else:
        top_rec_text = "No recommendations at this time."

    prompt = f"""You are an operations assistant for a supply chain logistics company.
Below is the current situation. Write a concise plain-English briefing (3-5 sentences) for an
operations manager. State the number of affected shipments, the active disruptions, any
cold-chain risks, and the single most urgent recommended action. Be factual and direct.

ACTIVE DISRUPTIONS:
{disruption_text}

AFFECTED SHIPMENTS ({len(affected_pairs)} total):
{shipment_text}

COLD-CHAIN TEMPERATURE ALERTS ({len(excursions)} total):
{excursion_text}

TOP RECOMMENDED ACTION:
{top_rec_text}

Briefing:"""

    return prompt
