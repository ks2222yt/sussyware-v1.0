import dearpygui.dearpygui as gui
import time,glfw,win32con,win32gui,pymem,pymem.process
import OpenGL.GL as gl
import threading, tkinter
import pygetwindow as gw
import mouse, keyboard, win32api
import math, requests



screenx = tkinter.Tk().winfo_screenwidth()
screeny = tkinter.Tk().winfo_screenheight()

targets = []

print('getting offsets')





try:
    offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
    client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
    dwEntityList = offsets['client.dll']['dwEntityList']
    dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
    dwViewMatrix = offsets['client.dll']['dwViewMatrix']
    m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
    m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
    m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
    m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
    m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
    m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
    m_iIDEntIndex = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_iIDEntIndex']

    print("dwEntityList =",dwEntityList)
    print("dwLocalPlayerPawn =",dwLocalPlayerPawn)
    print("dwViewMatrix =",dwViewMatrix)
    print("m_iTeamNum =",m_iTeamNum)
    print("m_lifeState =",m_lifeState)
    print("m_pGameSceneNode =",m_pGameSceneNode)
    print("m_modelState =",m_modelState)
    print("m_hPlayerPawn =",m_hPlayerPawn)
    print("m_iHealth =",m_iHealth)
    print("m_iIDEntIndex =",m_iIDEntIndex)


except: 
    print('cannot get offsets')
    exit(0)


print('getting cs2 process')
try:
    pm = pymem.Pymem("cs2.exe")
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
except:
    while True:
        try:
            pm = pymem.Pymem("cs2.exe")
            client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
            break
        
        except:
            print('waiting for cs2.exe')
            time.sleep(2)

bone_pairs = [
    (1, 5), (5, 8), (8, 9), (9, 11),
    (5, 13), (13, 14), (14, 16),
    (1, 23), (23, 24), (1, 26), (26, 27)
]

class calcs:
    def world_to_screen(matrix, posx, posy, posz, width, height):
        screenW = (matrix[12] * posx) + (matrix[13] * posy) + (matrix[14] * posz) + matrix[15]
        if screenW > 0.001:
            screenX = (matrix[0] * posx) + (matrix[1] * posy) + (matrix[2] * posz) + matrix[3]
            screenY = (matrix[4] * posx) + (matrix[5] * posy) + (matrix[6] * posz) + matrix[7]

            camX = width / 2
            camY = height / 2

            x = camX + (camX * screenX / screenW)//1
            y = camY - (camY * screenY / screenW)//1

            return x, y
        return -999,-999

    def get_bone_pos(bone_id):
        boneX = pm.read_float(bone_matrix + bone_id * 0x20)
        boneY = pm.read_float(bone_matrix + bone_id * 0x20 + 0x4)
        boneZ = pm.read_float(bone_matrix + bone_id * 0x20 + 0x8)          
        bone_pos_x, bone_pos_y = calcs.world_to_screen(view_matrix, boneX, boneY, boneZ, screenx, screeny)
        return [bone_pos_x, bone_pos_y]

class combat:
    def aimbot(targets):
        gl.glColor3b(*(int(gui.get_value('aimcolor')[0] / 2), int(gui.get_value('aimcolor')[1] / 2), int(gui.get_value('aimcolor')[2] / 2)))
        try:
            to_shot = []
            fovcheck_status = gui.get_value('fovcheck')
            fov_radius = gui.get_value('aimfov')
            
            if fovcheck_status:
                num_segments = 100
                angle_step = 2 * math.pi / num_segments
                for i in range(num_segments):
                    angle1 = i * angle_step
                    angle2 = (i + 1) * angle_step
                    x1 = fov_radius * math.cos(angle1)
                    y1 = fov_radius * math.sin(angle1)
                    x2 = fov_radius * math.cos(angle2)
                    y2 = fov_radius * math.sin(angle2)
                    gl.glVertex2d(screenx / 2 + x1, screeny / 2 - y1)
                    gl.glVertex2d(screenx / 2 + x2, screeny / 2 - y2)

            if targets is not None:

                closest_target = None
                closest_distance = float('inf')

                for target in targets:
                    distance_from_center = math.sqrt((target[0] - screenx / 2) ** 2 + (target[1] - screeny / 2) ** 2)
                    
                    if (fovcheck_status and distance_from_center < fov_radius) or not fovcheck_status:
                        if target not in to_shot:
                            to_shot.append(target)
                        
                        if distance_from_center < closest_distance:
                            closest_distance = distance_from_center
                            closest_target = target
                
                if closest_target:
                    target_x_dist = int(closest_target[0] - screenx / 2)
                    target_y_dist = int(closest_target[1] - screeny / 2)
                    
                    for xd in range(gui.get_value('strenght')):
                        if keyboard.is_pressed(gui.get_value('aimkey')):
                            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, target_x_dist, target_y_dist, 0, 0)
                            if gui.get_value('shaff') and abs(target_x_dist) <= 2 and abs(target_y_dist) <= 2:
                                mouse.click()

                try:
                    if closest_target:
                        gl.glVertex2d(screenx / 2, screeny / 2)
                        gl.glVertex2d(closest_target[0], screeny - closest_target[1])
                except:
                    pass

        except:
            None   
    def triggerbot():
        if pm.read_int(local_player_pawn + m_iIDEntIndex) > 0 and keyboard.is_pressed(gui.get_value('trkey')):
            mouse.click()

class esp:
    def tracers(target_x, target_y, from_x, from_y):
        gl.glColor3b(*(int(gui.get_value('arrcolor')[0] / 2), int(gui.get_value('arrcolor')[1] / 2), int(gui.get_value('arrcolor')[2] / 2)))
        if gui.get_value('tractype') == 'arrows':
            distance_from_center=70
            dx = target_x - from_x
            dy = target_y - from_y

            distance_to_target = math.sqrt(dx * dx + dy * dy)

            arrow_length = 30

            if distance_to_target < distance_from_center:
                return

            dx /= distance_to_target
            dy /= distance_to_target

            base_x = from_x + dx * distance_from_center
            base_y = from_y + dy * distance_from_center

            tip_x = base_x - dx * arrow_length
            tip_y = base_y - dy * arrow_length

            arrowhead_width = 20

            perp_dx = -dy
            perp_dy = dx

            left_x = tip_x + perp_dx * (arrowhead_width / 2)
            left_y = tip_y + perp_dy * (arrowhead_width / 2)
            right_x = tip_x - perp_dx * (arrowhead_width / 2)
            right_y = tip_y - perp_dy * (arrowhead_width / 2)

            gl.glEnd()
            gl.glBegin(gl.GL_TRIANGLES)

            gl.glVertex2f(base_x, base_y)
            gl.glVertex2f(left_x, left_y)
            gl.glVertex2f(right_x, right_y)

            gl.glEnd()
            gl.glBegin(gl.GL_LINES)
        elif gui.get_value('tractype') == 'default':
            gl.glVertex2f(from_x,from_y)
            gl.glVertex2f(target_x,target_y)
  
    def BoxEsp(head_pos_x,head_pos_y,leg_pos_y,head_leg):
        gl.glColor3b(*(int(gui.get_value('boxcolor')[0] / 2), int(gui.get_value('boxcolor')[1] / 2), int(gui.get_value('boxcolor')[2] / 2)))
        
        if gui.get_value('boxtype')== '1':
            gl.glVertex2f(head_pos_x - head_leg // 3 -1, screeny - leg_pos_y)
            gl.glVertex2f(head_pos_x + head_leg // 3, screeny - leg_pos_y)
            gl.glVertex2f(head_pos_x - head_leg // 3, screeny - leg_pos_y)
            gl.glVertex2f(head_pos_x - head_leg // 3, screeny - head_pos_y)
            gl.glVertex2f(head_pos_x + head_leg // 3, screeny - leg_pos_y)
            gl.glVertex2f(head_pos_x + head_leg // 3, screeny - head_pos_y)
            gl.glVertex2f(head_pos_x - head_leg // 3, screeny - head_pos_y)
            gl.glVertex2f(head_pos_x + head_leg // 3, screeny - head_pos_y)
        
        elif gui.get_value('boxtype')== '2':
            line_length = (head_leg // 5)

            gl.glVertex2f(head_pos_x - head_leg // 3 - 1, screeny - head_pos_y)
            gl.glVertex2f(head_pos_x - head_leg // 3 - 1 + line_length, screeny - head_pos_y)

            gl.glVertex2f(head_pos_x + head_leg // 3 - line_length, screeny - head_pos_y)
            gl.glVertex2f(head_pos_x + head_leg // 3, screeny - head_pos_y)

            gl.glVertex2f(head_pos_x - head_leg // 3 - 1, screeny - leg_pos_y)
            gl.glVertex2f(head_pos_x - head_leg // 3 - 1 + line_length, screeny - leg_pos_y)

            gl.glVertex2f(head_pos_x + head_leg // 3 - line_length, screeny - leg_pos_y)
            gl.glVertex2f(head_pos_x + head_leg // 3, screeny - leg_pos_y)

            gl.glVertex2f(head_pos_x - head_leg // 3, screeny - head_pos_y)
            gl.glVertex2f(head_pos_x - head_leg // 3, screeny - head_pos_y - line_length)

            gl.glVertex2f(head_pos_x - head_leg // 3, screeny - leg_pos_y + line_length)
            gl.glVertex2f(head_pos_x - head_leg // 3, screeny - leg_pos_y)

            gl.glVertex2f(head_pos_x + head_leg // 3, screeny - head_pos_y)
            gl.glVertex2f(head_pos_x + head_leg // 3, screeny - head_pos_y - line_length)

            gl.glVertex2f(head_pos_x + head_leg // 3, screeny - leg_pos_y + line_length)
            gl.glVertex2f(head_pos_x + head_leg // 3, screeny - leg_pos_y)

    def draw_bone(bone1_id, bone2_id):
        bone1 = calcs.get_bone_pos(bone1_id)
        bone2 = calcs.get_bone_pos(bone2_id)
        gl.glVertex2f(bone1[0], screeny - bone1[1])
        gl.glVertex2f(bone2[0], screeny - bone2[1])

    def fillbox(head_pos_x,head_pos_y,leg_pos_y,head_leg):
        
        gl.glEnd()

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glColor4f(0, 0, 0, 0.5)

        gl.glBegin(gl.GL_QUADS)

        gl.glVertex2f(head_pos_x + head_leg//3,screeny - leg_pos_y)

        gl.glVertex2f(head_pos_x - head_leg//3,screeny - leg_pos_y) 

        gl.glVertex2f(head_pos_x - head_leg//3,screeny - head_pos_y) 
                
        gl.glVertex2f(head_pos_x + head_leg//3,screeny - head_pos_y)
                
        gl.glEnd()

        gl.glBegin(gl.GL_LINES)
    
    def HPbar(head_pos_x,head_pos_y,leg_pos_y,head_leg,entity_health):
        
        delta_hp = (leg_pos_y-head_pos_y)*entity_health
                
        gl.glColor3b(*(0, 120, 0))
        gl.glVertex2f(head_pos_x - head_leg // 3 - 5 - thick, screeny - leg_pos_y)
        gl.glVertex2f(head_pos_x - head_leg // 3 - 5 - thick, screeny - head_pos_y)

        gl.glColor3b(*(120, 0, 0))
        gl.glVertex2f(head_pos_x - head_leg // 3 - 5 - thick, screeny - head_pos_y)
        gl.glVertex2f(head_pos_x - head_leg // 3 - 5 - thick, screeny - leg_pos_y + delta_hp) 



def mainloop():
    gl.glBegin(gl.GL_LINES)
    
    global view_matrix, local_player_pawn
    view_matrix = []
    
    for i in range(16):
        try:
            temp_mat_val = pm.read_float(client + dwViewMatrix + i * 4)
            view_matrix.append(temp_mat_val)

            local_player_pawn = pm.read_longlong(client + dwLocalPlayerPawn)
        except:None

    try:
        local_player_team = pm.read_int(local_player_pawn + m_iTeamNum)
    except:
        return
    
    for i in range(64):
        try:
            entity = pm.read_longlong(client + dwEntityList)             
            if not entity:continue         
            
            list_entry = pm.read_longlong(entity + ((8 * (i & 0x7FFF) >> 9) + 16))
            
            if not list_entry:continue
            
            entity_controller = pm.read_longlong(list_entry + (120) * (i & 0x1FF))
            
            if not entity_controller:continue
            
            entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
            
            if not entity_controller_pawn:continue
            
            list_entry = pm.read_longlong(entity + (0x8 * ((entity_controller_pawn & 0x7FFF) >> 9) + 16))
            
            if not list_entry:continue
            
            entity_pawn = pm.read_longlong(list_entry + (120) * (entity_controller_pawn & 0x1FF))
            
            if not entity_pawn or entity_pawn == local_player_pawn:continue
            
            entity_alive = pm.read_int(entity_pawn + m_lifeState)
            
            if entity_alive != 256:continue
            
            entity_team = pm.read_int(entity_pawn + m_iTeamNum)
            
            if gui.get_value('tcheck') or gui.get_value('tcheck1'):
                if entity_team == local_player_team:continue
            if pm.read_int(entity_pawn + m_iHealth) < 1:continue
            
            
            global bone_matrix
            game_scene = pm.read_longlong(entity_pawn + m_pGameSceneNode)
            bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
        except:None


        try:
            
            head_pos_x = calcs.get_bone_pos(6)[0]
            head_pos_y = calcs.get_bone_pos(6)[1]
            leg_pos_y = calcs.get_bone_pos(28)[1]


            if gui.get_value('aim') and head_pos_x != -999 and head_pos_y != -999:
                targets.append([head_pos_x,head_pos_y,entity_pawn])
            
            if targets != []:
                
                if head_pos_x == -999 and head_pos_y == -999:
                    continue

                head_leg = abs(head_pos_y - leg_pos_y)


                if gui.get_value('fillbox'):
                    esp.fillbox(head_pos_x,head_pos_y,leg_pos_y,head_leg)
            
                if gui.get_value('esp'):
                    esp.BoxEsp(head_pos_x,head_pos_y,leg_pos_y,head_leg)
                
                if gui.get_value('tracs'):
                    targx = head_pos_x
                    fromx = screenx/2
                    if gui.get_value('targtype') == 'Head':
                        targy = screeny-head_pos_y
                    elif gui.get_value('targtype') == 'Leg':
                        targy = screeny-leg_pos_y
                        
                    if gui.get_value('tracfrom') == 'Middle':
                        fromy = screeny/2
                    elif gui.get_value('tracfrom') == 'Up':
                        fromy = screeny
                    elif gui.get_value('tracfrom') == 'Down':
                        fromy = 0
                        
                    esp.tracers(targx,targy,fromx,fromy)

                if gui.get_value('hpbar'):
                    esp.HPbar(head_pos_x,head_pos_y,leg_pos_y,head_leg,pm.read_int(entity_pawn + m_iHealth)/100)

                if gui.get_value('bonesp'):
                    gl.glColor3b(*(int(gui.get_value('bonecolor')[0] / 2), int(gui.get_value('bonecolor')[1] / 2), int(gui.get_value('bonecolor')[2] / 2)))
                    for bone1_id, bone2_id in bone_pairs:
                            esp.draw_bone(bone1_id, bone2_id)
 
 
        except:None

    if gui.get_value('aim'):
        combat.aimbot(targets)
    
    if gui.get_value('trig'):
        combat.triggerbot()
    print(targets)
    targets.clear()
    gl.glEnd()



def main():
    glfw.init()
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
    glfw.window_hint(glfw.FLOATING, True)
    glfw.window_hint(glfw.DECORATED, False)
    global window
    window = glfw.create_window(screenx, screeny, 'sussyware', None, None)
    glfw.make_context_current(window)
    gl.glOrtho(0, screenx, 0, screeny, -1, 1)

    handle = win32gui.FindWindow(0, 'sussyware')

    exStyle = win32gui.GetWindowLong(handle, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(handle, win32con.GWL_EXSTYLE, exStyle | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glMatrixMode(gl.GL_MODELVIEW)

    try:
        gw.getWindowsWithTitle(title='Counter-Strike 2')[0].activate()
        gw.getWindowsWithTitle(title='Sussyware cs2')[0].activate()
    except:None

    while True:
        try:
            global thick
            thick = 1
            glfw.swap_buffers(window)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            time.sleep(0.0000001)
            gl.glLineWidth(thick)
            
            mainloop()
            if keyboard.is_pressed('ins'):
                while True:
                    try:
                        gw.getWindowsWithTitle(title='Sussyware cs2')[0].restore()
                        gw.getWindowsWithTitle(title='Sussyware cs2')[0].activate()
                        break
                    except:None
        except:None



def gui_loop():
    while True:
        try:
            time.sleep(0.1)
            if gui.get_value('fovcheck'):
                gui.show_item('aimcolor')
                gui.show_item('aimfov')
            else: 
                gui.hide_item('aimcolor')
                gui.hide_item('aimfov')
            if gui.get_value('bodies'):
                gui.show_item('bodiescolor')
            else:
                gui.hide_item('bodiescolor')
        except:None

def threads():
    threading.Thread(target=gui_loop, daemon=True).start()
    threading.Thread(target=main, daemon=True).start()

def close_viewport():
    gui.stop_dearpygui()

def move_gui():
    while True:
        mouse_pos = mouse.get_position()
        gui.set_viewport_pos(pos=(mouse_pos[0]-250,mouse_pos[1]))
        if mouse.is_pressed('left'):break

def minimize_viewport():
    gui.minimize_viewport()

def change_tab(sender, data):
    gui.hide_item('tab1')
    gui.hide_item('tab2')
    gui.hide_item('tab3')

    if sender == 'tab1_button':
        gui.show_item('tab1')
    elif sender == 'tab2_button':
        gui.show_item('tab2')
    elif sender == 'tab3_button':
        gui.show_item('tab3')

gui.create_context()
gui.create_viewport(title='Sussyware cs2', width=500, height=500, decorated=False)
gui.setup_dearpygui()
gui.set_viewport_resizable(False)

with gui.window(label='', width=500, height=500, no_title_bar=True, no_resize=True, no_move=True, show=True, tag='mainwindow', no_scroll_with_mouse=True,no_scrollbar=True):
    gui.add_button(label="Sussyware cs2", callback=move_gui, width=400, height=20,pos=(0,5))
    gui.add_button(label="-", callback=minimize_viewport, width=50, height=20, pos=(400, 5))
    gui.add_button(label="X", callback=close_viewport, width=50, height=20, pos=(450, 5))
    gui.add_spacer(height=20)
    with gui.group(horizontal=True):
        with gui.group():
            gui.add_button(label="Visual", callback=change_tab, tag='tab1_button', width=100,height=30)
            gui.add_button(label="Combat", callback=change_tab, tag='tab2_button', width=100,height=30)     
            gui.add_button(label="Checks", callback=change_tab, tag='tab3_button', width=100,height=30)
        
        with gui.child_window(tag='tab1', show=True, height=500):          
            gui.add_text('Visual')
            with gui.collapsing_header(label='Box Esp'):
                gui.add_combo(label='Type',tag='boxtype',items=['1','2'],default_value='2')                
                gui.add_color_edit(label='', tag='boxcolor', default_value=[0.0, 0.0, 0.0, 255.0], height=180, width=180)
                gui.add_checkbox(label='Fill Box', tag='fillbox', default_value=False)
                gui.add_checkbox(label='Box Esp ', tag='esp', default_value=True)
            with gui.collapsing_header(label='Bone Esp'):
                gui.add_color_edit(label='', tag='bonecolor', default_value=[0.0, 255.0, 255.0, 255.0], height=180, width=180)
                gui.add_checkbox(label='Bone Esp', tag='bonesp', default_value=True)
            with gui.collapsing_header(label='Hp Bar'):
                gui.add_checkbox(label='HP Bar', tag='hpbar', default_value=True)
            with gui.collapsing_header(label='Tracers'):
                gui.add_combo(label='Type',tag='tractype',items=['default','arrows'],default_value='default')
                gui.add_combo(label='Target',tag='targtype',items=['Head','Leg'],default_value='Leg')
                gui.add_combo(label='From',tag='tracfrom',items=['Middle','Up','Down'],default_value='Middle') 
                gui.add_color_edit(label='', tag='arrcolor', default_value=[255.0, 255.0, 255.0, 255.0], height=180, width=180)
                gui.add_checkbox(label='Tracers', tag='tracs')


        with gui.child_window(tag='tab2', show=False, height=500):
            gui.add_text('Combat')
            gui.add_spacer(width=10)
            with gui.collapsing_header(label='Triggerbot Settings'):
                gui.add_input_text(label='Trigger Key', tag='trkey', hint='Enter Key')
                gui.add_checkbox(label='Legit Triggerbot', tag='trig')
                gui.add_separator()
            with gui.collapsing_header(label='Aimbot Settings'):
                gui.add_slider_int(label='Aim Fov', tag='aimfov', min_value=10, max_value=360, default_value=40)
                gui.add_color_edit(label='Fov Color', tag='aimcolor', default_value=[255.0, 255.0, 255.0, 255.0], height=180, width=160)
                gui.add_checkbox(label='Fov Check', tag='fovcheck', default_value=True)
                gui.add_slider_int(label='Aim Strength', tag='strenght', min_value=1, max_value=4, default_value=3)
                gui.add_input_text(label='Aimbot Key', tag='aimkey', default_value='v', hint='Enter Key')
                gui.add_checkbox(label='Aimbot', tag='aim', default_value=True)
                gui.add_checkbox(label='Shot After Aim', tag='shaff')
        
        with gui.child_window(tag='tab3', show=False, height=500):
            gui.add_text('Checks')
            gui.add_spacer(width=10)
            gui.add_checkbox(label='Team Check', tag='tcheck', default_value=True)




with gui.theme() as theme:
    with gui.theme_component(gui.mvAll):
        gui.add_theme_color(gui.mvThemeCol_WindowBg, (10, 10, 15, 255))
        gui.add_theme_color(gui.mvThemeCol_Button, (45, 55, 70, 255))
        gui.add_theme_color(gui.mvThemeCol_Text, (255, 255, 255, 255))
        gui.add_theme_color(gui.mvThemeCol_Tab, (40, 50, 65, 255))
        gui.add_theme_color(gui.mvThemeCol_FrameBg, (35, 45, 60, 255))
        gui.add_theme_color(gui.mvThemeCol_SliderGrab, (10, 10, 15, 255))
        gui.add_theme_color(gui.mvThemeCol_FrameBgActive, (55, 65, 80, 255))
        gui.add_theme_color(gui.mvThemeCol_TabActive, (55, 70, 85, 255))
        gui.add_theme_color(gui.mvThemeCol_TabHovered, (50, 60, 75, 255))
        gui.add_theme_color(gui.mvThemeCol_FrameBgHovered, (50, 60, 75, 255))
        gui.add_theme_color(gui.mvThemeCol_ButtonHovered, (80, 100, 120, 255))
        gui.add_theme_color(gui.mvThemeCol_SliderGrabActive, (255, 255, 255, 255))
        gui.add_theme_color(gui.mvThemeCol_CheckMark, (0, 180, 0, 255))
        gui.add_theme_color(gui.mvThemeCol_HeaderHovered, (60, 75, 90, 255))
        gui.add_theme_color(gui.mvThemeCol_ChildBg, (5, 5, 10, 255))
        gui.add_theme_color(gui.mvThemeCol_ButtonActive, (200, 220, 240, 255))
        gui.add_theme_color(gui.mvThemeCol_BorderShadow, 20)
        gui.add_theme_color(gui.mvThemeCol_Border, (30, 40, 55, 255))
        gui.add_theme_color(gui.mvThemeCol_Header, (40, 50, 65, 255))
        gui.add_theme_color(gui.mvThemeCol_HeaderHovered, (50, 60, 75, 255))

        
        gui.add_theme_style(gui.mvStyleVar_ChildRounding,3)
        gui.add_theme_style(gui.mvStyleVar_WindowBorderSize,5)
        gui.add_theme_style(gui.mvStyleVar_ChildBorderSize,2)
        gui.add_theme_style(gui.mvStyleVar_FrameRounding,0)




gui.bind_theme(theme)

gui.show_viewport()
threads()
gui.start_dearpygui()
gui.destroy_context()