# Solution Overview

## What We Built

We built a Supply Chain Disruption Assistant & Fleet Utilisation Optimizer that gives logistics teams a single operational view of shipment disruptions, available fleet, cold-chain temperature risks, and alternative transport options.

The system combines shipment, disruption, fleet, carrier, and temperature data to identify affected shipments and generate practical recommendations.

For cold-chain shipments, the system also detects temperature excursions and marks urgent cases where cargo may require immediate attention.

An optional IBM watsonx.ai integration can generate a concise situation summary from the current operational data.

## How It Works

1. The system loads shipment, disruption, fleet, carrier, and temperature data from CSV datasets.

2. Active disruptions are compared with shipment origins and destinations to identify potentially affected shipments.

3. Available vehicles are analysed based on location, capacity, and cold-chain requirements.

4. Temperature readings above 8°C are detected as cold-chain excursions and assigned a severity level.

5. The recommendation engine evaluates suitable alternative carriers, vehicles, and routes while considering shipment requirements.

6. The results are exposed through a FastAPI backend.

7. The frontend dashboard fetches the results and presents affected shipments, idle fleet, temperature risks, recommendations, and the situation summary.

8. When valid watsonx.ai credentials are configured, the current operational information is sent to IBM watsonx.ai to generate an AI-assisted situation summary.

## Architecture Diagram

See [`architecture.md`](architecture.md) for the detailed architecture diagram.

A simplified view of the current prototype is:

```text
                    ┌──────────────────────┐
                    │   CSV Data Sources   │
                    │ Shipments / Fleet    │
                    │ Disruptions / IoT    │
                    │ Carriers             │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Analysis Engine    │
                    │ Disruption Detection │
                    │ Fleet Matching       │
                    │ Temperature Risk     │
                    │ Recommendations      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   FastAPI Backend    │
                    │       / API          │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴───────────┐
                    │                      │
                    ▼                      ▼
          ┌─────────────────┐    ┌──────────────────┐
          │ Web Dashboard   │    │ IBM watsonx.ai   │
          │ HTML/CSS/JS     │    │ AI Summary       │
          └─────────────────┘    └──────────────────┘
```

## Key Design Decisions

| Decision                                                                    | Rationale                                                                                                                                          |
| --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Used a rule-based analysis engine                                           | The prototype needs deterministic and explainable disruption, fleet, and temperature decisions.                                                    |
| Used CSV datasets                                                           | CSV data keeps the prototype simple, reproducible, and easy to run without requiring a database server.                                            |
| Added fleet matching based on capacity, location, and cold-chain capability | Recommendations should consider the actual requirements of the affected shipment rather than simply selecting any available vehicle.               |
| Added temperature excursion detection                                       | Cold-chain cargo can require faster intervention when temperatures exceed the expected 2°C–8°C range.                                              |
| Added alternative carrier and route recommendations                         | The system should provide an actionable response instead of only reporting that a disruption exists.                                               |
| Used IBM watsonx.ai for the situation summary                               | The AI layer converts the current operational signals into a concise human-readable briefing while the core detection logic remains deterministic. |
| Added automated tests                                                       | The analysis engine contains multiple decision rules, so automated tests help verify that changes do not break existing behaviour.                 |

## IBM Technologies Used

### IBM watsonx.ai

IBM watsonx.ai is integrated into the backend through the IBM watsonx.ai Python SDK.

The application builds a factual situation-summary prompt from the current shipment, disruption, fleet, and temperature analysis. When valid watsonx.ai credentials are configured, the backend uses the `ibm/granite-3-8b-instruct` model to generate a concise operational briefing.

The integration is implemented in:

```text
src/backend/watsonx_client.py
```

The core dashboard does not depend on the AI service being available. If watsonx.ai is not configured or the request fails, the application returns a clear fallback message while the deterministic dashboard features continue working.

### IBM Bob

IBM Bob was used as an AI coding agent during development of the project.

Bob was used to inspect the repository, reason about the analysis implementation, and create the automated test suite for the core analysis engine.

The resulting `tests/test_analysis.py` contains 45 automated tests covering disruption detection, idle fleet, temperature excursions, recommendations, and data integrity.

This demonstrates IBM Bob as part of the actual software-development workflow rather than simply mentioning it in the documentation.
