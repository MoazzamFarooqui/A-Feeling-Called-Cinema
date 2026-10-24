import os
import sys

import pytest
from streamlit.testing.v1 import AppTest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

APP_PATH = os.path.join(ROOT, 'app.py')

PAGES = [
    'Home',
    'Mood to Scene',
    'Watch Party',
    'Time Budget',
    'Double Feature',
    'Cultural Bridge',
    'Era Machine',
    'Hidden Gems',
]


@pytest.fixture(scope='module')
def at():
    app = AppTest.from_file(APP_PATH, default_timeout=240)
    app.run()
    assert not app.exception
    return app


def goto(at, page):
    at.sidebar.radio[0].set_value(page).run()
    assert not at.exception, at.exception
    return at


def click(at, label):
    button = next(item for item in at.button if item.label == label)
    button.click().run()
    assert not at.exception, at.exception


def captions(at):
    return [item.value for item in at.caption]


def infos(at):
    return [item.value for item in at.info]


@pytest.mark.parametrize('page', PAGES)
def test_every_page_renders_without_exception(at, page):
    goto(at, page)
    assert not at.exception


def test_mood_journey(at):
    goto(at, 'Mood to Scene')
    at.text_area[0].set_value('A rainy Sunday afternoon with a warm cup of tea').run()
    click(at, 'Find my scene')
    assert any('films matched that mood' in text for text in captions(at))


def test_watch_party_single_person_journey(at):
    goto(at, 'Watch Party')
    at.number_input[0].set_value(1).run()
    at.text_input[0].set_value('Inception').run()
    at.selectbox[0].set_value(at.selectbox[0].options[0]).run()
    click(at, 'Find common ground')
    assert any('whole group' in text for text in captions(at))


def test_time_budget_thirty_minutes_shows_friendly_empty_state(at):
    goto(at, 'Time Budget')
    at.number_input[0].set_value(30).run()
    click(at, 'Show me what fits')
    assert any('shortest is 40 minutes' in text for text in infos(at))


def test_double_feature_journey(at):
    goto(at, 'Double Feature')
    at.text_input[0].set_value('Spirited Away').run()
    at.selectbox[0].set_value(at.selectbox[0].options[0]).run()
    click(at, 'Build the double feature')
    assert any('pairing' in text for text in captions(at))


def test_cultural_bridge_journey(at):
    goto(at, 'Cultural Bridge')
    at.text_input[0].set_value('Spirited Away').run()
    at.selectbox[0].set_value(at.selectbox[0].options[0]).run()
    click(at, 'Cross the bridge')
    assert any('international films' in text for text in captions(at))


def test_era_machine_journey(at):
    goto(at, 'Era Machine')
    at.text_input[0].set_value('The Matrix').run()
    at.selectbox[0].set_value(at.selectbox[0].options[0]).run()
    click(at, 'Fire up the machine')
    assert any('feel like your anchor' in text for text in captions(at))


def test_hidden_gems_impossible_filters_show_empty_state(at):
    goto(at, 'Hidden Gems')
    at.selectbox[0].set_value('TV Movie').run()
    at.number_input[0].set_value(1920).run()
    at.number_input[1].set_value(1920).run()
    click(at, 'Apply filters')
    assert any('No gems match those filters' in text for text in infos(at))


def test_picker_with_no_matches_warns_before_running(at):
    goto(at, 'Double Feature')
    at.text_input[0].set_value('zzzzqqqxxx').run()
    assert any('No titles match that search yet' in text for text in captions(at))
    click(at, 'Build the double feature')
    assert any('Choose an anchor film first' in item.value for item in at.warning)


def test_error_state_offers_working_retry_button(at, monkeypatch):
    import src.recommender as recommender_module

    goto(at, 'Double Feature')
    at.text_input[0].set_value('The Godfather').run()
    at.selectbox[0].set_value(at.selectbox[0].options[0]).run()

    def explode(self, movie_id, mode='mirror'):
        raise ValueError('engine exploded')

    monkeypatch.setattr(recommender_module.MovieRecommender, 'double_feature', explode)
    click(at, 'Build the double feature')
    assert any('engine exploded' in item.value for item in at.error)
    assert any(button.label == 'Try again' for button in at.button)

    monkeypatch.undo()
    click(at, 'Try again')
    assert not at.error
    assert any('pairing' in text for text in captions(at))
