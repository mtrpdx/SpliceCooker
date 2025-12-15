"""This file is a vertex shader written in GLSL.

The vertex shader handles visual effects on the framebuffer.

"""

# Pass-through vertex shader
vertex_source = """#version 330 core
in vec3 position;
in vec2 tex_coords;
out vec2 v_tex_coords;

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

void main() {
    gl_Position = window.projection * window.view * vec4(position, 1.0);
    v_tex_coords = tex_coords;
}
"""

# Dithering
# Use a 4x4 Bayer Matrix to decide which pixels to turn on/off
fragment_source = """#version 330 core
in vec2 v_tex_coords;
out vec4 final_color;

uniform sampler2D our_texture;

// The 4x4 Bayer Matrix (Ordered Dithering Pattern)
const float dither_matrix[16] = float[](
    0.0/16.0,  8.0/16.0,  2.0/16.0, 10.0/16.0,
    12.0/16.0, 4.0/16.0, 14.0/16.0, 6.0/16.0,
    3.0/16.0, 11.0/16.0, 1.0/16.0,  9.0/16.0,
    15.0/16.0, 7.0/16.0, 13.0/16.0, 5.0/16.0
);

void main() {
    // 1. Get the original color from the FBO texture
    vec4 color = texture(our_texture, v_tex_coords);
    
    // 2. Determine screen coordinates for the matrix
    // gl_FragCoord gives us the pixel X/Y on screen
    int x = int(gl_FragCoord.x) % 4;
    int y = int(gl_FragCoord.y) % 4;
    int index = x + y * 4;
    
    // 3. Get the threshold from the matrix
    float threshold = dither_matrix[index];
    
    // 4. Calculate Brightness (Luminance)
    float brightness = (color.r + color.g + color.b) / 3.0;
    
    // 5. Apply Dithering
    // If the pixel is brighter than the threshold, make it white (or green).
    // Otherwise, make it black.
    if (brightness > threshold) {
        final_color = vec4(0.2, 1.0, 0.2, 1.0); // Bright Green (Oscilloscope look)
    } else {
        final_color = vec4(0.0, 0.0, 0.0, 1.0); // Black background
    }
}
"""
