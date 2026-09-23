extends Control

# UI-only HTTP bridge.  It never starts, stops, or modifies rocket-agent.
const DEFAULT_ENDPOINT := "http://127.0.0.1:8000/chat"
const PET_TEXTURE := preload("res://assets/pet.png")

var endpoint := DEFAULT_ENDPOINT
var pet: TextureRect
var menu: Control
var panel: PanelContainer
var response_box: RichTextLabel
var prompt_input: LineEdit
var request: HTTPRequest
var drag_started := false
var press_position := Vector2.ZERO
var window_start := Vector2i.ZERO

func _ready() -> void:
	get_window().transparent_bg = true
	get_window().borderless = true
	get_window().always_on_top = true
	get_window().unresizable = true
	get_window().size = Vector2i(620, 720)
	load_preferences()
	build_pet()
	build_radial_menu()
	build_panel()
	request = HTTPRequest.new()
	add_child(request)
	request.request_completed.connect(_on_request_completed)

func build_pet() -> void:
	pet = TextureRect.new()
	pet.name = "RocketSprite"
	pet.texture = PET_TEXTURE
	pet.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	pet.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	pet.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	pet.mouse_filter = Control.MOUSE_FILTER_STOP
	pet.gui_input.connect(_on_pet_input)
	add_child(pet)

func build_radial_menu() -> void:
	menu = Control.new()
	menu.name = "RocketContextMenu"
	menu.position = Vector2(310, 385)
	menu.size = Vector2(1, 1)
	menu.visible = false
	menu.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(menu)
	var entries := [["Chat", Vector2(-118, -90)], ["Tools", Vector2(98, -90)], ["Settings", Vector2(-124, 58)], ["About", Vector2(104, 58)], ["Exit", Vector2(0, 142)]]
	for entry in entries:
		var button := Button.new()
		button.name = entry[0] + "Button"
		button.text = entry[0]
		button.position = entry[1] - Vector2(48, 19)
		button.size = Vector2(96, 38)
		button.tooltip_text = entry[0]
		button.add_theme_font_size_override("font_size", 14)
		button.pressed.connect(_on_menu_action.bind(entry[0]))
		menu.add_child(button)

func build_panel() -> void:
	panel = PanelContainer.new()
	panel.name = "CompactPanel"
	panel.position = Vector2(28, 380)
	panel.size = Vector2(564, 305)
	panel.visible = false
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	var style := StyleBoxFlat.new()
	style.bg_color = Color("182033ed")
	style.border_color = Color("ff7b36")
	style.set_border_width_all(2)
	style.corner_radius_top_left = 14; style.corner_radius_top_right = 14
	style.corner_radius_bottom_left = 14; style.corner_radius_bottom_right = 14
	style.content_margin_left = 16; style.content_margin_right = 16
	style.content_margin_top = 14; style.content_margin_bottom = 14
	panel.add_theme_stylebox_override("panel", style)
	add_child(panel)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 8)
	panel.add_child(box)
	var title := Label.new(); title.name = "PanelTitle"; title.add_theme_font_size_override("font_size", 18)
	box.add_child(title)
	response_box = RichTextLabel.new(); response_box.name = "PanelContent"; response_box.bbcode_enabled = true
	response_box.fit_content = false; response_box.custom_minimum_size = Vector2(0, 170)
	box.add_child(response_box)
	var row := HBoxContainer.new(); box.add_child(row)
	prompt_input = LineEdit.new(); prompt_input.name = "ChatInput"; prompt_input.placeholder_text = "Ask Rocket…"
	prompt_input.size_flags_horizontal = Control.SIZE_EXPAND_FILL; prompt_input.text_submitted.connect(_send_chat)
	row.add_child(prompt_input)
	var send := Button.new(); send.text = "Send"; send.pressed.connect(_send_chat.bind("")); row.add_child(send)
	var close := Button.new(); close.text = "×"; close.tooltip_text = "Close"; close.pressed.connect(func(): panel.visible = false); row.add_child(close)

func _on_pet_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			press_position = event.position
			window_start = get_window().position
			drag_started = false
		else:
			if not drag_started:
				menu.visible = not menu.visible
				if menu.visible: panel.visible = false
	if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
		var delta := event.position - press_position
		if delta.length() > 4.0: drag_started = true
		if drag_started: get_window().position = window_start + Vector2i(delta)

func _on_menu_action(action: String) -> void:
	menu.visible = false
	match action:
		"Chat": show_chat()
		"Tools": show_info("Tools", "[b]Tools[/b]\nRocket is ready to expose companion tools here. This desktop UI does not change the existing Python agent.")
		"Settings": show_settings()
		"About": show_info("About Rocket", "[b]Rocket[/b] is a transparent, always-on-top desktop companion built with Godot 4.")
		"Exit": get_tree().quit()

func show_chat() -> void:
	panel.visible = true
	panel.get_node("VBoxContainer/PanelTitle").text = "Chat with Rocket"
	response_box.text = "[color=#a7c8ff]Endpoint:[/color] " + endpoint + "\n\nType a message and press Enter."
	prompt_input.visible = true
	prompt_input.grab_focus()

func show_settings() -> void:
	panel.visible = true
	panel.get_node("VBoxContainer/PanelTitle").text = "Settings"
	response_box.text = "[b]Backend endpoint[/b]\n" + endpoint + "\n\nEdit res://rocket_settings.json to point this UI at your existing rocket-agent HTTP route. Expected request body: {\\\"message\\\": \\\"…\\\"}."
	prompt_input.visible = false

func show_info(title: String, body: String) -> void:
	panel.visible = true
	panel.get_node("VBoxContainer/PanelTitle").text = title
	response_box.text = body
	prompt_input.visible = false

func _send_chat(submitted: String = "") -> void:
	var message := submitted if not submitted.is_empty() else prompt_input.text.strip_edges()
	if message.is_empty(): return
	prompt_input.clear()
	response_box.text = "[color=#a7c8ff]Rocket is thinking…[/color]"
	var headers := PackedStringArray(["Content-Type: application/json", "Accept: application/json"])
	var result := request.request(endpoint, headers, HTTPClient.METHOD_POST, JSON.stringify({"message": message}))
	if result != OK: response_box.text = "[color=#ff9b7a]Could not start HTTP request (%s). Check the endpoint in rocket_settings.json.[/color]" % result

func _on_request_completed(result: int, code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	if result != HTTPRequest.RESULT_SUCCESS:
		response_box.text = "[color=#ff9b7a]Rocket-agent is unreachable. Confirm it is running at:\n%s[/color]" % endpoint
		return
	var text := body.get_string_from_utf8()
	var parsed = JSON.parse_string(text)
	if typeof(parsed) == TYPE_DICTIONARY:
		text = str(parsed.get("response", parsed.get("message", parsed.get("content", text))))
	response_box.text = "[b]Rocket[/b]\n" + text.replace("[", "\\[")
	if code < 200 or code >= 300: response_box.text = "[color=#ff9b7a]HTTP %d[/color]\n%s" % [code, response_box.text]

func load_preferences() -> void:
	var file := FileAccess.open("res://rocket_settings.json", FileAccess.READ)
	if file == null: return
	var values = JSON.parse_string(file.get_as_text())
	if typeof(values) == TYPE_DICTIONARY and values.has("agent_endpoint"):
		endpoint = str(values.agent_endpoint)
