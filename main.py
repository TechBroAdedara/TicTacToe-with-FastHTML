import uuid
from fasthtml.common import (
    fast_app,
    Div,
    H1,
    P,
    Button,
    Link,
    Script,
    Mount,
    StaticFiles,
    serve,
    Style,
)
from icecream import ic  # for debugging, nothing special

# Custom global style for the app
style = Style(
    """
            body{
                min-height: 100vh;
                margin:0;
                background-color: #1A1A1E;
                display:grid;
            }"""
)

tailwind_script = Script(src="https://cdn.tailwindcss.com")
local_css_with_tailwind = Link(
    rel="stylesheet", href="/src/output.css"
)  # fallback for offline use
script = Script(src="/src/htmx.min.js")  # also fallback for HTMX script

app, rt = fast_app(
    routes=[Mount("/src", StaticFiles(directory="src"), name="src")],
    hdrs=(local_css_with_tailwind, style, script, tailwind_script),
    pico=False,
    live=True,
)

# Store game states per user in dictionaries
button_states_dict = {}
current_state_index_dict = {}
winner_found_game_ended_dict = {}

win_states = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
]  # possible win streaks/states for Xs and Os

# Function to initialize or fetch the user's game state
def get_user_game_state(user_id):
    """Initialize the game state for a user if not already initialized."""
    if user_id not in button_states_dict:
        button_states_dict[user_id] = [[None for _ in range(9)] for _ in range(9)]
        current_state_index_dict[user_id] = -1
        winner_found_game_ended_dict[user_id] = False
    return (
        button_states_dict[user_id],
        current_state_index_dict[user_id],
        winner_found_game_ended_dict[user_id],
    )


def check_win(player, user_id) -> bool:
    # Fetch user-specific game state
    button_states, current_state_index, winner_found_game_ended = get_user_game_state(
        user_id
    )

    for cell_1, cell_2, cell_3 in win_states:
        if (
            button_states[current_state_index][cell_1] is not None
            and button_states[current_state_index][cell_1]
            == button_states[current_state_index][cell_2]
            and button_states[current_state_index][cell_2]
            == button_states[current_state_index][cell_3]
        ):
            winner_found_game_ended_dict[user_id] = True
            return f"Player {player} wins the game!"

    # Check if it's a tie
    if all(value is not None for value in button_states[current_state_index]):
        winner_found_game_ended_dict[user_id] = True
        return "No Winner :("

    return f"Player {'X' if player == 'O' else 'O'}'s turn!"


def handle_click(index: int, user_id: str):
    """Handle click for a specific user."""
    button_states, current_state_index, _ = get_user_game_state(user_id)

    next_index = current_state_index + 1
    button_states[next_index] = button_states[current_state_index][
        :
    ]  # Copy current snapshot

    if button_states[current_state_index][index] is None:
        if "X" not in button_states[current_state_index] or button_states[
            current_state_index
        ].count("X") <= button_states[current_state_index].count("O"):
            button_states[next_index][index] = "X"
        else:
            button_states[next_index][index] = "O"

    current_state_index_dict[user_id] = next_index
    return button_states[next_index][index]


@app.get("/on_click")
def render_button(index: int, user_id: str):
    """Handles button click for the user."""
    player = handle_click(index, user_id)
    winner = check_win(player, user_id)  # Checks if the user has a winner

    button_states, current_state_index, winner_found_game_ended = get_user_game_state(
        user_id
    )

    buttons = [
        Button(
            f"{text if text is not None else '.'}",
            cls="tic-button-disabled"
            if (text is not None) or winner_found_game_ended
            else "tic-button",
            hx_get=f"/on_click?index={idx}&user_id={user_id}",
            disabled=True if (text is not None) or winner_found_game_ended else False,
            hx_target=".buttons-div",
            hx_swap="outerHTML",
        )
        for idx, text in enumerate(button_states[current_state_index])
    ]

    board = Div(
        Div(winner, cls="justify-self-center"),
        Div(*buttons, cls="grid grid-cols-3 grid-rows-3"),
        cls="buttons-div font-bevan text-white font-light grid justify-center",
    )
    return board


@app.get("/restart")
def render_board(user_id: str):
    """Restart the game for a specific user."""
    # Reset game state for the user
    button_states_dict[user_id] = [[None for _ in range(9)] for _ in range(9)]
    current_state_index_dict[user_id] = -1
    winner_found_game_ended_dict[user_id] = False

    buttons = [
        Button(
            ".",
            cls="tic-button",
            hx_get=f"/on_click?index={i}&user_id={user_id}",
            hx_swap="outerHTML",
            hx_target=".buttons-div",
        )
        for i, _ in enumerate(button_states_dict[user_id][current_state_index_dict[user_id]])
    ]

    return Div(
        Div("Player X starts the game", cls="font-bevan text-white justify-self-center"),
        Div(*buttons, cls="grid grid-cols-3 grid-rows-3"),
        cls="buttons-div grid",
    )


# ---------------------------------------------Main Page --------------------------------------------
@app.get("/")
def main():
    user_id = uuid.uuid4()
    return Div(
        Div(
            H1("Tic Tac Toe!", cls="font-bevan text-5xl text-white"),
            P(
                "A FastHTML app by Adedara Adeloro",
                cls="font-bevan text-custom-blue font-light",
            ),
            cls="m-14",
        ),
        Div(
            render_board(user_id),  # Render buttons for the specific user
            Div(
                Button(
                    "Restart!",
                    cls="restart-button",
                    hx_get=f"/restart?user_id={user_id}",
                    hx_target=".buttons-div",
                    hx_swap="outerHTML",
                    disabled=False,
                ),
                cls="flex flex-col items-center justify-center m-10",
            ),
            cls="flex flex-col items-center justify-center",
        ),
        cls="justify-center items-center h-screen bg-custom-background",
    )


serve()
