import harfang as hg
from statistics import median

d = 5

cam_rot_speed = 0.5
k_wheel = 10

dtxl = []
dtyl = []

smoothed_dx = 0
smoothed_dy = 0

smoothed_rotx = 0


def OrbitalController(keyboard, mouse, cam_pos, cam_rot, cam_tgt, dt, width, height):
	global d
	global dtxl, dtyl, smoothed_dx, smoothed_dy, smoothed_rotx
	dt_sec = hg.time_to_sec_f(dt)

	k_ar = hg.ComputeAspectRatioX(width, height).x

	delta_x = mouse.DtX() if mouse.Down(hg.MB_0) else 0
	delta_y = -mouse.DtY() if mouse.Down(hg.MB_0) else 0
	dtxl.append(delta_x)
	dtyl.append(delta_y)
	if len(dtxl) > 5:
		dtxl.pop(0)
	if len(dtyl) > 5:
		dtyl.pop(0)
	delta_x = median(dtxl)
	delta_y = median(dtyl)

	smoothed_dx += (delta_x - smoothed_dx) * 0.1
	smoothed_dy += (delta_y - smoothed_dy) * 0.1

	state_modified = False
	speed = dt_sec * cam_rot_speed
	cam_rot.x += smoothed_dy * speed
	cam_rot.y += smoothed_dx * speed

	# clamp X

	if cam_rot.x > 1.57:
		cam_rot.x = 1.57
	if cam_rot.x < 0:
		cam_rot.x = 0



	if keyboard.Down(hg.K_LAlt):
		if mouse.Down(hg.MB_0):
			z_value = -mouse.DtY() * 5
			speed = d * dt_sec * 10
			d += z_value * speed

	if mouse.Wheel() != 0:
		wheel_dt = mouse.Wheel()

		k = abs(wheel_dt) * k_wheel * dt_sec
		if wheel_dt > 0:
			d /= k + 1
		else:
			d *= k + 1

		if d < 3:
			d = 3  # make sure not to come too close to the target
		if d > 28:
			d = 28

	if mouse.Down(hg.MB_2):  # scroll viewpoint
		speed = d * dt_sec * 0.1
		mat = hg.TransformationMat4(cam_pos, cam_rot)
		cam_tgt += (hg.GetX(mat) * -mouse.DtX() * k_ar + hg.GetY(mat) * -mouse.DtY()) * speed

	world = hg.TransformationMat4(cam_tgt, cam_rot, hg.Vec3.One) * hg.TranslationMat4(hg.Vec3(0, 0, -d))
	return world, cam_rot, cam_tgt, hg.GetT(world)
