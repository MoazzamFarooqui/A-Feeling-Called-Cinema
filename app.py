from datetime import time
from html import escape

import streamlit as st

from src.recommender import VALID_DECADES, MovieRecommender

st.set_page_config(
    page_title="A Feeling Called Cinema",
    page_icon=":material/movie:",
    layout="wide",
    initial_sidebar_state="auto",
)

GENRES = [
    "Action",
    "Adventure",
    "Animation",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "History",
    "Horror",
    "Music",
    "Mystery",
    "Romance",
    "Science Fiction",
    "TV Movie",
    "Thriller",
    "War",
    "Western",
]

MOOD_EXAMPLES = [
    "A rainy Sunday afternoon with a warm cup of tea",
    "An adrenaline rush that never lets go",
    "A slow, beautiful heartbreak",
    "Something strange and unsettling after midnight",
    "A cozy adventure the whole family can enjoy",
    "A clever puzzle that rewards paying attention",
]

FEATURES = [
    ("Mood to Scene", "Describe a feeling, moment, or vibe. Semantic search finds the films that share it."),
    ("Watch Party", "Blend one to five very different picks into a single film everyone can live with."),
    ("Time Budget", "Tell us how many minutes you have and see films that actually fit, with finish times."),
    ("Double Feature", "Pair a film with its mirror image or with its complete opposite."),
    ("Cultural Bridge", "Discover the international films that rhyme with something you already love."),
    ("Era Machine", "Drop a movie into another decade and find the films it belongs beside."),
    ("Hidden Gems", "High ratings, low buzz. Filter the films most people never found."),
]

STYLES = """
<style>
:root {
    --cm-black: #000000;
    --cm-white: #ffffff;
    --cm-muted: #555555;
    --cm-border: #e5e5e5;
    --cm-hover: #f5f5f5;
    --cm-active: #f0f0f0;
}

html, body, .stApp, [data-testid="stApp"], [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stHeader"], [data-testid="stToolbar"] {
    background: var(--cm-white) !important;
    color: var(--cm-black);
}
.stApp { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
.block-container { padding-top: 2.4rem; max-width: 1180px; }

[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
    background: var(--cm-white) !important;
    border-right: 1px solid var(--cm-border);
}
[data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: var(--cm-muted) !important; }

[data-testid="stSidebar"] [data-testid="stRadioOption"] {
    border-radius: 8px;
    padding: .38rem .55rem;
    margin: .12rem 0;
    transition: background-color .15s ease, box-shadow .15s ease;
}
[data-testid="stSidebar"] [data-testid="stRadioOption"]:hover { background: var(--cm-hover); }
[data-testid="stSidebar"] [data-testid="stRadioOption"]:has(input:checked) {
    background: var(--cm-active);
    box-shadow: inset 2px 0 0 var(--cm-black);
}
[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child { display: none; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] p { color: var(--cm-black) !important; font-weight: 500; }

[data-testid="stAppDeployButton"], [data-testid="stToolbarActions"] { display: none !important; }
[data-testid="stMainMenuButton"] svg, [data-testid="stSidebarCollapseButton"] svg,
[data-testid="stExpandSidebarButton"] svg { color: var(--cm-black) !important; fill: var(--cm-black) !important; }

[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p { color: var(--cm-black); }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: var(--cm-muted) !important; }

.cm-brand { font-size: 1.35rem; font-weight: 700; letter-spacing: .02em; color: var(--cm-black); }
.cm-brand span { color: var(--cm-black); }
.cm-hero h1 { font-size: 2.7rem; line-height: 1.12; letter-spacing: -.02em; margin: 0 0 .7rem; color: var(--cm-black); }
.cm-hero p { color: var(--cm-muted); font-size: 1.02rem; max-width: 62ch; margin: 0; }
.cm-section-title { font-size: 1.5rem; font-weight: 650; letter-spacing: -.01em; margin: 2.2rem 0 .3rem; color: var(--cm-black); }
.cm-section-sub { color: var(--cm-muted); margin: 0 0 1.1rem; }
.cm-feature { border: 1px solid var(--cm-border); border-radius: 14px; padding: 1.05rem 1.15rem; background: var(--cm-white); height: 100%; transition: background-color .2s ease, border-color .2s ease; }
.cm-feature:hover { background: #fafafa; border-color: #d4d4d4; }
.cm-feature h4 { margin: 0 0 .35rem; font-size: 1rem; color: var(--cm-black); }
.cm-feature p { margin: 0; color: var(--cm-muted); font-size: .88rem; line-height: 1.5; }
.cm-card-title { font-size: 1.06rem; font-weight: 650; line-height: 1.3; color: var(--cm-black); }
.cm-meta { color: var(--cm-muted); font-size: .84rem; margin: .25rem 0 .55rem; }
.cm-overview { display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; color: var(--cm-muted); font-size: .88rem; line-height: 1.55; margin: .1rem 0 .4rem; }
.cm-pill { display: inline-block; font-size: .7rem; padding: .12rem .55rem; border-radius: 999px; border: 1px solid #d9d9d9; background: var(--cm-white); color: var(--cm-black); margin: 0 .3rem .3rem 0; white-space: nowrap; }
.cm-pill.gem { background: var(--cm-black); border-color: var(--cm-black); color: var(--cm-white); font-weight: 600; }
.cm-hint { color: var(--cm-muted); font-size: .95rem; }

[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cm-card-title) {
    background: var(--cm-white);
    border: 1px solid var(--cm-border) !important;
    border-radius: 12px !important;
    transition: background-color .2s ease, border-color .2s ease;
}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cm-card-title):hover {
    background: #fafafa;
    border-color: #d4d4d4 !important;
}

[data-testid="stHorizontalBlock"]:has(.cm-card-title) { align-items: stretch; }
[data-testid="stColumn"]:has(.cm-card-title) {
    display: flex;
    flex-direction: column;
}
[data-testid="stColumn"]:has(.cm-card-title) > [data-testid="stVerticalBlock"] {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
}
[data-testid="stColumn"]:has(.cm-card-title) > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
}
[data-testid="stColumn"]:has(.cm-card-title) > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
    flex: 1 1 auto;
}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cm-card-title) > [data-testid="stLayoutWrapper"]:has([data-testid="stExpander"]) {
    margin-top: auto;
    flex: 0 0 auto;
}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .cm-card-title) [data-testid="stExpander"] details {
    display: flex;
    flex-direction: column-reverse;
}

[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"],
[data-testid="stNumberInputContainer"], [data-testid="stSelectbox"] [role="group"],
[data-testid="stTimeInput"] [role="group"] {
    background: var(--cm-white) !important;
    border: 1px solid var(--cm-border) !important;
    border-radius: 8px !important;
    color: var(--cm-black) !important;
    transition: border-color .15s ease, box-shadow .15s ease;
}
[data-testid="stTextInputRootElement"]:focus-within, [data-testid="stTextAreaRootElement"]:focus-within,
[data-testid="stNumberInputContainer"]:focus-within, [data-testid="stSelectbox"] [role="group"]:focus-within {
    border-color: var(--cm-black) !important;
    box-shadow: 0 0 0 1px var(--cm-black) !important;
}
[data-testid="stTextInputRootElement"] input, [data-testid="stTextAreaRootElement"] textarea,
[data-testid="stNumberInputField"], [data-testid="stSelectbox"] input, [data-testid="stTimeInput"] input {
    background: transparent !important;
    color: var(--cm-black) !important;
    border: none !important;
    box-shadow: none !important;
}
::placeholder { color: #888888 !important; opacity: 1; }
[data-testid="stSelectbox"] button { background: transparent !important; color: var(--cm-black) !important; }
[data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] { background: var(--cm-white) !important; color: var(--cm-black) !important; border-left: 1px solid var(--cm-border); }
[data-testid="stNumberInputStepDown"]:hover, [data-testid="stNumberInputStepUp"]:hover { background: var(--cm-hover) !important; }
[data-testid="stNumberInputStepDown"] svg, [data-testid="stNumberInputStepUp"] svg { fill: var(--cm-black); color: var(--cm-black); }

[role="listbox"] { background: var(--cm-white) !important; border: 1px solid var(--cm-border) !important; border-radius: 8px !important; box-shadow: 0 6px 18px rgba(0,0,0,.08) !important; }
[role="option"] { background: var(--cm-white); color: var(--cm-black) !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] { background: var(--cm-active) !important; color: var(--cm-black) !important; }

button[kind="primary"], [data-testid="stBaseButton-primary"] { background: var(--cm-black) !important; border: 1px solid var(--cm-black) !important; color: var(--cm-white) !important; border-radius: 8px !important; font-weight: 600; transition: background-color .15s ease, color .15s ease; }
button[kind="primary"] p, button[kind="primary"] span, button[kind="primary"] div, [data-testid="stBaseButton-primary"] p, [data-testid="stBaseButton-primary"] span, [data-testid="stBaseButton-primary"] div { color: var(--cm-white) !important; }
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover { background: #1a1a1a !important; border-color: #1a1a1a !important; }
button[kind="secondary"], [data-testid="stBaseButton-secondary"] { background: var(--cm-white) !important; border: 1px solid var(--cm-black) !important; color: var(--cm-black) !important; border-radius: 8px !important; font-weight: 600; transition: background-color .15s ease, color .15s ease; }
button[kind="secondary"] p, button[kind="secondary"] span, button[kind="secondary"] div, [data-testid="stBaseButton-secondary"] p, [data-testid="stBaseButton-secondary"] span, [data-testid="stBaseButton-secondary"] div { color: var(--cm-black) !important; }
button[kind="secondary"]:hover, [data-testid="stBaseButton-secondary"]:hover { background: var(--cm-hover) !important; }
button:disabled { opacity: .45 !important; }
button:focus-visible { outline: 2px solid var(--cm-black); outline-offset: 2px; }

[data-testid="stExpander"] { background: var(--cm-white) !important; border: 1px solid var(--cm-border) !important; border-radius: 8px !important; }
[data-testid="stExpander"] summary { color: var(--cm-black) !important; }
[data-testid="stExpander"] summary:hover { background: #fafafa; }
[data-testid="stExpander"] svg { color: var(--cm-black); fill: var(--cm-black); }

[data-testid="stAlert"] { background: var(--cm-white) !important; border: 1px solid var(--cm-border) !important; color: var(--cm-black) !important; border-radius: 8px !important; }
[data-testid="stAlert"] * { color: var(--cm-black) !important; }
[data-testid="stAlert"] svg { fill: var(--cm-black) !important; color: var(--cm-black) !important; }

[data-testid="stCheckbox"] input { accent-color: var(--cm-black); }
[data-testid="stSpinner"] svg { color: var(--cm-black) !important; }
a, a:visited { color: var(--cm-black) !important; }
hr { border-color: var(--cm-border) !important; }

@media (max-width: 700px) {
    .cm-hero h1 { font-size: 2rem; }
    .block-container { padding-top: 1.6rem; }
}
</style>
"""


@st.cache_resource(show_spinner="Loading the movie engine…")
def load_recommender():
    return MovieRecommender()


@st.cache_data(show_spinner=False)
def cached_search(query, top_k):
    return load_recommender().semantic_search(query, top_k=top_k)


@st.cache_data(show_spinner=False)
def cached_watch_party(movie_ids, top_k, max_runtime):
    return load_recommender().watch_party(list(movie_ids), top_k=top_k, max_runtime=max_runtime)


@st.cache_data(show_spinner=False)
def cached_time_budget(minutes, start_clock, calm_only, top_k):
    return load_recommender().time_budget(
        minutes, start_clock=start_clock, calm_only=calm_only, top_k=top_k
    )


@st.cache_data(show_spinner=False)
def cached_double_feature(movie_id, mode):
    return load_recommender().double_feature(movie_id, mode=mode)


@st.cache_data(show_spinner=False)
def cached_cultural_bridge(movie_id, top_k):
    return load_recommender().cultural_bridge(movie_id, top_k=top_k)


@st.cache_data(show_spinner=False)
def cached_era_machine(movie_id, decade, top_k):
    return load_recommender().era_time_machine(movie_id, decade, top_k=top_k)


@st.cache_data(show_spinner=False)
def cached_hidden_gems(genre, year_min, year_max, top_k):
    return load_recommender().hidden_gems(
        genre=genre, year_min=year_min, year_max=year_max, top_k=top_k
    )


@st.cache_data(show_spinner=False)
def cached_search_titles(query, limit=8):
    return load_recommender().search_titles(query, limit=limit)


def page_header(title, subtitle):
    st.markdown(
        f"""
        <div class="cm-hero">
            <h1>{escape(title)}</h1>
            <p>{escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_movie_card(movie):
    title = escape(movie["title"])
    pills = []
    if movie.get("is_hidden_gem"):
        pills.append('<span class="cm-pill gem">Hidden gem</span>')
    if movie.get("is_foreign"):
        pills.append(f'<span class="cm-pill">{escape(movie["language"].upper())} · international</span>')
    if "finish_time" in movie:
        pills.append(f'<span class="cm-pill">Ends {escape(movie["finish_time"])}</span>')
    if "score" in movie:
        pills.append(f'<span class="cm-pill">Match {movie["score"]:.2f}</span>')
    if "similarity" in movie:
        pills.append(f'<span class="cm-pill">Similarity {movie["similarity"]:.2f}</span>')
    if "intensity_shift" in movie:
        pills.append(f'<span class="cm-pill">Intensity shift {movie["intensity_shift"]:+.2f}</span>')

    with st.container(border=True):
        st.markdown(
            f"""
            <div class="cm-card-title">{title}</div>
            <div class="cm-meta">{movie["year"]} · {movie["runtime"]} min · {movie["vote_average"]:.1f}/10</div>
            <div>{''.join(pills)}</div>
            """,
            unsafe_allow_html=True,
        )
        if movie.get("tagline"):
            st.caption(f'“{movie["tagline"]}”')
        st.markdown(
            f'<p class="cm-overview">{escape(movie["overview"])}</p>',
            unsafe_allow_html=True,
        )
        with st.expander("Details"):
            facts = [
                ("Decade", movie["decade_label"]),
                ("Genres", ", ".join(movie["genres"]) or "Unknown"),
                ("Runtime", f'{movie["runtime"]} min'),
                ("Rating", f'{movie["vote_average"]:.1f}/10 from {movie["vote_count"]:,} votes'),
                ("Weighted rating", f'{movie["weighted_rating"]:.1f}'),
                ("Popularity", f'{movie["popularity"]:.1f}'),
                ("Gem score", f'{movie["gem_score"]:.3f}'),
                ("Intensity", movie["intensity_label"]),
                ("Studio", movie["main_studio"]),
                ("Language", movie["language"]),
            ]
            if "finish_time" in movie:
                facts.append(("Finish time", movie["finish_time"]))
            if movie.get("note"):
                facts.append(("Note", movie["note"]))
            st.markdown("  \n".join(f"**{label}:** {value}" for label, value in facts))


def render_grid(movies, columns=3, empty_message="No matches yet. Adjust the inputs and try again."):
    if not movies:
        st.info(empty_message)
        return
    for row_start in range(0, len(movies), columns):
        row_cols = st.columns(columns, gap="medium")
        for col, movie in zip(row_cols, movies[row_start:row_start + columns]):
            with col:
                render_movie_card(movie)


def movie_picker(label, key, exclude_ids=()):
    query = st.text_input(
        label,
        placeholder="Type a movie title (at least 2 characters)…",
        key=f"{key}_query",
    )
    if len(query.strip()) < 2:
        st.caption("Start typing to search 25,706 titles.")
        return None
    excluded = set(exclude_ids)
    hits = [movie for movie in cached_search_titles(query.strip()) if movie["id"] not in excluded]
    if not hits:
        st.caption("No titles match that search yet.")
        return None
    labels = [f'{movie["title"]} ({movie["year"]})' for movie in hits]
    choice = st.selectbox("Matches", labels, key=f"{key}_match", label_visibility="collapsed")
    return hits[labels.index(choice)]


def request_retry(key):
    st.session_state[f"{key}_retry"] = True


def action_clicked(label, key):
    clicked = st.button(label, type="primary")
    return clicked or st.session_state.pop(f"{key}_retry", False)


def show_action_error(prefix, key):
    message = st.session_state.get(f"{key}_error")
    if not message:
        return
    st.error(f"{prefix} {message}")
    st.button(
        "Try again",
        key=f"{key}_retry_button",
        on_click=request_retry,
        args=(key,),
    )


def sidebar():
    st.sidebar.markdown('<div class="cm-brand">A Feeling Called Cinema</div>', unsafe_allow_html=True)
    st.sidebar.caption("Data-driven movie recommendations")
    pages = {
        "Home": page_home,
        "Mood to Scene": page_mood,
        "Watch Party": page_watch_party,
        "Time Budget": page_time_budget,
        "Double Feature": page_double_feature,
        "Cultural Bridge": page_cultural_bridge,
        "Era Machine": page_era_machine,
        "Hidden Gems": page_hidden_gems,
    }
    choice = st.sidebar.radio("Navigate", list(pages), label_visibility="collapsed")
    return pages[choice]


def page_home():
    page_header(
        "Find the perfect film for the exact moment.",
        "For the nights that need a very specific kind of movie.",
    )

    st.markdown('<div class="cm-section-title">Seven ways in</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="cm-section-sub">Choose a tool in the sidebar, then give it one small input.</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(2, gap="medium")
    for index, (name, description) in enumerate(FEATURES):
        with cols[index % 2]:
            st.markdown(
                f'<div class="cm-feature"><h4>{escape(name)}</h4><p>{escape(description)}</p></div>',
                unsafe_allow_html=True,
            )
            st.write("")

    st.markdown(
        '<div class="cm-section-title">Tonight’s overlooked gems</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="cm-section-sub">High ratings and low popularity, pulled live from the dataset.</p>',
        unsafe_allow_html=True,
    )
    gems = cached_hidden_gems(None, None, None, 3)
    render_grid(gems, columns=3, empty_message="No hidden gems available right now.")


def page_mood():
    page_header(
        "Describe the feeling. We’ll find the film.",
        "Forget genres. Tell us the feeling.",
    )

    def apply_example():
        st.session_state.mood_query = st.session_state.mood_example

    example = st.selectbox(
        "Need inspiration?",
        MOOD_EXAMPLES,
        index=None,
        placeholder="Pick an example mood…",
        key="mood_example",
        on_change=apply_example,
    )
    if example:
        st.caption("Example loaded into the scene box below.")
    query = st.text_area(
        "Your scene",
        placeholder="e.g. A lonely drive through neon streets at 2am",
        height=100,
        key="mood_query",
    )
    top_k = st.number_input("How many films?", min_value=1, max_value=50, value=12)

    if action_clicked("Find my scene", "mood"):
        if len(query.strip()) < 3:
            st.warning("Describe the mood in at least a few words.")
        else:
            try:
                with st.spinner("Searching the mood space…"):
                    st.session_state.mood_results = cached_search(query.strip(), top_k)
                    st.session_state.mood_error = ""
            except Exception as exc:
                st.session_state.mood_results = None
                st.session_state.mood_error = str(exc)

    show_action_error("Could not run that search.", "mood")
    results = st.session_state.get("mood_results")
    if results is not None:
        if results:
            st.caption(f"{len(results)} films matched that mood.")
        render_grid(results, empty_message="No films matched that mood. Try different wording.")


def page_watch_party():
    page_header(
        "One film. Several very different people.",
        "Your favourites are different. Your next favourite doesn't have to be.",
    )

    party_size = st.number_input("How many people are choosing?", min_value=1, max_value=5, value=2)
    picks = []
    for index in range(party_size):
        movie = movie_picker(
            f"Person {index + 1}",
            key=f"watch_party_{index}",
            exclude_ids=[pick["id"] for pick in picks if pick],
        )
        picks.append(movie)

    cap_runtime = st.checkbox("Cap the runtime", value=False)
    max_runtime = None
    if cap_runtime:
        max_runtime = st.number_input(
            "Maximum runtime (minutes)", min_value=60, max_value=240, value=180, step=10
        )

    if action_clicked("Find common ground", "watch_party"):
        movie_ids = tuple(pick["id"] for pick in picks if pick)
        if not movie_ids:
            st.warning("Choose at least one film first.")
        else:
            try:
                with st.spinner("Resolving everyone’s taste…"):
                    st.session_state.watch_party_results = cached_watch_party(
                        movie_ids, 12, max_runtime
                    )
                    st.session_state.watch_party_error = ""
            except Exception as exc:
                st.session_state.watch_party_results = None
                st.session_state.watch_party_error = str(exc)

    show_action_error("Could not build that watch party.", "watch_party")
    results = st.session_state.get("watch_party_results")
    if results is not None:
        if results and any(movie.get("note") for movie in results):
            st.caption("Filters were relaxed slightly so the group still had common ground.")
        if results:
            st.caption(f"{len(results)} films the whole group can agree on.")
        render_grid(results, empty_message="No shared film found. Try fewer or broader picks.")


def page_time_budget():
    page_header(
        "You have a certain number of minutes. Use them well.",
        "Your time is limited. Make the movie count.",
    )

    minutes = st.number_input("Minutes available tonight", min_value=30, max_value=240, value=120, step=15)
    plan_clock = st.checkbox("Plan the evening clock", value=False)
    start_time = None
    if plan_clock:
        start_time = st.time_input("Start time", value=time(20, 0), step=900)
    calm_only = st.toggle("Calm, bedtime-safe films only", value=False)

    if action_clicked("Show me what fits", "time_budget"):
        start_clock = start_time.strftime("%H:%M") if start_time else None
        try:
            with st.spinner("Checking the clock…"):
                st.session_state.time_budget_results = cached_time_budget(
                    minutes, start_clock, calm_only, 12
                )
                st.session_state.time_budget_error = ""
        except Exception as exc:
            st.session_state.time_budget_results = None
            st.session_state.time_budget_error = str(exc)

    show_action_error("Could not build that schedule.", "time_budget")
    results = st.session_state.get("time_budget_results")
    if results is not None:
        if results:
            st.caption(f"{len(results)} films fit inside {minutes} minutes.")
        shortest = int(load_recommender().df["runtime"].min())
        render_grid(
            results,
            empty_message=(
                f"No film in the catalogue is {minutes} minutes or shorter. "
                f"The shortest is {shortest} minutes — give yourself at least that much time."
            ),
        )


def page_double_feature():
    page_header(
        "Two films that belong in the same night.",
        "Find its other half. Or its complete opposite.",
    )

    movie = movie_picker("Anchor film", key="double_feature")
    mode_label = st.radio("Pairing style", ["Mirror", "Contrast"], horizontal=True)
    mode = mode_label.lower()

    if mode == "mirror":
        st.caption("Mirror: same feeling, different era.")
    else:
        st.caption("Contrast: same genre, opposite energy.")

    if action_clicked("Build the double feature", "double_feature"):
        if not movie:
            st.warning("Choose an anchor film first.")
        else:
            try:
                with st.spinner("Finding the other half…"):
                    st.session_state.double_feature_results = cached_double_feature(
                        movie["id"], mode
                    )
                    st.session_state.double_feature_error = ""
            except Exception as exc:
                st.session_state.double_feature_results = None
                st.session_state.double_feature_error = str(exc)

    show_action_error("Could not build that pairing.", "double_feature")
    results = st.session_state.get("double_feature_results")
    if results:
        st.caption(f"A {results['mode']} pairing, in viewing order.")
        render_grid(results["playlist"], columns=2)


def page_cultural_bridge():
    page_header(
        "The same story, told somewhere else.",
        "The same soul, in a different language.",
    )

    movie = movie_picker("Anchor film", key="cultural_bridge")
    top_k = st.number_input("How many bridges?", min_value=1, max_value=50, value=12)

    if action_clicked("Cross the bridge", "cultural_bridge"):
        if not movie:
            st.warning("Choose an anchor film first.")
        else:
            try:
                with st.spinner("Looking beyond the usual borders…"):
                    st.session_state.cultural_bridge_results = cached_cultural_bridge(
                        movie["id"], top_k
                    )
                    st.session_state.cultural_bridge_error = ""
            except Exception as exc:
                st.session_state.cultural_bridge_results = None
                st.session_state.cultural_bridge_error = str(exc)

    show_action_error("Could not build that bridge.", "cultural_bridge")
    results = st.session_state.get("cultural_bridge_results")
    if results is not None:
        if results:
            st.caption(f"{len(results)} international films share that fingerprint.")
        render_grid(results, empty_message="No international matches surfaced. Try another film.")


def page_era_machine():
    page_header(
        "What if this film had been made in another decade?",
        "The story stays. The decades change.",
    )

    movie = movie_picker("Anchor film", key="era_machine")
    decade = st.selectbox(
        "Travel to the",
        VALID_DECADES,
        index=len(VALID_DECADES) - 2,
        format_func=lambda value: f"{value}s",
    )
    top_k = st.number_input("How many contemporaries?", min_value=1, max_value=50, value=12)

    if action_clicked("Fire up the machine", "era_machine"):
        if not movie:
            st.warning("Choose an anchor film first.")
        else:
            try:
                with st.spinner(f"Traveling to the {decade}s…"):
                    st.session_state.era_machine_results = cached_era_machine(
                        movie["id"], decade, top_k
                    )
                    st.session_state.era_machine_error = ""
            except Exception as exc:
                st.session_state.era_machine_results = None
                st.session_state.era_machine_error = str(exc)

    show_action_error("Could not make that trip.", "era_machine")
    results = st.session_state.get("era_machine_results")
    if results is not None:
        if results:
            st.caption(f"{len(results)} films from the {decade}s that feel like your anchor.")
        render_grid(results, empty_message="No films surfaced in that decade. Try another one.")


def page_hidden_gems():
    page_header(
        "The films audiences found before the algorithm did.",
        "Some of cinema’s best stories are still waiting to be discovered.",
    )

    cols = st.columns(4, gap="medium")
    with cols[0]:
        genre = st.selectbox("Genre", ["Any genre"] + GENRES)
    with cols[1]:
        year_from = st.number_input("From year", min_value=1920, max_value=2023, value=1920)
    with cols[2]:
        year_to = st.number_input("To year", min_value=1920, max_value=2023, value=2023)
    with cols[3]:
        top_k = st.number_input("How many gems?", min_value=1, max_value=50, value=20)

    if action_clicked("Apply filters", "hidden_gems"):
        if year_from > year_to:
            st.warning("From year must be less than or equal to To year.")
        else:
            try:
                with st.spinner("Digging through the catalogue…"):
                    st.session_state.hidden_gems_results = cached_hidden_gems(
                        None if genre == "Any genre" else genre,
                        int(year_from),
                        int(year_to),
                        int(top_k),
                    )
                    st.session_state.hidden_gems_error = ""
                    st.session_state.hidden_gems_loaded = True
            except Exception as exc:
                st.session_state.hidden_gems_results = None
                st.session_state.hidden_gems_error = str(exc)

    if not st.session_state.get("hidden_gems_loaded"):
        with st.spinner("Loading tonight’s gems…"):
            st.session_state.hidden_gems_results = cached_hidden_gems(None, None, None, 20)
        st.session_state.hidden_gems_loaded = True

    show_action_error("Could not load hidden gems.", "hidden_gems")
    results = st.session_state.get("hidden_gems_results") or []
    if results:
        st.caption(f"{len(results)} overlooked films, ranked by gem score.")
    render_grid(results, empty_message="No gems match those filters. Widen the range and try again.")


st.markdown(STYLES, unsafe_allow_html=True)
selected_page = sidebar()
selected_page()
