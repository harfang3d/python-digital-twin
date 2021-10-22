$input v_texcoord0

#include <bgfx_shader.sh>

SAMPLER2D(s_texTexture, 0);
SAMPLER2D(s_texTextureGradient, 1);
SAMPLER2D(s_texTextureMask, 2);
uniform vec4 uTextureColor;

void main() {
    vec4 tex_c = texture2D(s_texTexture, v_texcoord0);
    vec4 tex_masque_c = texture2D(s_texTextureMask, v_texcoord0);
    vec4 tex_gradient_c = texture2D(s_texTextureGradient, vec2(uTextureColor.x, 0.5));
	gl_FragColor = tex_c * tex_c.w + vec4(tex_gradient_c.xyz, tex_gradient_c.w*tex_masque_c.w) * (1.0-tex_c.w);
}
