import dearpygui.dearpygui as gui
import time,glfw,win32con,win32gui,pymem,pymem.process
import OpenGL.GL as gl
import requests, threading, tkinter
import pygetwindow as gw
import mouse, keyboard, win32api,random
import math



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

except: 
    print('cannot get offsets')
    exit(0)





while True:
    try:
        print('getting cs2 process')
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        break
    
    except:
        print('waiting for cs2.exe')
        time.sleep(0.5)

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
    bone_pos_x, bone_pos_y = world_to_screen(view_matrix, boneX, boneY, boneZ, screenx, screeny)
    return [bone_pos_x, bone_pos_y]

def filter_pos(list_):
    if not list_:
        return None


    min_sum = float('inf')
    closest = None

    for element in list_:
        sum_abs = sum(abs(x) for x in element)

        if sum_abs < min_sum:
            min_sum = sum_abs
            closest = element
    return closest 


















def cheat():
    gl.glBegin(gl.GL_LINES)
    global view_matrix
    view_matrix = []
    for i in range(16):
        temp_mat_val = pm.read_float(client + dwViewMatrix + i * 4)
        view_matrix.append(temp_mat_val)

        local_player_pawn = pm.read_longlong(client + dwLocalPlayerPawn)

    try:
        local_player_team = pm.read_int(local_player_pawn + m_iTeamNum)
    except:
        return
    
    for i in range(64):
        entity = pm.read_longlong(client + dwEntityList)             
        if not entity:
            continue         
        list_entry = pm.read_longlong(entity + ((8 * (i & 0x7FFF) >> 9) + 16))
        if not list_entry:
            continue
        entity_controller = pm.read_longlong(list_entry + (120) * (i & 0x1FF))
        if not entity_controller:
            continue
        entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
        if not entity_controller_pawn:
            continue
        list_entry = pm.read_longlong(entity + (0x8 * ((entity_controller_pawn & 0x7FFF) >> 9) + 16))
        if not list_entry:
            continue
        entity_pawn_addr = pm.read_longlong(list_entry + (120) * (entity_controller_pawn & 0x1FF))
        if not entity_pawn_addr or entity_pawn_addr == local_player_pawn:
            continue
        entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
        if entity_alive != 256:
            continue
        entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
        if entity_team == local_player_team:
            continue
        global bone_matrix
        game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
        bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)




        try:

            head_pos_x = get_bone_pos(6)[0]
            head_pos_y = get_bone_pos(6)[1]
            leg_pos_y = get_bone_pos(28)[1]
            if gui.get_value('aim'):
                targets.append([head_pos_x,head_pos_y])
            
                    
            head_leg = abs(head_pos_y - leg_pos_y)
        
            
            
            gl.glColor3b(*(int(gui.get_value('color')[0] / 2), int(gui.get_value('color')[1] / 2), int(gui.get_value('color')[2] / 2)))


            if gui.get_value('esp'):
                gl.glVertex2f(head_pos_x - head_leg // 3, screeny - leg_pos_y)
                gl.glVertex2f(head_pos_x + head_leg // 3, screeny - leg_pos_y)
                gl.glVertex2f(head_pos_x - head_leg // 3, screeny - leg_pos_y)
                gl.glVertex2f(head_pos_x - head_leg // 3, screeny - head_pos_y)
                gl.glVertex2f(head_pos_x + head_leg // 3, screeny - leg_pos_y)
                gl.glVertex2f(head_pos_x + head_leg // 3, screeny - head_pos_y)
                gl.glVertex2f(head_pos_x - head_leg // 3, screeny - head_pos_y)
                gl.glVertex2f(head_pos_x + head_leg // 3, screeny - head_pos_y)

                gl.glColor3f(0.0, 0.0, 0.0)
                gl.glVertex2f(head_pos_x - head_leg // 3 - thick, screeny - leg_pos_y - thick)
                gl.glVertex2f(head_pos_x + head_leg // 3 + thick, screeny - leg_pos_y - thick)

                gl.glVertex2f(head_pos_x - head_leg // 3 - thick, screeny - leg_pos_y-thick)
                gl.glVertex2f(head_pos_x - head_leg // 3 - thick, screeny - head_pos_y+thick)

                gl.glVertex2f(head_pos_x + head_leg // 3 + thick, screeny - leg_pos_y-thick)
                gl.glVertex2f(head_pos_x + head_leg // 3 + thick, screeny - head_pos_y+thick)

                gl.glVertex2f(head_pos_x - head_leg // 3 - thick, screeny - head_pos_y + thick)
                gl.glVertex2f(head_pos_x + head_leg // 3 + thick, screeny - head_pos_y + thick)

                        
                gl.glVertex2f(head_pos_x - head_leg // 3 + thick, screeny - leg_pos_y + thick)
                gl.glVertex2f(head_pos_x + head_leg // 3 - thick, screeny - leg_pos_y + thick)

                gl.glVertex2f(head_pos_x - head_leg // 3 + thick, screeny - leg_pos_y+thick)
                gl.glVertex2f(head_pos_x - head_leg // 3 + thick, screeny - head_pos_y-thick)

                gl.glVertex2f(head_pos_x + head_leg // 3 - thick, screeny - leg_pos_y+thick)
                gl.glVertex2f(head_pos_x + head_leg // 3 - thick, screeny - head_pos_y-thick)

                gl.glVertex2f(head_pos_x - head_leg // 3 + thick, screeny - head_pos_y - thick)
                gl.glVertex2f(head_pos_x + head_leg // 3 - thick, screeny - head_pos_y - thick)

                    
                gl.glColor3b(*(int(gui.get_value('color')[0] / 2), int(gui.get_value('color')[1] / 2), int(gui.get_value('color')[2] / 2)))
            
                
            def draw_bone(bone1_id,bone2_id):
                gl.glVertex2f(get_bone_pos(bone1_id)[0], screeny - get_bone_pos(bone1_id)[1])
                gl.glVertex2f(get_bone_pos(bone2_id)[0], screeny - get_bone_pos(bone2_id)[1])
            
            if gui.get_value('aa'):
                draw_bone(1,5)
                draw_bone(5,8)
                draw_bone(8,9)
                draw_bone(9,11)
                draw_bone(5,13)
                draw_bone(13,14)
                draw_bone(14,16)
                draw_bone(1,23)
                draw_bone(23,24)
                draw_bone(1,26)
                draw_bone(26,27)

            

            if gui.get_value('hpbar'):
                
                entity_health = pm.read_int(entity_pawn_addr + m_iHealth)/100
                delta_hp = (leg_pos_y-head_pos_y)*entity_health
                
                gl.glColor3b(*(0, 120, 0))
                gl.glVertex2f(head_pos_x - head_leg // 3 - 5 - thick, screeny - leg_pos_y)
                gl.glVertex2f(head_pos_x - head_leg // 3 - 5 - thick, screeny - head_pos_y)

                gl.glColor3b(*(120, 0, 0))
                gl.glVertex2f(head_pos_x - head_leg // 3 - 5 - thick, screeny - head_pos_y)
                gl.glVertex2f(head_pos_x - head_leg // 3 - 5 - thick, screeny - leg_pos_y + delta_hp) 
                
                gl.glColor3b(*(int(gui.get_value('color')[0] / 2), int(gui.get_value('color')[1] / 2), int(gui.get_value('color')[2] / 2)))


            if pm.read_int(local_player_pawn + m_iIDEntIndex) > 0 and keyboard.is_pressed(gui.get_value('trkey')) and gui.get_value('trig'):
                mouse.click()

             

        except Exception:
            pass

        
    
    try:
        to_shot = []
        if gui.get_value('aim'):
            fov_radius = gui.get_value('aimfov')
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

            closest_target = None
            closest_distance = float('inf')
            for target in targets:
                distance_from_center = math.sqrt((target[0] - screenx / 2) ** 2 + (target[1] - screeny / 2) ** 2)
                if distance_from_center < fov_radius:
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
                        if gui.get_value('shaff') and abs(target_x_dist) <= 1 and abs(target_y_dist) <= 1:
                            time.sleep(0.001)
                            mouse.click()

                try:
                    gl.glVertex2d(screenx / 2, screeny / 2)
                    gl.glVertex2d(closest_target[0], screeny - closest_target[1])
                except:
                    pass
    except:None                


   
   
    targets.clear()
    gl.glEnd()
    
        
            







def main():
    print('ok')
    glfw.init()
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
    glfw.window_hint(glfw.FLOATING, True)
    glfw.window_hint(glfw.DECORATED, False)
    global window
    window = glfw.create_window(screenx, screeny, 'Crosshairlabrender', None, None)
    glfw.make_context_current(window)
    gl.glOrtho(0, screenx, 0, screeny, -1, 1)

    handle = win32gui.FindWindow(0, 'Crosshairlabrender')

    exStyle = win32gui.GetWindowLong(handle, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(handle, win32con.GWL_EXSTYLE, exStyle | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

    handle = win32gui.FindWindow(0, 'Sussyware cs2')

    while True:
        try:
            gw.getWindowsWithTitle(title='Counter-Strike 2')[0].activate()
            gw.getWindowsWithTitle(title='Sussyware cs2')[0].activate()
            break
        except:None

    while True:
        try:
            global thick
            thick = 1
            glfw.swap_buffers(window)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            glfw.poll_events()
            time.sleep(0.0000001)
            gl.glLineWidth(thick)
            
            cheat()
        
            if keyboard.is_pressed('ins'):
                while True:
                    try:
                        gw.getWindowsWithTitle(title='Sussyware cs2')[0].activate()
                        break
                    except:None
        except:None


        
            


def startmain():
    try:main()
    except:main()





gui.create_context()
gui.create_viewport(title='Sussyware cs2', width=400, height=400, decorated=True)
gui.setup_dearpygui()
gui.set_viewport_resizable(False)



def threads():
    threading.Thread(target=startmain, daemon=True).start()



with gui.window(label='Sussyware cs2', width=400,height=400,no_title_bar=True,no_resize=True, no_move=True, show=True, tag='mainwindow'):
    with gui.tab_bar(label='cross'): 
        with gui.tab(label='Visual'):
            with gui.group(horizontal=True):
                with gui.group(horizontal=False):
                    gui.add_checkbox(label='Box Esp',tag='esp')
                    gui.add_checkbox(label='Stick Esp',tag='aa')
                    gui.add_checkbox(label='HP Bar',tag='hpbar')
                gui.add_color_picker(label='color:',tag='color', default_value=[255.0,255.0,255.0,255.0],height=180,width=180)
        with gui.tab(label='Combat'):
            gui.add_input_text(label='trigger key', tag='trkey')
            gui.add_checkbox(label='legit triggerbot (can target objects like doors)',tag='trig')
            gui.add_separator()
            gui.add_slider_int(label='aim Fov',tag='aimfov',min_value=10,max_value=360,default_value=50)
            gui.add_slider_int(label='aim strenght',tag='strenght',min_value=1,max_value=5,default_value=2)
            gui.add_input_text(label='aim key', tag='aimkey')
            gui.add_checkbox(label='aimbot',tag='aim')
            gui.add_checkbox(label='shot after aim',tag='shaff')
            



gui.show_viewport()
threads()
gui.start_dearpygui()
gui.destroy_context()