$input v_texcoord0

#include <bgfx_shader.sh>

SAMPLER2D(s_texTexture, 0);

#define PI 3.14159265359

uniform vec4 uProgress;

void main() {
	float circle_r = 0.45;
	float circle_thickness = 0.04;
	vec2 circle_angle = v_texcoord0 * vec2(-2.0, 2.0) - vec2(-1.0, 1.0);
	float d = length(v_texcoord0 - vec2(0.5, 0.5));
	float k_circle = abs(circle_r - d);

	k_circle = (1 - (k_circle * (1 / circle_thickness))) * 5;

	if (((atan2(-circle_angle.x, circle_angle.y) / PI) + 1.0) / 2.0 > uProgress.x)
		k_circle = 0.0;

	k_circle = clamp(k_circle, 0.0, 1.0);

	vec4 texColor = texture2D(s_texTexture, v_texcoord0);
	gl_FragColor = vec4(1.0, 1.0, 1.0, k_circle + texColor.w);
}
