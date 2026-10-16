from dataclasses import replace

from game.bureaucracy import collect_initial_document, handover
from game.input_state import InputState
from game.state import create_game_state, update_game_state


def test_matching_dropoff_zone_accepts_document() -> None:
    state = create_game_state()
    assert state.world.document_source is not None
    collected = update_game_state(
        replace(state, player=state.player.at(state.world.document_source.bounds.center)),
        InputState(interact_pressed=True),
        0,
    )
    assert collected.workflow is not None and collected.workflow.carried_document is not None
    zone = collected.world.dropoff_zones[1]
    delivered = update_game_state(
        replace(collected, player=collected.player.at(zone.center)),
        InputState(interact_pressed=True),
        0,
    )
    assert delivered.workflow is not None
    assert delivered.workflow.definition.servants[0].served


def test_each_authored_pickup_zone_can_start_document_interaction() -> None:
    state = create_game_state()
    assert len(state.world.document_sources) == 2
    second_source = state.world.document_sources[1]
    collected = update_game_state(
        replace(state, player=state.player.at(second_source.bounds.center)),
        InputState(interact_pressed=True),
        0,
    )
    assert collected.workflow is not None
    assert collected.workflow.carried_document is not None


def test_mismatched_dropoff_zone_rejects_document_without_mutation() -> None:
    state = create_game_state()
    carrying, _ = collect_initial_document(state.workflow)
    carrying_state = replace(state, workflow=carrying)
    zone = carrying_state.world.dropoff_zones[2]
    rejected = update_game_state(
        replace(carrying_state, player=carrying_state.player.at(zone.center)),
        InputState(interact_pressed=True),
        0,
    )
    assert rejected.workflow == carrying_state.workflow
