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
button_states = ["."] * 9
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
game_in_progress = True


def check_win() -> bool:
    global button_statess
    for cell_1, cell_2, cell_3 in win_states:
        if (
            button_states[cell_1] != "."
            and button_states[cell_1] == button_states[cell_2]
            and button_states[cell_2] == button_states[cell_3]
        ):
            return "Winner"


@app.get("/declare_winner")
def declare_winner():
    print("Winner Called")
    return "There's a winner"


@app.get("/on_click")
def click_handler(index: int):
    global button_states, game_in_progress
    new_button_text = ""
    if button_states[index] == ".":
        button_states[index] = (
            "X"
            if "X" not in button_states
            or button_states.count("X") == button_states.count("O")
            else "O"
        )
        new_button_text = button_states[index]

    new_button_text = button_states[index]
    print(check_win())
    return Button(
        f"{new_button_text}",
        cls="tic-button-disabled",
        hx_get=f"/on_click?index={index}",
        disabled=True,
    )


@app.post("/restart")
def render_buttons():
    global button_states, game_in_progress
    game_in_progress = True
    button_states = ["."] * 9

    # button component
    buttons = [
        Button(
            ".", cls="tic-button", hx_get=f"/on_click?index={i}", hx_swap="outerHTML"
        )
        for i, _ in enumerate(button_states)
    ]
    return Div(*buttons, cls="buttons-div grid grid-cols-3 grid-rows-3")


@app.get("/test")
def test():
    return "<h1>Test</h1>"


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
                render_buttons(),
            ),
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
        cls="justify-center items-center h-screen bg-custom-background",
    )


serve()
