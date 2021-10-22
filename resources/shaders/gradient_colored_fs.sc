$input v_texcoord0

#include <bgfx_shader.sh>

SAMPLER2D(s_texTextureGradient, 1);
uniform vec4 uTextureColor;

void main() {
	gl_FragColor = texture2D(s_texTextureGradient, vec2(uTextureColor.x, 0.5));
}
