import harfang as hg
import requests
import socket
from math import pi
from statistics import median
import math
from OrbitalCam import OrbitalController

str_error = "The robot is not connected"

# helpers
def clamp(v, v_min, v_max):
	return max(v_min, min(v, v_max))


def rangeadjust_clamp(k, a, b, u, v):
	return rangeadjust(clamp(k, a, b), a, b, u, v)


def rangeadjust(k, a, b, u, v):
	return (k - a) / (b - a) * (v - u) + u


def lerp(k, a, b):
	return a + (b - a) * k

# look for the poppy on the network
url = ""
try:
	url = "http://" + socket.gethostbyname('poppy.local') + ":6969"
except:
	print(str_error + ": "+url)

# initialize  Harfang
hg.InputInit()
hg.WindowSystemInit()

keyboard = hg.Keyboard()
mouse = hg.Mouse()

res_x, res_y = 1920, 1080

#initialize lists and variables for toggle button (swipe style)
mousexlist = []
mouseylist = []
has_switched = False
compliance_mode = False

win = hg.NewWindow("Harfang - Poppy", res_x, res_y, 32)#, hg.WV_Fullscreen)
hg.RenderInit(win)
hg.RenderReset(res_x, res_y, hg.RF_MSAA8X | hg.RF_FlipAfterRender | hg.RF_FlushAfterRender | hg.RF_MaxAnisotropy)

hg.AddAssetsFolder("resources_compiled")

# AAA render params
aaa_config = hg.ForwardPipelineAAAConfig()
aaa_config.temporal_aa_weight = 0.01
aaa_config.sample_count = 1
aaa_config.motion_blur = 0.01
aaa_config.exposure = 1.925
aaa_config.gamma = 2.45
pipeline_aaa = hg.CreateForwardPipelineAAAFromAssets("core", aaa_config)
pipeline = hg.CreateForwardPipeline()
res = hg.PipelineResources()

# load scene
scene = hg.Scene()
hg.LoadSceneFromAssets("poppy.scn", scene, res, hg.GetForwardPipelineInfo())

# load texture for the quads
target_tex = hg.LoadTextureFromAssets("point.png", 0)[0]
texture_point = hg.MakeUniformSetTexture("s_texTexture", target_tex, 0)

target_tex = hg.LoadTextureFromAssets("Asset_1.png", 0)[0]
texture_asset1 = hg.MakeUniformSetTexture("s_texTexture", target_tex, 0)

target_tex = hg.LoadTextureFromAssets("Asset_2.png", 0)[0]
texture_asset2 = hg.MakeUniformSetTexture("s_texTexture", target_tex, 0)

target_tex = hg.LoadTextureFromAssets("switch-on.png", 0)[0]
texture_on = hg.MakeUniformSetTexture("s_texTexture", target_tex, 0)

target_tex = hg.LoadTextureFromAssets("switch-off.png", 0)[0]
texture_off = hg.MakeUniformSetTexture("s_texTexture", target_tex, 0)


# load shaders
render_state_quad = hg.ComputeRenderState(hg.BM_Alpha, hg.DT_Less, hg.FC_Disabled)
render_state_quad_occluded = hg.ComputeRenderState(hg.BM_Alpha, hg.DT_Less, hg.FC_Disabled)
render_state_line = hg.ComputeRenderState(hg.BM_Opaque, hg.DT_Less, hg.FC_Disabled)
shader_rotator = hg.LoadProgramFromAssets("shaders/rotator")
shader_for_plane = hg.LoadProgramFromAssets("shaders/texture")
shader_for_line = hg.LoadProgramFromAssets("shaders/pos_rgb")
shader_font = hg.LoadProgramFromAssets("core/shader/font")
vtx_layout = hg.VertexLayoutPosFloatTexCoord0UInt8()
vtx_line_layout = hg.VertexLayoutPosFloatColorUInt8()

# load font
font = hg.LoadFontFromAssets("Roboto-Regular.ttf", 36, 1024, 1, "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ ¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ")
text_render_state = hg.ComputeRenderState(hg.BM_Alpha, hg.DT_Always, hg.FC_Disabled, False)
font_color = hg.MakeUniformSetValue("u_color", hg.Vec4(1.0, 0.75, 0.2, 1.0))
font_color_white = hg.MakeUniformSetValue("u_color", hg.Vec4(1.0, 1.0, 1.0, 1.0))
font_shadow = hg.MakeUniformSetValue("u_color", hg.Vec4(0.0, 0.0, 0.0, 1.0))

# array for each motor node and rotation axis choice
hg_motors = [
	{"n": scene.GetNode("bras_1"), "acc": 0, "v": 0, "axis": "Y", "lower_limit": -150, "upper_limit": 150, "new_position": 0.0, "quad_jauge_axis": hg.CreatePlaneModel(vtx_layout, 0.12, 0.12, 1, 1), "offset_slider": hg.Vec3(0, 0, 1), "offset_rotation": hg.Vec3(0, 0, 0), "axis_tex_big": True},
	{"n": scene.GetNode("bras_2"), "acc": 0, "v": 0, "axis": "X", "lower_limit": 90, "upper_limit": -125, "new_position": 0.0, "quad_jauge_axis": hg.CreatePlaneModel(vtx_layout, 0.03, 0.03, 1, 1), "offset_slider": hg.Vec3(1, 0, 0), "offset_rotation": hg.Vec3(-1.57, 1.57, 0), "axis_tex_big": False},
	{"n": scene.GetNode("bras_3"), "acc": 0, "v": 0, "axis": "X", "lower_limit": 90, "upper_limit": -90, "new_position": 0.0, "quad_jauge_axis": hg.CreatePlaneModel(vtx_layout, 0.03, 0.03, 1, 1), "offset_slider": hg.Vec3(1, 0, 0), "offset_rotation": hg.Vec3(-1.57, 1.57, 0), "axis_tex_big": False},
	{"n": scene.GetNode("bras_4"), "acc": 0, "v": 0, "axis": "Z", "lower_limit": -150, "upper_limit": 150, "new_position": 0.0, "quad_jauge_axis": hg.CreatePlaneModel(vtx_layout, 0.06, 0.06, 1, 1), "offset_slider": hg.Vec3(0, 1, 0), "offset_rotation": hg.Vec3(0, 0, 0), "axis_tex_big": True},
	{"n": scene.GetNode("bras_5"), "acc": 0, "v": 0, "axis": "X", "lower_limit": 90, "upper_limit": -90, "new_position": 0.0, "quad_jauge_axis": hg.CreatePlaneModel(vtx_layout, 0.03, 0.03, 1, 1), "offset_slider": hg.Vec3(1, 0, 0), "offset_rotation": hg.Vec3(-1.57, 0, 1.57), "axis_tex_big": False},
	{"n": scene.GetNode("bras_6"), "acc": 0, "v": 0, "axis": "X", "lower_limit": 110, "upper_limit": -90, "new_position": 0.0, "quad_jauge_axis": hg.CreatePlaneModel(vtx_layout, 0.03, 0.03, 1, 1), "offset_slider": hg.Vec3(1, 0, 0), "offset_rotation": hg.Vec3(-1.57, 0, 1.57), "axis_tex_big": False},
]

led_colors = [
	"off",
	"red",
	"green",
	"yellow",
	"blue",
	"pink",
	"cyan",
	"white"
]
led_current_motor_ping_pong = 0
led_current_motor_timer_ping_pong = 0
led_current_motor_way_ping_pong = 1
led_color = 1

timer_requests_not_overload = 0

# if there is no camera add one
cam = None
for n in scene.GetAllNodes():
	if n.GetCamera().IsValid():
		cam = n
		break

if cam is None:
	cam = scene.CreateNode()
	cam.SetName("Camera")
	cam.SetTransform(scene.CreateTransform())
	cam.GetTransform().SetWorld(hg.TransformationMat4(hg.Vec3(0, 1000, 0), hg.Vec3(0, 0, 0)))
	cam.SetCamera(scene.CreateCamera(0.1, 10000))

scene.SetCurrentCamera(cam)
cam_tgt = hg.Vec3(0, 0.9, 0)
cam_pos = cam.GetTransform().GetPos()
cam_rot = cam.GetTransform().GetRot()

# load shader imgui
imgui_prg = hg.LoadProgramFromAssets("core/shader/imgui")
imgui_img_prg = hg.LoadProgramFromAssets("core/shader/imgui_image")

hg.ImGuiInit(10, imgui_prg, imgui_img_prg)

app_clock = 0
app_status = "dancing"

def toggle_button(label, value, x, y):
	global has_switched
	mat = hg.TransformationMat4(hg.Vec3(x, y, 1), hg.Vec3(0, 0, 0), hg.Vec3(1, 1, 1))
	pos = hg.GetT(mat)
	axis_x = hg.GetX(mat) * 56
	axis_y = hg.GetY(mat) * 24

	toggle_vtx = hg.Vertices(vtx_layout, 4)
	toggle_vtx.Begin(0).SetPos(pos - axis_x - axis_y).SetTexCoord0(hg.Vec2(0, 1)).End()
	toggle_vtx.Begin(1).SetPos(pos - axis_x + axis_y).SetTexCoord0(hg.Vec2(0, 0)).End()
	toggle_vtx.Begin(2).SetPos(pos + axis_x + axis_y).SetTexCoord0(hg.Vec2(1, 0)).End()
	toggle_vtx.Begin(3).SetPos(pos + axis_x - axis_y).SetTexCoord0(hg.Vec2(1, 1)).End()
	toggle_idx = [0, 3, 2, 0, 2, 1]


	hg.DrawTriangles(view_id, toggle_idx, toggle_vtx, shader_for_plane, [], [texture_on if value else texture_off], render_state_quad)

	if mouse.Down(hg.MB_0):
		mousexlist.append(mouse.X())
		mouseylist.append(mouse.Y())
	else:
		mousexlist.clear()
		mouseylist.clear()
		has_switched = False

	if len(mousexlist) > 20:
		mousexlist.pop(0)
	if len(mouseylist) > 20:
		mouseylist.pop(0)

	if len(mouseylist) > 0:
		mouse_x = median(mousexlist)
		mouse_y = median(mouseylist)
		if mouse_x > pos.x - axis_x.x and mouse_x < pos.x + axis_x.x and mouse_y > pos.y - axis_y.y and mouse_y < pos.y + axis_y.y and not has_switched:
			value = True if not value else False
			has_switched = True
			mousexlist.clear()
			mouseylist.clear()

	mat = hg.TranslationMat4(hg.Vec3(pos.x + axis_x.x + 10, y - 10, 1))
	hg.SetS(mat, hg.Vec3(1, -1, 1))
	hg.DrawText(view_id,
				font,
				label, shader_font, "u_tex", 0,
				mat, hg.Vec3(0, 0, 0), hg.DTHA_Left, hg.DTVA_Top,
				[font_color_white], [], text_render_state)
	return value

buttonlist = [[100, res_y - 80]]

def is_switching():
	for i in buttonlist:
		mat = hg.TransformationMat4(hg.Vec3(i[0], i[1], 1), hg.Vec3(0, 0, 0), hg.Vec3(1, 1, 1))
		pos = hg.GetT(mat)
		axis_x = hg.GetX(mat) * 56
		axis_y = hg.GetY(mat) * 24
		if (mouse.X() > pos.x - axis_x.x - 10 and mouse.X() < pos.x + axis_x.x + 10 and mouse.Y() > pos.y - axis_y.y - 10 and mouse.Y() < pos.y + axis_y.y + 10 and mouse.Down(hg.MB_0)): # check if mouse is clicked and is within the button area + 10px on every side
				return True
	return False

def get_v_from_dancing(id_robot):
	elapsed_time = app_clock *0.5
	_amp = 1
	_freq = 0.5
	_offset = 0
	_phase = 0

	if id_robot == 0:
		_freq = 0.25
		_amp = 90.
	elif id_robot == 3:
		_freq = 0.25
		_amp = 90.
		_phase = 180.
	elif id_robot == 4:
		_freq = 0.8
		_amp = 30.
	elif id_robot == 5:
		_freq = 0.8
		_amp = 20.
		_phase = 180.
	else:
		_freq = 0.2
		_amp = 15.

	""" Compute the sin(t) where t is the elapsed time since the primitive has been started. """
	return _amp * math.sin(_freq * 2.0 * math.pi * elapsed_time + _phase * math.pi / 180.0) + _offset


# send value
if url != "":
	try:
		requests.get(url + "/reset-simulation")
	except:
		print("Robot not connected "+url)

# main loop
current_frame = 0
while not hg.ReadKeyboard().Key(hg.K_Escape):
	keyboard.Update()
	mouse.Update()
	dt = hg.TickClock()

	app_clock += hg.time_to_sec_f(dt)

	render_was_reset, res_x, res_y = hg.RenderResetToWindow(win, res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X | hg.RF_MaxAnisotropy)
	res_y = max(res_y, 16)
	
	if not is_switching(): # and hg.ImGuiIsWindowFocused() 
		world, cam_rot, cam_tgt, cam_pos = OrbitalController(keyboard, mouse, cam_pos, cam_rot, cam_tgt, dt, res_x, res_y)
		cam.GetTransform().SetWorld(world)

	scene.Update(dt)
	new_pass_views = hg.SceneForwardPipelinePassViewId()
	view_id = 0
	view_id, pass_ids = hg.SubmitSceneToPipeline(view_id, scene, hg.IntRect(0, 0, res_x, res_y), True, pipeline, res, pipeline_aaa, aaa_config, current_frame)

	view_state = scene.ComputeCurrentCameraViewState(hg.ComputeAspectRatioX(res_x, res_y))

	# api poppy
	url_set_motor_pos_registers = url + "/motors/set/registers/"
	url_set_motor_pos = url + "/motors/set/goto/"
	send_dt = 1/10 # send information to the poppy every send_dt

	# get values from the real robot
	if compliance_mode:
		timer_requests_not_overload += hg.time_to_sec_f(dt)
		if timer_requests_not_overload > send_dt:
			timer_requests_not_overload = 0

			if url != "":
				try:
					r = requests.get(url + "/motors/get/positions").text
					for id, m in enumerate(hg_motors):
						hg_m = hg_motors[id]
						hg_m["v"] = float(r.split(';')[id])
						if id==5: hg_m["v"] = -float(r.split(';')[id])	# send negative value for claw motor angle ()

				except:
					print("Robot not connected " + url)

	# set 3D mesh with the current motor pos
	for id, m in enumerate(hg_motors):
		hg_m = hg_motors[id]

		# check if we are getting value from the real root
		if compliance_mode:
			v = hg_m["v"]
		else:  # sending value to the real robot
			if app_status == "dancing":
				v = get_v_from_dancing(id)

		# led
		led_actual_color = "off"
		if led_current_motor_ping_pong == id:
			led_actual_color = led_colors[led_color]

		# send the next position to the robot
		if id == 5:
			url_set_motor_pos_registers += f"m{id + 1}:compliant:{'True' if compliance_mode else 'False'};m{id + 1}:led:{led_actual_color};"
			url_set_motor_pos += f"m{id + 1}:{-v}:{send_dt};"
		else:
			url_set_motor_pos_registers += f"m{id + 1}:compliant:{'True' if compliance_mode else 'False'};m{id + 1}:led:{led_actual_color};"
			url_set_motor_pos += f"m{id + 1}:{v}:{send_dt};"


		hg_m["acc"] = lerp(0.1, hg_m["acc"], clamp((hg_m["v"] - v) / (hg.time_to_sec_f(dt)**2), -9999, 9999))
		hg_m["v"] = v
		# set the position to the virtual robot
		rot = hg.Vec3(0, 0, 0)
		if hg_m["axis"] == "X":
			rot = hg.Vec3(-v*pi/180.0, 0, 0)
		elif hg_m["axis"] == "Y":
			rot = hg.Vec3(0, -v*pi/180.0, 0)
		elif hg_m["axis"] == "Z":
			rot = hg.Vec3(-1.57, 0, -v*pi/180.0)

		hg_m["n"].GetTransform().SetRot(rot)

	# check if we are getting value from the real root
	if not compliance_mode:
		# send value
		timer_requests_not_overload += hg.time_to_sec_f(dt)
		if timer_requests_not_overload > send_dt:
			timer_requests_not_overload = 0

			if url != "":
				try:
					requests.get(url_set_motor_pos[:-1])
				except:
					print("Robot not connected "+url)

	# led ping pong
	led_current_motor_timer_ping_pong += hg.time_to_sec_f(dt)
	if led_current_motor_timer_ping_pong > 1/5:
		led_current_motor_timer_ping_pong = 0
		led_current_motor_ping_pong += led_current_motor_way_ping_pong

		if led_current_motor_ping_pong <= 0:
			led_color += 1
			if led_color >= len(led_colors):
				led_color = 1

		if led_current_motor_ping_pong >= len(hg_motors)-1 or led_current_motor_ping_pong <= 0:
			led_current_motor_way_ping_pong *= -1

		if url != "":
			try:
				requests.get(url_set_motor_pos_registers[:-1])
			except:
				print("Robot not connected "+url)

	# draw ui
	view_id_scene_opaque = hg.GetSceneForwardPipelinePassViewId(pass_ids, hg.SFPP_Opaque)
	view_id_scene_alpha = hg.GetSceneForwardPipelinePassViewId(pass_ids, hg.SFPP_Transparent)

	cam_world = cam.GetTransform().GetWorld()

	# set 3D mesh with the current motor pos
	for id, m in enumerate(hg_motors):
		hg_m = hg_motors[id]
		v = hg_m["v"]

		# set the position to the virtual robot
		m_world = hg_m["n"].GetTransform().GetWorld()
		m_pos = hg.GetT(m_world)
		m_world_rot = hg.GetR(hg_m["n"].GetTransform().GetParent().GetTransform().GetWorld())
		m_world_scale = hg.GetS(m_world)

		if hg_m["offset_slider"].x == 1:
			m_pos += hg.GetX(m_world) * 0.03
		if hg_m["offset_slider"].y == 1:
			m_pos += hg.GetZ(m_world) * -0.015
		if hg_m["offset_slider"].z == 1:
			m_pos += hg.GetY(m_world) * 0.003

		# draw jauge in axis
		m_world = hg.TransformationMat4(m_pos, m_world_rot, m_world_scale) * hg.RotationMat4(hg_m["offset_rotation"])
		hg_m["centroid_jauge_world"] = m_world

		progress = hg.MakeUniformSetValue("uProgress", hg.Vec4(rangeadjust_clamp(v, -180, 180, 0, 100)/100, 0, 0, 0))

		hg.DrawModel(view_id_scene_alpha, hg_m["quad_jauge_axis"], shader_rotator, [progress], [texture_asset1], m_world, render_state_quad_occluded)

	# draw 2D jauge
	# set 2D view
	hg.SetViewFrameBuffer(view_id, hg.InvalidFrameBufferHandle)

	hg.SetViewRect(view_id, 0, 0, res_x, res_y)
	hg.SetViewClear(view_id, 0, 0, 1.0, 0)

	vs = hg.ComputeOrthographicViewState(hg.TranslationMat4(hg.Vec3(res_x / 2, res_y / 2, 0)), res_y, 0.1, 100, hg.Vec2(res_x / res_y, 1))
	hg.SetViewTransform(view_id, vs.view, vs.proj)

	for id, m in enumerate(hg_motors):
		hg_m = hg_motors[id]
		v = hg_m["v"]

		# percent from acceleration
		p = rangeadjust_clamp(abs(m["acc"]), 0, 9999, 0, 1)

		# texture quad
		quad_width = quad_height = res_y * 0.12
		pos_in_pixel = hg.iVec2(int(res_x - quad_width * 1.1), int((res_y * 0.05) + (res_y * 0.9)/len(hg_motors) * id + (quad_height * 1.2) / 2))

		#setup quad vertices
		mat = hg.TransformationMat4(hg.Vec3(pos_in_pixel.x, pos_in_pixel.y, 1), hg.Vec3(0, 0, 0), hg.Vec3(1, 1, 1))

		pos = hg.GetT(mat)
		axis_x = hg.GetX(mat) * quad_width / 2
		axis_y = hg.GetY(mat) * quad_height / 2

		quad_vtx = hg.Vertices(vtx_layout, 4)
		quad_vtx.Begin(0).SetPos(pos - axis_x - axis_y).SetTexCoord0(hg.Vec2(0, 1)).End()
		quad_vtx.Begin(1).SetPos(pos - axis_x + axis_y).SetTexCoord0(hg.Vec2(0, 0)).End()
		quad_vtx.Begin(2).SetPos(pos + axis_x + axis_y).SetTexCoord0(hg.Vec2(1, 0)).End()
		quad_vtx.Begin(3).SetPos(pos + axis_x - axis_y).SetTexCoord0(hg.Vec2(1, 1)).End()
		quad_idx = [0, 3, 2, 0, 2, 1]

		# draw quad
		progress = hg.MakeUniformSetValue("uProgress", hg.Vec4(rangeadjust_clamp(v, -180, 180, 0, 100)/100, 0, 0, 0))

		hg.DrawTriangles(view_id, quad_idx, quad_vtx, shader_rotator, [progress], [texture_asset2], render_state_quad)

		# # draw line in 2D
		vtx = hg.Vertices(vtx_line_layout, 2)
		motor_pos_2D = view_state.view * hg.ProjectToScreenSpace(view_state.proj, hg.GetT(hg_m["centroid_jauge_world"]), hg.Vec2(res_x, res_y))[1]
		# print(str(hg.GetT(hg_m["centroid_jauge_world"]).x) + ", " + str(hg.GetT(hg_m["centroid_jauge_world"]).y) + ", " + str(hg.GetT(hg_m["centroid_jauge_world"]).z))
		vtx.Begin(0).SetPos(motor_pos_2D).SetColor0(hg.Color.White).End()
		vtx.Begin(1).SetPos(hg.Vec3(pos_in_pixel.x - quad_width / 2, pos_in_pixel.y, 1)).SetColor0(hg.Color.White).End()

		hg.DrawLines(view_id, vtx, shader_for_line)

		# draw percent
		pos_in_pixel.x -= int(res_y / 35)
		pos_in_pixel.y -= 10
		mat = hg.TranslationMat4(hg.Vec3(pos_in_pixel.x, pos_in_pixel.y, 1))
		hg.SetS(mat, hg.Vec3(res_y / 1080, -res_y / 1080, res_y / 1080))

		hg.DrawText(view_id,
					font,
					'{n} °'.format(n = int(rangeadjust_clamp(v, -180, 180, 0, 360))), shader_font, "u_tex", 0,
					mat, hg.Vec3(0, 0, 0), hg.DTHA_Left, hg.DTVA_Top,
					[font_color_white], [], text_render_state)	

		# draw central point on motor
		quad_width = 8
		quad_height = 8
		pos_in_pixel = motor_pos_2D

		color = hg.MakeUniformSetValue("uTextureColor", hg.Vec4(-1.0, 0, 0, 1.0))

		hg.DrawTriangles(view_id, quad_idx, quad_vtx, shader_for_plane, [], [texture_point], render_state_quad)


	# if roboto was not found, add a red text to tell everybody
	if url == "":
		mat = hg.TranslationMat4(hg.Vec3(14, 48, 1))
		hg.SetS(mat, hg.Vec3(1, -1, 1))
		hg.DrawText(view_id,
					font,
					str_error, shader_font, "u_tex", 0,
					mat, hg.Vec3(0, 0, 0), hg.DTHA_Left, hg.DTVA_Top,
					[font_shadow], [], text_render_state)		
		mat = hg.TranslationMat4(hg.Vec3(15, 50, 1))
		hg.SetS(mat, hg.Vec3(1, -1, 1))
		hg.DrawText(view_id,
					font,
					str_error, shader_font, "u_tex", 0,
					mat, hg.Vec3(0, 0, 0), hg.DTHA_Left, hg.DTVA_Top,
					[font_color], [], text_render_state)

	compliance_mode = toggle_button("Compliance Mode ON" if compliance_mode else "Compliance Mode OFF", compliance_mode, 100, res_y - 80)

	view_id += 1


	current_frame = hg.Frame()
	hg.UpdateWindow(win)

hg.RenderShutdown()
hg.DestroyWindow(win)