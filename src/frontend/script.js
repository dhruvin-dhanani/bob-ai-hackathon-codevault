
async function loadDashboardData() {

    // ── Situation Summary ─────────────────────────────────────────────────────
    const summaryText = document.getElementById("situation-summary-text");
    summaryText.textContent = "Loading situation summary...";

    try {
        const summaryResponse = await fetch("http://127.0.0.1:8000/situation-summary");
        const summaryData = await summaryResponse.json();

        summaryText.textContent = summaryData.summary;
    } catch (e) {
        summaryText.textContent = "Failed to load situation summary — is the backend running?";
        summaryText.classList.add("section-error");
    }


    // ── Affected Shipments ────────────────────────────────────────────────────
    try {
        const affectedResponse = await fetch("http://127.0.0.1:8000/affected-shipments");
        const affectedShipments = await affectedResponse.json();

        document.getElementById("affected-count").textContent = affectedShipments.length;

        const affectedList = document.getElementById("affected-list");
        affectedList.innerHTML = "";

        affectedShipments.forEach(shipment => {
            const item = document.createElement("p");

            item.textContent =
                shipment.shipment_id +
                " — " +
                shipment.origin +
                " → " +
                shipment.destination;

            affectedList.appendChild(item);
        });
    } catch (e) {
        document.getElementById("affected-count").textContent = "—";

        const affectedList = document.getElementById("affected-list");
        affectedList.innerHTML = "";

        const error = document.createElement("p");
        error.className = "section-error";
        error.textContent = "Failed to load — is the backend running?";
        affectedList.appendChild(error);
    }


    // ── Idle Fleet ────────────────────────────────────────────────────────────
    try {
        const fleetResponse = await fetch("http://127.0.0.1:8000/idle-fleet");
        const idleFleet = await fleetResponse.json();

        document.getElementById("idle-count").textContent = idleFleet.length;

        const idleList = document.getElementById("idle-list");
        idleList.innerHTML = "";

        idleFleet.forEach(vehicle => {
            const item = document.createElement("p");

            item.textContent =
                vehicle.vehicle_id +
                " — " +
                vehicle.type +
                " — " +
                vehicle.location;

            idleList.appendChild(item);
        });
    } catch (e) {
        document.getElementById("idle-count").textContent = "—";

        const idleList = document.getElementById("idle-list");
        idleList.innerHTML = "";

        const error = document.createElement("p");
        error.className = "section-error";
        error.textContent = "Failed to load — is the backend running?";
        idleList.appendChild(error);
    }


    // ── Temperature Excursions ────────────────────────────────────────────────
    try {
        const temperatureResponse = await fetch("http://127.0.0.1:8000/temperature-excursions");
        const temperatureExcursions = await temperatureResponse.json();

        document.getElementById("temperature-count").textContent = temperatureExcursions.length;

        const temperatureList = document.getElementById("temperature-list");
        temperatureList.innerHTML = "";

        temperatureExcursions.forEach(excursion => {
            const item = document.createElement("p");

            item.textContent =
                excursion.shipment_id +
                " — " +
                excursion.temperature_celsius +
                "\u00b0C — " +
                excursion.severity +
                " — " +
                excursion.risk_message;

            if (excursion.severity === "Severe") {
                item.classList.add("severity-severe");
            } else if (excursion.severity === "Moderate") {
                item.classList.add("severity-moderate");
            }

            temperatureList.appendChild(item);
        });
    } catch (e) {
        document.getElementById("temperature-count").textContent = "—";

        const temperatureList = document.getElementById("temperature-list");
        temperatureList.innerHTML = "";

        const error = document.createElement("p");
        error.className = "section-error";
        error.textContent = "Failed to load — is the backend running?";
        temperatureList.appendChild(error);
    }


    // ── Recommendations ───────────────────────────────────────────────────────
    try {
        const recommendationsResponse = await fetch("http://127.0.0.1:8000/recommendations");
        const recommendations = await recommendationsResponse.json();

        const recommendationsList = document.getElementById("recommendations-list");
        recommendationsList.innerHTML = "";

        recommendations.forEach(recommendation => {
            const item = document.createElement("div");
            item.className = "recommendation-card";

            // Mark urgent recommendations visually
            if (recommendation.urgent) {
                item.classList.add("recommendation-urgent");
            }

            const title = document.createElement("strong");
            title.textContent = recommendation.shipment_id;
            item.appendChild(title);

            const fields = [
                ["Current carrier", recommendation.current_carrier],
                ["Suggested carrier", recommendation.suggested_carrier],
                ["Suggested vehicle", recommendation.suggested_vehicle],
                [
                    "Suggested vehicle capacity",
                    recommendation.suggested_vehicle_capacity !== null
                        ? recommendation.suggested_vehicle_capacity + " kg"
                        : "N/A"
                ],
                ["Suggested route", recommendation.suggested_route],
                ["Reason", recommendation.reason],
            ];

            fields.forEach(([label, value]) => {
                const line = document.createElement("p");

                line.style.margin = "4px 0";
                line.style.padding = "0";
                line.style.background = "none";

                const labelSpan = document.createElement("span");

                labelSpan.style.color = "#57606a";
                labelSpan.textContent = label + ": ";

                const valueSpan = document.createElement("span");

                valueSpan.textContent = value;

                line.appendChild(labelSpan);
                line.appendChild(valueSpan);

                item.appendChild(line);
            });

            // Display cold-chain warning when present
            if (recommendation.additional_risk) {
                const riskLine = document.createElement("p");

                riskLine.style.margin = "8px 0 4px 0";
                riskLine.style.padding = "8px";
                riskLine.style.background = "#fff3cd";
                riskLine.style.borderRadius = "5px";
                riskLine.style.fontWeight = "bold";

                riskLine.textContent =
                    "Cold-chain risk: " + recommendation.additional_risk;

                item.appendChild(riskLine);
            }

            // Display urgent status when required
            if (recommendation.urgent) {
                const urgentLine = document.createElement("p");

                urgentLine.style.margin = "4px 0";
                urgentLine.style.padding = "0";
                urgentLine.style.background = "none";
                urgentLine.style.fontWeight = "bold";

                urgentLine.textContent =
                    "URGENT: Immediate attention required";

                item.appendChild(urgentLine);
            }

            recommendationsList.appendChild(item);
        });
    } catch (e) {
        const recommendationsList = document.getElementById("recommendations-list");
        recommendationsList.innerHTML = "";

        const error = document.createElement("p");
        error.className = "section-error";
        error.textContent = "Failed to load — is the backend running?";
        recommendationsList.appendChild(error);
    }
}


// Load dashboard when page opens
loadDashboardData();


// Refresh dashboard when Refresh button is clicked
document.getElementById("refresh-btn").addEventListener("click", loadDashboardData);

