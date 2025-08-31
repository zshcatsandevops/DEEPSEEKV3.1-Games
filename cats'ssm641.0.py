from ursina import *
from ursina.prefabs.button import Button
from ursina.prefabs.first_person_controller import FirstPersonController

# --- App setup ---
app = Ursina()
window.size = (600, 400)        # Start windowed
window.borderless = False
window.fullscreen = False
window.title = "Ultra Mario 3D Bros"

# ============================
#   MAIN MENU
# ============================
def create_main_menu():
    # Reset camera to UI mode for main menu
    camera.orthographic = True
    camera.fov = 10
    camera.position = (0, 0, 0)
    camera.rotation = (0, 0, 0)
    
    # Unlock mouse for menu interaction
    mouse.locked = False
    mouse.visible = True
    
    camera.ui.background_color = color.cyan

    global title, start_btn, options_btn, quit_btn

    # Title
    title = Text("Ultra Mario 3D Bros",
                 origin=(0,0),
                 scale=3,
                 y=0.45,
                 color=color.yellow,
                 outline=2,
                 font='VeraMono.ttf')

    # Buttons
    start_btn = Button(text='START', color=color.orange, scale=(.35,.12), y=0.1)
    options_btn = Button(text='OPTIONS', color=color.lime, scale=(.35,.12), y=-0.10)
    quit_btn = Button(text='QUIT', color=color.red, scale=(.35,.12), y=-0.30)

    # Hover effects
    for btn in (start_btn, options_btn, quit_btn):
        btn.animate_x(0, duration=0.4 + 0.1 * [start_btn, options_btn, quit_btn].index(btn), curve=curve.out_elastic)
        btn.on_mouse_enter = lambda b=btn: setattr(b, 'scale', (0.39, 0.13))
        btn.on_mouse_exit = lambda b=btn: setattr(b, 'scale', (0.35, 0.12))

    # Button actions
    start_btn.on_click = launch_game
    options_btn.on_click = open_options
    quit_btn.on_click = quit_game


# ============================
#   GAME LAUNCH
# ============================
def launch_game():
    destroy_menu()
    camera.ui.background_color = color.black
    window.title = "Ultra Mario 3D Bros - Test Engine"

    # Example test world
    ground = Entity(model='plane', texture='white_cube', color=color.green, scale=20, collider='box')
    cube = Entity(model='cube', color=color.azure, scale=2, position=(2,1,2), collider='box')
    player = FirstPersonController()


# ============================
#   OPTIONS MENU - Mario Bros Arcade Style
# ============================
def open_options():
    destroy_menu()
    
    # Reset camera for 3D environment
    camera.orthographic = False
    camera.position = (0, 5, -10)
    camera.rotation_x = 20
    camera.fov = 60
    
    # Unlock mouse for interaction with 3D objects
    mouse.locked = False
    mouse.visible = True
    
    # Create the options room
    global option_room
    option_room = Entity(enabled=True)
    
    # Floor with checkered pattern (like Mario)
    option_floor = Entity(model='plane', texture='white_cube', scale=20, 
                         color=color.red, parent=option_room)
    option_floor.rotation_x = 90
    
    # Walls
    wall_positions = [(0, 0, 10), (0, 0, -10), (10, 0, 0), (-10, 0, 0)]
    for i, pos in enumerate(wall_positions):
        wall = Entity(model='cube', texture='white_cube', scale=(20, 10, 1), 
                     color=color.blue, position=pos, parent=option_room)
        if i >= 2:  # East and west walls
            wall.scale = (1, 10, 20)
    
    # Create Mario-style stereo system (like in Sunshine)
    stereo_base = Entity(model='cube', color=color.gray, scale=(3, 0.5, 1), 
                        position=(0, -3, 5), parent=option_room)
    
    # Speakers
    speaker_positions = [(-1, -2, 5), (1, -2, 5)]
    for pos in speaker_positions:
        speaker = Entity(model='cylinder', color=color.black, scale=(0.5, 0.8, 0.5), 
                        position=pos, parent=option_room)
    
    # Stereo buttons (that will function as our options)
    global stereo_buttons
    stereo_buttons = []
    button_positions = [(-0.8, -2.8, 5.1), (0, -2.8, 5.1), (0.8, -2.8, 5.1)]
    button_colors = [color.green, color.orange, color.red]
    button_texts = ["MUSIC", "FULL", "BACK"]
    
    for i, pos in enumerate(button_positions):
        btn = Button(text=button_texts[i], color=button_colors[i], scale=(0.5, 0.2), 
                    world_position=pos, parent=option_room, eternal=True)
        btn.world_scale = (0.5, 0.2, 0.1)
        btn.on_click = [toggle_music, toggle_fullscreen, back_to_main][i]
        stereo_buttons.append(btn)
    
    # Add some Mario-themed props
    Entity(model='cube', color=color.red, scale=(1, 1, 1), 
          position=(-5, -3, 5), texture='white_cube', parent=option_room)  # Mystery block
    Entity(model='sphere', color=color.yellow, scale=(0.8, 0.8, 0.8), 
          position=(5, -3, -5), parent=option_room)  # Coin
    
    # UI elements for options
    global opt_title, back_btn_ui
    opt_title = Text("OPTIONS ROOM", origin=(0,0), scale=2, y=0.4, 
                    color=color.yellow, outline=2, parent=camera.ui)
    
    # Add a back button in UI as well for easier access
    back_btn_ui = Button(text='BACK TO MENU', color=color.red, scale=(.25,.08), 
                        y=-0.4, parent=camera.ui)
    back_btn_ui.on_click = back_to_main


def toggle_music():
    # Find the music button by its text
    for btn in stereo_buttons:
        if btn.text == "MUSIC":
            if btn.color == color.green:
                btn.color = color.gray
                btn.text = "MUTE"
            else:
                btn.color = color.green
                btn.text = "MUSIC"
            break


def toggle_fullscreen():
    # Find the fullscreen button by its text
    for btn in stereo_buttons:
        if btn.text in ["FULL", "WIND"]:
            if btn.text == "FULL":
                btn.text = "WIND"
                btn.color = color.orange
                window.fullscreen = False
            else:
                btn.text = "FULL"
                btn.color = color.green
                window.fullscreen = True
            break


def back_to_main():
    destroy_options()
    create_main_menu()


# ============================
#   UTILITIES
# ============================
def destroy_menu():
    for e in (title, start_btn, options_btn, quit_btn):
        try: 
            destroy(e)
        except: 
            pass

def destroy_options():
    # Destroy 3D objects
    try: 
        destroy(option_room)
    except: 
        pass
    
    # Destroy UI elements
    for e in (opt_title, back_btn_ui):
        try: 
            destroy(e)
        except: 
            pass
    
    # Destroy stereo buttons
    try:
        for btn in stereo_buttons:
            destroy(btn)
    except:
        pass
    
    # Reset camera
    camera.position = (0, 0, 0)
    camera.rotation_x = 0


# ============================
#   QUIT GAME
# ============================
def quit_game():
    application.quit()


# ============================
#   RUN
# ============================
create_main_menu()
app.run()
