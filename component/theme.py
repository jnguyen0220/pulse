from contextlib import contextmanager
from nicegui import ui


@contextmanager
def frame():
    with ui.header().classes(replace="row items-center") as header:
        ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
            "flat color=white"
        )
        ui.label("Pulse").classes("font-bold")
    with ui.left_drawer(value=False).classes("bg-blue-100") as left_drawer:
        ui.label("Side menu")
    with ui.column().classes('w-full'):
        yield
