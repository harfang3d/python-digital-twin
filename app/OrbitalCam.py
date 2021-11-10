import harfang as hg

d = 5

cam_rot_speed = 0.5
k_wheel = 10


def OrbitalController(keyboard, mouse, cam_pos, cam_rot, cam_tgt, dt, width, height):
	global d
	dt_sec = hg.time_to_sec_f(dt)

	k_ar = hg.ComputeAspectRatioX(width, height).x

	state_modified = False
	if mouse.Down(hg.MB_0):
		speed = dt_sec * cam_rot_speed
		delta_x = mouse.DtX()
		delta_y = -mouse.DtY()
		if delta_x > 40 or delta_x < -40:
			delta_x = 0
		if delta_y > 40 or delta_y < -40:
			delta_y = 0
		cam_rot.x += delta_y * speed
		cam_rot.y += delta_x * speed

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
