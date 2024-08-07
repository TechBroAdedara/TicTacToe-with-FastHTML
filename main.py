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
from icecream import ic

style = Style(
    """
            body{
                min-height: 100vh;
                margin:0;
                background-color: #1A1A1E;
                display:grid;

            
            }"""
)
script = Script(src="/src/htmx.min.js")
css_with_tailwind = Link(rel="stylesheet", href="/src/output.css")

app, rt = fast_app(
    routes=[Mount("/src", StaticFiles(directory="src"), name="src")],
    hdrs=(css_with_tailwind, style, script),
    pico=False,
    live=True,
)

current_state_index = -1
button_states = [[None for _ in range(9)] for _ in range(9)]
win_states = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
]


def check_win(player) -> bool:
    global button_states, current_state_index
    next_index = current_state_index + 1
    for cell_1, cell_2, cell_3 in win_states:
        if (
            button_states[current_state_index][cell_1] != None
            and button_states[current_state_index][cell_1]
            == button_states[current_state_index][cell_2]
            and button_states[current_state_index][cell_2]
            == button_states[current_state_index][cell_3]
        ):
            return f" {player} is the winner!"
    if all(value is not None for value in button_states[current_state_index]):
        return "No winner"


def handle_click(index: int):
    global button_states, current_state_index
    next_index = current_state_index + 1
    button_states[next_index] = button_states[current_state_index][:]

    if button_states[current_state_index][index] is None:
        if "X" not in button_states[current_state_index] or button_states[
            current_state_index
        ].count("X") <= button_states[current_state_index].count("O"):
            button_states[next_index][index] = "X"
        else:
            button_states[next_index][index] = "O"
    ic(button_states)
    current_state_index += 1
    return button_states[next_index][index]


@app.get("/on_click")  # On click, call helper function to alternate between X and O
def render_button(index: int):
    global button_states, current_state_index
    player = handle_click(index)
    button = Button(
        f"{player}",  # helper function: handle_click, which gives the button its value
        cls="tic-button-disabled",
        hx_get=f"/on_click?index={index}",
        disabled=True,
    )
    print(check_win(player))  # function that checks if there's a winner
    return button


# Rerenders the board if the restart button is clicked.
# Also responsible for initial rendering on board when webpage is reloaded
@app.post("/restart")
def restart_game():
    global button_states, current_state_index
    current_state_index = -1
    button_states = [[None for _ in range(9)] for _ in range(9)]
    # button component
    buttons = [
        Button(
            ".", cls="tic-button", hx_get=f"/on_click?index={i}", hx_swap="outerHTML"
        )
        for i, _ in enumerate(button_states[current_state_index])
    ]
    return Div(*buttons, cls="buttons-div grid grid-cols-3 grid-rows-3")


# @app.get("/test")
# def test():
#     return "<h1>Test</h1>"


@app.get("/")
def homepage():
    global button_states
    return Div(
        Div(
            H1("Tic Tac Toe!", cls="font-bevan text-5xl text-white"),
            P(
                "An app by Adedara Adeloro",
                cls="font-bevan text-custom-blue font-semibold",
            ),
            cls="m-14",
        ),
        Div(
            Div(
                restart_game(),  # render buttons initially.
                # Function name doesn't reflect operation, bear with me
            ),
            Div(
                Button("Go to state 1", cls="restart-button"),
                Button(
                    "Restart!",
                    cls="restart-button",
                    hx_post="/restart",
                    hx_target=".buttons-div",
                    hx_swap="outerHTML",
                    disabled=False,
                ),
                cls="flex flex-col items-center justify-center",
            ),
            cls="flex flex-col items-center justify-center",
        ),
        cls="justify-center items-center h-screen bg-custom-background",
    )


serve()
