from dataclasses import FrozenInstanceError

import pytest

from app.models.enums import ScenarioType
from app.scenarios.catalog import SCENARIO_CATALOG


def test_catalog_contains_all_defined_scenarios():
    assert set(SCENARIO_CATALOG.keys()) == set(ScenarioType)


def test_catalog_keys_match_scenario_identifiers():
    for scenario_id, scenario in SCENARIO_CATALOG.items():
        assert scenario.scenario_id == scenario_id


def test_scenarios_have_unique_parameter_identifiers():
    for scenario in SCENARIO_CATALOG.values():
        parameter_ids = [
            parameter.parameter_id
            for parameter in scenario.parameters
        ]

        assert len(parameter_ids) == len(set(parameter_ids))


def test_scenarios_have_unique_phase_identifiers():
    for scenario in SCENARIO_CATALOG.values():
        phase_ids = [
            phase.phase_id
            for phase in scenario.phases
        ]

        assert len(phase_ids) == len(set(phase_ids))


def test_enum_parameters_have_allowed_values():
    for scenario in SCENARIO_CATALOG.values():
        for parameter in scenario.parameters:
            if parameter.value_type == "enum":
                assert parameter.allowed_values


def test_scientific_references_use_https():
    for scenario in SCENARIO_CATALOG.values():
        for reference in scenario.scientific_references:
            assert reference.url.startswith("https://")


def test_scenario_definitions_are_immutable():
    scenario = next(iter(SCENARIO_CATALOG.values()))

    with pytest.raises(FrozenInstanceError):
        scenario.name = "Modified Scenario"