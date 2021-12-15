$input a_position, a_texcoord0
$output v_texcoord0

#include <bgfx_shader.sh>

void main() {
	gl_Position = mul(u_viewProj, vec4(a_position.xy, 0., 1.));
	v_texcoord0 = a_texcoord0;
}
