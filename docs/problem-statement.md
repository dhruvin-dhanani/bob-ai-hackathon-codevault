# Problem Statement

## Background

Modern logistics operations depend on multiple carriers, vehicles, routes, ports, highways, and temperature-sensitive shipments. When a disruption occurs, operations teams must quickly understand which shipments are affected, which vehicles are available, whether alternative carriers can handle the shipment, and whether cold-chain cargo is at risk.

These decisions become more difficult when operational information is spread across shipment records, fleet records, disruption reports, carrier capabilities, and IoT temperature readings.

## The Problem

When a port closure, road blockage, carrier disruption, or other operational incident occurs, logistics teams need to identify affected shipments and determine practical alternatives quickly.

For cold-chain shipments, the situation is more urgent because a temperature excursion above the acceptable range can increase cargo risk.

At the same time, available vehicles may remain underutilised while affected shipments require additional capacity. Without a unified view, teams may spend valuable time manually comparing shipment requirements, vehicle capacity, carrier capabilities, routes, and temperature data.

Our project addresses this problem by bringing these signals together and generating actionable disruption and fleet-utilisation recommendations.

## Who is Affected

The primary users are:

* Logistics operations teams monitoring shipments and disruptions
* Fleet managers responsible for vehicle utilisation
* Supply-chain coordinators handling rerouting decisions
* Cold-chain operators responsible for temperature-sensitive cargo

These users need a fast operational view rather than having to inspect multiple datasets separately during a disruption.

## Why It Matters

A disruption can affect multiple shipments simultaneously. Delayed decisions can increase delivery delays, leave available fleet capacity unused, and create additional risk for temperature-sensitive cargo.

Cold-chain excursions are particularly important because the shipment may require urgent intervention when temperatures move outside the expected operating range.

The operational challenge is therefore not only detecting that a disruption exists, but connecting the disruption to affected shipments, available resources, carrier capabilities, and cargo risk.

## Why Existing Solutions Fall Short

Traditional logistics workflows often rely on separate transportation-management systems, spreadsheets, carrier portals, fleet records, and monitoring systems. These tools may provide individual pieces of information but do not necessarily provide one simple operational view connecting disruption impact, fleet availability, carrier alternatives, routing suggestions, and cold-chain risk.

Manual comparison across these sources can slow down response during time-sensitive incidents.

Our prototype addresses this gap by combining shipment, disruption, fleet, carrier, and temperature data into a single dashboard and producing recommendations that connect the available information into an actionable response.
