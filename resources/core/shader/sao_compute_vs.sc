$input a_position, a_texcoord0
$output v_viewRay

#include <forward_pipeline.sh>

void main() {
	gl_Position = mul(u_viewProj, vec4(a_position.xy, 0.0, 1.0) );

	vec2 sp = a_position.xy * 2. - 1.;
	sp.y *= -1.;

	vec4 ndc = mul(uMainInvProjection, vec4(sp, 1., 1.)); // far ndc frustum plane
	ndc /= ndc.w;
	ndc /= ndc.z;

	v_viewRay = ndc.xyz;
}
