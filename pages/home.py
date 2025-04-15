import asyncio
import time
from nicegui import ui
from component import theme
import itertools

from lib.ping import tcp_ping, web_ping

ERROR = {}
headers = {"User-Agent": "Mozilla 5.0"}
TIMER = 30


def create() -> None:

    @ui.page("/")
    def home():
        async def set_timer():
            ui_timer.interval = int(ui_input_timer.value) if ui_input_timer.value else 5

        async def make_request():
            web = []
            tcp = []
            row_id = table.row_key
            for row in table.rows:
                payload = (row.get(row_id), row.get("address"))
                if row.get("active") and row.get("protocol") == "WEB":
                    web.append(payload)
                if row.get("active") and row.get("protocol") == "TCP":
                    tcp.append((*payload, row.get("port")))

            results = await asyncio.gather(web_ping(web), tcp_ping(tcp))
            merged = list(itertools.chain(*results))
            time = await ui.run_javascript("new Date().toLocaleString()")
            ui_refresh.set_text(time)

            for id, resp in merged:
                index = next(
                    (i for i, item in enumerate(table.rows) if item.get(row_id) == id),
                    -1,
                )
                payload = {"color": "red"}
                if resp == None:
                    payload.update({"color": "green"})
                else:
                    if not ERROR.get(id):
                        ERROR.update({id: []})
                    ERROR.get(id).append({"timestamp": time.time(), "error": resp})

                payload.update({"error": len(ERROR.get(id, []))})
                table.rows[index].update(payload)
            table.update()

        with theme.frame():
            with ui.row().classes("items-center"):
                with ui.button_group():
                    ui.button("add", icon="add")
                    ui.button("Import", icon="upload", color="secondary")
                    ui.button("Export", icon="download", color="secondary")
                ui_input_timer = ui.number("Interval", value=TIMER).props(
                    "outlined dense"
                )
                ui.button("Set", icon="schedule", color="secondary", on_click=set_timer)
                ui_refresh = ui.label()

        ui.query(".nicegui-content").classes("absolute-full")
        columns = [
            {"name": "active", "label": "Active", "field": "active"},
            {
                "name": "name",
                "label": "Name",
                "field": "name",
                "required": True,
                "align": "left",
            },
            {
                "name": "address",
                "label": "Address",
                "field": "address",
                "sortable": True,
            },
            {"name": "status", "label": "Status", "field": "status", "sortable": True},
            {
                "name": "protocol",
                "label": "Protocol",
                "field": "protocol",
                "sortable": True,
            },
            {
                "name": "error",
                "label": "Error",
                "field": "error",
                "sortable": True,
            },
        ]
        rows = [
            {
                "name": "Google",
                "address": "https://google.com",
                "active": True,
                "id": 1,
                "protocol": "WEB",
                "color": "orange",
            },
            {
                "name": "Meta",
                "address": "https://facebook.com",
                "active": True,
                "id": 2,
                "protocol": "WEB",
                "color": "orange",
            },
            {
                "name": "Amazon",
                "address": "https://amazon.com",
                "active": False,
                "id": 3,
                "protocol": "WEB",
                "color": "grey",
            },
            {
                "name": "Google DNS",
                "address": "8.8.8.8",
                "active": True,
                "id": 4,
                "protocol": "TCP",
                "color": "orange",
                "port": 53,
            },
        ]
        table = ui.table(columns=columns, rows=rows, row_key="id").classes("fit")
        table.add_slot(
            "body-cell-active",
            r"""
                <q-td :props="props" auto-width>
                    <q-toggle v-model="props.row.active" unchecked-icon="clear" checked-icon="check" color="green" @update:model-value="$parent.$emit('toggle', props.row)" />
                </q-td>                                    
            """,
        )
        table.add_slot(
            "body-cell-status",
            r"""
                <q-td :props="props" auto-width>
                    <q-avatar :color="props.row.color" size="sm" />
                </q-td>                                    
            """,
        )

        def on_row_toggle(row):
            row_id = table.row_key
            row_data = row.args
            active = row_data.get("active")
            index = next(
                (
                    i
                    for i, item in enumerate(table.rows)
                    if item.get(row_id) == row_data.get(row_id)
                ),
                -1,
            )
            color = "orange" if active else "grey"
            table.rows[index].update({**row_data, "color": color, "active": active})
            table.update()

        table.on("toggle", on_row_toggle)
        ui_timer = ui.timer(TIMER, make_request)
