uniform float time;
uniform vec2 resolution;
// based on https://www.shadertoy.com/view/MtBGDW
#define FIELD 5.0
#define CHANNEL bvec3(true, true, true)
#define TONE vec3(0.299, 0.587, 0.114)

vec2 pieuvreEQ(vec3 p,float t)
{
	vec2 fx = p.xy;
	fx.x = (fx.y+length(p*fx.x)-cos(t+fx.y));
	fx.x = (fx.y+length(p*fx.x)-cos(t+fx.y));
	fx.x = (fx.y+length(p*fx.x)-cos(t+fx.y));
	fx.x*=fx.x * 0.1;
	return fx;
}

vec3 computeColor(vec2 fx)
{
	vec3 color = vec3(CHANNEL) * TONE;
	color -= fx.x;
	color.b += color.g * 1.5;
	return clamp(color, 0.0, 1.0);
}

void main(void)
{
	float ratio = resolution.y / resolution.x;
	gl_FragCoord.y *= ratio;
	vec2 position = (gl_FragCoord.xy / resolution.xy) - vec2(0.5, 0.6 * ratio);
	vec3 p = position.xyx * FIELD;
	vec3 color = vec3(0.0, 0.0, 0.2);

	color += computeColor(pieuvreEQ(p * 2.5, time));
	gl_FragColor = vec4(color, 1.0);
}