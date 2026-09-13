"""
tests/test_analysis.py

Automated tests for src/backend/analysis.py.

Run from the repo root with:
    python -m unittest tests/test_analysis.py -v

All tests use the real CSV files in src/data/ — no mocking, no fixtures.
The test suite is intentionally read-only: it never modifies CSV data or
application files.
"""

import unittest

from src.backend.analysis import (
    find_affected_shipments,
    find_idle_fleet,
    find_matching_idle_fleet,
    find_temperature_excursions,
    suggest_alternatives,
    load_disruptions,
    load_fleet,
    load_shipments,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _affected_map():
    """Return {shipment_id: disruption_id} for every affected shipment."""
    return {
        s["shipment_id"]: d["disruption_id"]
        for s, d in find_affected_shipments()
    }


def _rec_map():
    """Return {shipment_id: recommendation_dict} for all recommendations."""
    return {r["shipment_id"]: r for r in suggest_alternatives()}


# ══════════════════════════════════════════════════════════════════════════════
# 1. Disruption detection
# ══════════════════════════════════════════════════════════════════════════════

class TestDisruptionDetection(unittest.TestCase):

    def test_only_active_disruptions_are_considered(self):
        """Resolved disruptions must never appear as the matched disruption."""
        disruptions = load_disruptions()
        resolved_ids = set(
            disruptions[disruptions["status"] == "Resolved"]["disruption_id"]
        )

        for _, disruption in find_affected_shipments():
            self.assertNotIn(
                disruption["disruption_id"],
                resolved_ids,
                f"Resolved disruption {disruption['disruption_id']} was matched "
                "to a shipment — only Active disruptions should match.",
            )

    def test_affected_shipments_returns_tuples(self):
        """Each item must be a (shipment_row, disruption_row) tuple."""
        results = find_affected_shipments()
        self.assertIsInstance(results, list)
        for item in results:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2,
                             "Each element must be a 2-tuple (shipment, disruption).")

    def test_four_mumbai_shipments_are_affected(self):
        """All four Mumbai-origin shipments must appear in the affected list."""
        affected_ids = {s["shipment_id"] for s, _ in find_affected_shipments()}
        for sid in ("S001", "S002", "S005", "S007"):
            self.assertIn(sid, affected_ids,
                          f"Mumbai shipment {sid} should be affected but was not found.")

    def test_pune_shipments_are_not_affected(self):
        """S003 (Pune→Ahmedabad) and S006 (Pune→Delhi) must not be affected."""
        affected_ids = {s["shipment_id"] for s, _ in find_affected_shipments()}
        for sid in ("S003", "S006"):
            self.assertNotIn(sid, affected_ids,
                             f"Pune shipment {sid} must not be affected by Mumbai disruptions.")

    def test_chennai_shipments_are_not_affected(self):
        """S004 (Chennai→Mumbai) and S008 (Chennai→Delhi) must not be affected."""
        affected_ids = {s["shipment_id"] for s, _ in find_affected_shipments()}
        for sid in ("S004", "S008"):
            self.assertNotIn(sid, affected_ids,
                             f"Chennai shipment {sid} must not be affected by Mumbai disruptions.")

    def test_s001_matched_to_road_blockage_not_port_closure(self):
        """S001 (Mumbai→Ahmedabad) must match the Mumbai-Ahmedabad road disruption (D002),
        not the port closure (D001), because the location string specifically names
        both the origin and the destination."""
        mapping = _affected_map()
        self.assertIn("S001", mapping,
                      "S001 must be in the affected shipments.")
        self.assertEqual(
            mapping["S001"], "D002",
            f"S001 (Mumbai→Ahmedabad) must match D002 (Road Blockage), "
            f"but got {mapping.get('S001')}.",
        )

    def test_s007_matched_to_road_blockage_not_port_closure(self):
        """S007 (Mumbai→Ahmedabad) must match D002 for the same reason as S001."""
        mapping = _affected_map()
        self.assertIn("S007", mapping,
                      "S007 must be in the affected shipments.")
        self.assertEqual(
            mapping["S007"], "D002",
            f"S007 (Mumbai→Ahmedabad) must match D002 (Road Blockage), "
            f"but got {mapping.get('S007')}.",
        )

    def test_s002_matched_to_port_closure(self):
        """S002 (Mumbai→Delhi) must match D001 (Port Closure): the highway disruption
        does not name Delhi, so D001 is the correct general-origin match."""
        mapping = _affected_map()
        self.assertIn("S002", mapping,
                      "S002 must be in the affected shipments.")
        self.assertEqual(
            mapping["S002"], "D001",
            f"S002 (Mumbai→Delhi) must match D001 (Port Closure), "
            f"but got {mapping.get('S002')}.",
        )

    def test_s005_matched_to_port_closure(self):
        """S005 (Mumbai→Jaipur) must match D001 (Port Closure) for the same reason."""
        mapping = _affected_map()
        self.assertIn("S005", mapping,
                      "S005 must be in the affected shipments.")
        self.assertEqual(
            mapping["S005"], "D001",
            f"S005 (Mumbai→Jaipur) must match D001 (Port Closure), "
            f"but got {mapping.get('S005')}.",
        )

    def test_resolved_disruption_d003_matches_nothing(self):
        """D003 (Carrier Strike, Delhi, Resolved) must not match any shipment."""
        for _, disruption in find_affected_shipments():
            self.assertNotEqual(
                disruption["disruption_id"], "D003",
                "Resolved disruption D003 must not match any shipment.",
            )


# ══════════════════════════════════════════════════════════════════════════════
# 2. Idle fleet
# ══════════════════════════════════════════════════════════════════════════════

class TestIdleFleet(unittest.TestCase):

    def test_only_available_vehicles_returned(self):
        """find_idle_fleet() must return only vehicles with status == 'Available'."""
        idle = find_idle_fleet()
        self.assertFalse(idle.empty, "There should be at least one available vehicle.")
        for _, vehicle in idle.iterrows():
            self.assertEqual(
                vehicle["status"], "Available",
                f"Vehicle {vehicle['vehicle_id']} has status '{vehicle['status']}' "
                "but only 'Available' vehicles should be returned.",
            )

    def test_assigned_vehicles_are_excluded(self):
        """No vehicle marked 'Assigned' in the fleet CSV may appear in the idle list."""
        fleet = load_fleet()
        assigned_ids = set(fleet[fleet["status"] == "Assigned"]["vehicle_id"])
        idle_ids = set(find_idle_fleet()["vehicle_id"])
        overlap = assigned_ids & idle_ids
        self.assertEqual(
            overlap, set(),
            f"Assigned vehicles found in idle fleet: {overlap}",
        )

    def test_idle_fleet_contains_expected_vehicles(self):
        """V009, V010, V011, V012 are 'Available' in the current fleet CSV."""
        idle_ids = set(find_idle_fleet()["vehicle_id"])
        for vid in ("V009", "V010", "V011", "V012"):
            self.assertIn(vid, idle_ids,
                          f"Vehicle {vid} should be idle/available but was not returned.")

    def test_find_matching_idle_fleet_cold_chain_filter(self):
        """When cold_chain='Yes', only Refrigerated Trucks must be returned."""
        result = find_matching_idle_fleet(
            cold_chain="Yes",
            cargo_weight=100,
            origin="Mumbai",
        )
        for _, v in result.iterrows():
            self.assertEqual(
                v["type"], "Refrigerated Truck",
                f"Vehicle {v['vehicle_id']} (type={v['type']!r}) was suggested "
                "for a cold-chain shipment but is not a Refrigerated Truck.",
            )

    def test_find_matching_idle_fleet_no_cold_chain_allows_regular_trucks(self):
        """When cold_chain='No', regular trucks are acceptable."""
        result = find_matching_idle_fleet(
            cold_chain="No",
            cargo_weight=100,
            origin="Ahmedabad",
        )
        types = set(result["type"])
        self.assertIn("Truck", types,
                      "Regular trucks should be returned for non-cold-chain shipments.")

    def test_find_matching_idle_fleet_capacity_filter(self):
        """Vehicles with capacity below cargo_weight must be excluded."""
        result = find_matching_idle_fleet(
            cold_chain="No",
            cargo_weight=4500,
            origin="Ahmedabad",
        )
        for _, v in result.iterrows():
            self.assertGreaterEqual(
                v["capacity_kg"], 4500,
                f"Vehicle {v['vehicle_id']} has capacity {v['capacity_kg']}kg "
                "which is below the required 4500kg.",
            )

    def test_find_matching_idle_fleet_prefers_origin_location(self):
        """When a vehicle at the shipment's origin is available, it must be returned
        in preference to one elsewhere."""
        # V011 is a Refrigerated Truck in Mumbai (Available, 3000kg)
        result = find_matching_idle_fleet(
            cold_chain="Yes",
            cargo_weight=1000,
            origin="Mumbai",
        )
        self.assertFalse(result.empty,
                         "At least one refrigerated truck should be available in Mumbai.")
        # All returned vehicles should be in Mumbai (origin preferred)
        locations = set(result["location"])
        self.assertEqual(
            locations, {"Mumbai"},
            f"Expected only Mumbai vehicles when origin preference applies, "
            f"got locations: {locations}.",
        )


# ══════════════════════════════════════════════════════════════════════════════
# 3. Temperature excursions
# ══════════════════════════════════════════════════════════════════════════════

class TestTemperatureExcursions(unittest.TestCase):

    def test_readings_above_8c_are_detected(self):
        """Any reading above 8°C must appear as an excursion."""
        excursions = find_temperature_excursions()
        self.assertFalse(excursions.empty,
                         "There must be at least one temperature excursion in the test data.")
        for _, exc in excursions.iterrows():
            self.assertGreater(
                exc["temperature_celsius"], 8,
                f"Reading {exc['reading_id']} has temperature {exc['temperature_celsius']}°C "
                "which is not above 8°C but was included as an excursion.",
            )

    def test_readings_at_or_below_8c_are_excluded(self):
        """Readings of 8°C or below must not be flagged as excursions."""
        from src.backend.analysis import load_temperature_readings
        readings = load_temperature_readings()
        safe_ids = set(
            readings[readings["temperature_celsius"] <= 8]["reading_id"]
        )
        excursion_ids = set(find_temperature_excursions()["reading_id"])
        overlap = safe_ids & excursion_ids
        self.assertEqual(
            overlap, set(),
            f"Safe readings wrongly included in excursions: {overlap}",
        )

    def test_t003_detected_as_moderate_excursion(self):
        """T003 (S002, 8.7°C) must be detected as a Moderate excursion."""
        excursions = find_temperature_excursions()
        exc_map = {row["reading_id"]: row for _, row in excursions.iterrows()}
        self.assertIn("T003", exc_map,
                      "T003 (8.7°C) must be detected as a temperature excursion.")
        self.assertEqual(exc_map["T003"]["severity"], "Moderate",
                         "T003 at 8.7°C must be classified as Moderate (≤10°C).")

    def test_t006_detected_as_moderate_excursion(self):
        """T006 (S005, 9.8°C) must be detected as a Moderate excursion (just below 10°C)."""
        excursions = find_temperature_excursions()
        exc_map = {row["reading_id"]: row for _, row in excursions.iterrows()}
        self.assertIn("T006", exc_map,
                      "T006 (9.8°C) must be detected as a temperature excursion.")
        self.assertEqual(exc_map["T006"]["severity"], "Moderate",
                         "T006 at 9.8°C must be classified as Moderate (≤10°C).")

    def test_severity_severe_threshold_is_above_10c(self):
        """Any reading strictly above 10°C must be classified as Severe."""
        excursions = find_temperature_excursions()
        for _, exc in excursions.iterrows():
            if exc["temperature_celsius"] > 10:
                self.assertEqual(
                    exc["severity"], "Severe",
                    f"Reading {exc['reading_id']} at {exc['temperature_celsius']}°C "
                    "should be Severe but was not.",
                )

    def test_s007_readings_within_safe_range_not_flagged(self):
        """S007 temperatures (3.5, 4.0, 4.3°C) are all safe and must not appear."""
        excursions = find_temperature_excursions()
        excursion_shipments = set(excursions["shipment_id"])
        self.assertNotIn(
            "S007", excursion_shipments,
            "S007 has no readings above 8°C and must not appear in excursions.",
        )

    def test_excursions_have_risk_message(self):
        """Every excursion must have a non-empty risk_message field."""
        for _, exc in find_temperature_excursions().iterrows():
            self.assertIn("risk_message", exc.index)
            self.assertTrue(
                str(exc["risk_message"]).strip(),
                f"Reading {exc['reading_id']} has an empty risk_message.",
            )


# ══════════════════════════════════════════════════════════════════════════════
# 4. Recommendations
# ══════════════════════════════════════════════════════════════════════════════

class TestRecommendations(unittest.TestCase):

    REQUIRED_KEYS = {
        "shipment_id",
        "current_carrier",
        "suggested_vehicle",
        "suggested_vehicle_capacity",
        "suggested_carrier",
        "suggested_route",
        "reason",
        "additional_risk",
        "urgent",
    }

    def test_recommendations_have_all_required_fields(self):
        """Every recommendation must contain all nine expected fields."""
        for rec in suggest_alternatives():
            missing = self.REQUIRED_KEYS - set(rec.keys())
            self.assertEqual(
                missing, set(),
                f"Recommendation for {rec.get('shipment_id')} is missing fields: {missing}",
            )

    def test_recommendations_produced_for_all_affected_shipments(self):
        """Every affected shipment must have exactly one recommendation."""
        affected_ids = {s["shipment_id"] for s, _ in find_affected_shipments()}
        rec_ids = set(_rec_map().keys())
        self.assertEqual(
            affected_ids, rec_ids,
            f"Mismatch between affected shipments {affected_ids} "
            f"and recommendation shipment IDs {rec_ids}.",
        )

    def test_s001_recommendation_present(self):
        """S001 must have a recommendation."""
        self.assertIn("S001", _rec_map(),
                      "No recommendation found for S001.")

    def test_s002_recommendation_present(self):
        """S002 must have a recommendation."""
        self.assertIn("S002", _rec_map(),
                      "No recommendation found for S002.")

    def test_s005_recommendation_present(self):
        """S005 must have a recommendation."""
        self.assertIn("S005", _rec_map(),
                      "No recommendation found for S005.")

    def test_s007_recommendation_present(self):
        """S007 must have a recommendation."""
        self.assertIn("S007", _rec_map(),
                      "No recommendation found for S007.")

    def test_s002_has_cold_chain_risk_flag(self):
        """S002 has a temperature excursion (T003, 8.7°C) and must have
        additional_risk set to a non-None, non-empty value."""
        rec = _rec_map().get("S002")
        self.assertIsNotNone(rec, "S002 recommendation must exist.")
        self.assertIsNotNone(
            rec["additional_risk"],
            "S002 has a cold-chain excursion and must have additional_risk set.",
        )
        self.assertIn(
            "Cold-chain", rec["additional_risk"],
            f"S002 additional_risk should mention cold-chain, got: {rec['additional_risk']!r}",
        )
        self.assertTrue(
            rec["urgent"],
            "S002 has a temperature excursion so urgent must be True.",
        )

    def test_s005_has_cold_chain_risk_flag(self):
        """S005 has a temperature excursion (T006, 9.8°C) and must have
        additional_risk set and urgent=True."""
        rec = _rec_map().get("S005")
        self.assertIsNotNone(rec, "S005 recommendation must exist.")
        self.assertIsNotNone(
            rec["additional_risk"],
            "S005 has a cold-chain excursion and must have additional_risk set.",
        )
        self.assertIn(
            "Cold-chain", rec["additional_risk"],
            f"S005 additional_risk should mention cold-chain, got: {rec['additional_risk']!r}",
        )
        self.assertTrue(
            rec["urgent"],
            "S005 has a temperature excursion so urgent must be True.",
        )

    def test_s001_has_no_cold_chain_risk(self):
        """S001 is not a cold-chain shipment and has no excursions — additional_risk must be None."""
        rec = _rec_map().get("S001")
        self.assertIsNotNone(rec, "S001 recommendation must exist.")
        self.assertIsNone(
            rec["additional_risk"],
            f"S001 has no temperature excursions so additional_risk must be None, "
            f"got: {rec['additional_risk']!r}.",
        )
        self.assertFalse(
            rec["urgent"],
            "S001 has no temperature excursion so urgent must be False.",
        )

    def test_s007_has_no_cold_chain_risk(self):
        """S007 is cold-chain but all its readings are safe — additional_risk must be None."""
        rec = _rec_map().get("S007")
        self.assertIsNotNone(rec, "S007 recommendation must exist.")
        self.assertIsNone(
            rec["additional_risk"],
            f"S007 has no readings above 8°C so additional_risk must be None, "
            f"got: {rec['additional_risk']!r}.",
        )
        self.assertFalse(
            rec["urgent"],
            "S007 has no temperature excursion so urgent must be False.",
        )

    def test_current_carrier_is_not_suggested_again(self):
        """The suggested carrier must differ from the current carrier."""
        for rec in suggest_alternatives():
            if rec["suggested_carrier"] != "No suitable carrier available":
                self.assertNotEqual(
                    rec["suggested_carrier"],
                    rec["current_carrier"],
                    f"Recommendation for {rec['shipment_id']} suggests the same "
                    f"carrier ({rec['current_carrier']}) that is already in use.",
                )

    def test_cold_chain_shipments_get_refrigerated_vehicle_or_none(self):
        """When a cold-chain shipment receives a vehicle suggestion, it must be
        a Refrigerated Truck (not a plain Truck)."""
        fleet = load_fleet()
        fleet_map = {row["vehicle_id"]: row for _, row in fleet.iterrows()}

        shipments = load_shipments()
        cold_chain_ids = set(
            shipments[shipments["cold_chain"] == "Yes"]["shipment_id"]
        )

        for rec in suggest_alternatives():
            if rec["shipment_id"] not in cold_chain_ids:
                continue
            vehicle_id = rec["suggested_vehicle"]
            if vehicle_id == "No suitable vehicle available":
                continue
            vehicle_type = fleet_map[vehicle_id]["type"]
            self.assertEqual(
                vehicle_type, "Refrigerated Truck",
                f"Cold-chain shipment {rec['shipment_id']} was assigned vehicle "
                f"{vehicle_id} (type={vehicle_type!r}) which is not refrigerated.",
            )

    def test_reason_is_not_generic_placeholder(self):
        """The reason field must not contain the old generic placeholder text."""
        banned = {"Active disruption affecting shipment", "Alternative route recommended"}
        for rec in suggest_alternatives():
            self.assertNotIn(
                rec["reason"],
                banned,
                f"Recommendation for {rec['shipment_id']} still has a generic "
                f"placeholder reason: {rec['reason']!r}",
            )

    def test_s001_route_uses_vadodara(self):
        """S001 (Mumbai→Ahmedabad) must receive the Vadodara bypass route."""
        rec = _rec_map().get("S001")
        self.assertIsNotNone(rec, "S001 recommendation must exist.")
        self.assertIn(
            "Vadodara", rec["suggested_route"],
            f"S001 Ahmedabad route should use Vadodara, got: {rec['suggested_route']!r}",
        )

    def test_s002_route_uses_jaipur(self):
        """S002 (Mumbai→Delhi) must receive the Jaipur bypass route."""
        rec = _rec_map().get("S002")
        self.assertIsNotNone(rec, "S002 recommendation must exist.")
        self.assertIn(
            "Jaipur", rec["suggested_route"],
            f"S002 Delhi route should use Jaipur, got: {rec['suggested_route']!r}",
        )

    def test_s005_route_uses_udaipur(self):
        """S005 (Mumbai→Jaipur) must receive the Udaipur bypass route."""
        rec = _rec_map().get("S005")
        self.assertIsNotNone(rec, "S005 recommendation must exist.")
        self.assertIn(
            "Udaipur", rec["suggested_route"],
            f"S005 Jaipur route should use Udaipur, got: {rec['suggested_route']!r}",
        )


# ══════════════════════════════════════════════════════════════════════════════
# 5. Data integrity
# ══════════════════════════════════════════════════════════════════════════════

class TestDataIntegrity(unittest.TestCase):

    def test_all_csv_files_load_without_error(self):
        """All five CSV files must load as non-empty DataFrames."""
        from src.backend.analysis import (
            load_carriers, load_disruptions, load_fleet,
            load_shipments, load_temperature_readings,
        )
        for name, loader in (
            ("shipments", load_shipments),
            ("disruptions", load_disruptions),
            ("fleet", load_fleet),
            ("carriers", load_carriers),
            ("temperature_readings", load_temperature_readings),
        ):
            df = loader()
            self.assertFalse(df.empty, f"{name}.csv loaded as an empty DataFrame.")

    def test_disruptions_have_status_column(self):
        """disruptions.csv must contain a 'status' column used by all filtering logic."""
        disruptions = load_disruptions()
        self.assertIn("status", disruptions.columns,
                      "disruptions.csv must have a 'status' column.")

    def test_fleet_status_values_are_valid(self):
        """Every vehicle in fleet.csv must have status 'Available' or 'Assigned'."""
        fleet = load_fleet()
        valid_statuses = {"Available", "Assigned"}
        for _, v in fleet.iterrows():
            self.assertIn(
                v["status"], valid_statuses,
                f"Vehicle {v['vehicle_id']} has unexpected status: {v['status']!r}",
            )

    def test_no_duplicate_shipment_ids(self):
        """shipments.csv must not contain duplicate shipment_id values."""
        shipments = load_shipments()
        duplicates = shipments[shipments.duplicated("shipment_id")]["shipment_id"].tolist()
        self.assertEqual(duplicates, [],
                         f"Duplicate shipment IDs found: {duplicates}")

    def test_temperature_readings_reference_valid_shipments(self):
        """Every shipment_id in temperature_readings.csv must exist in shipments.csv."""
        from src.backend.analysis import load_temperature_readings
        shipment_ids = set(load_shipments()["shipment_id"])
        readings = load_temperature_readings()
        for _, row in readings.iterrows():
            self.assertIn(
                row["shipment_id"], shipment_ids,
                f"Temperature reading {row['reading_id']} references unknown "
                f"shipment {row['shipment_id']!r}.",
            )


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)
