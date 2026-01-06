from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# =============================================================================
# GLOBAL VARIABLES & STATE MANAGEMENT
# =============================================================================

# Window dimensions
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800

# Camera-related variables
camera_pos = (0, 400, 500)
fovY = 60
GRID_LENGTH = 600
rand_var = 423

# Game State
STATE_MENU = 0
STATE_LEVEL_1 = 1
STATE_LEVEL_2 = 2
STATE_LEVEL_3 = 3
STATE_GAMEOVER = 4
STATE_WIN = 5
current_state = STATE_MENU

# Player State
player_pos = [0, 0, 0]
player_number = "001"
is_moving = False
facing_dir = 180
first_person = False
player_speed = 3.0

# Input states
keys_pressed = {
    'w': False, 'a': False, 's': False, 'd': False,
    'r': False, 'm': False
}

# Level 1 Specifics (Red Light Green Light)
l1_traffic_light = "GREEN"
l1_timer = 0
l1_next_switch = 0
l1_finish_z = -400
l1_start_z = 300
l1_eliminated = False
l1_light_duration = 0

# Level 2 Specifics (Dalgona)
l2_shape = "CIRCLE"
l2_path_points = []
l2_visited_points = []
l2_shape_radius = 150
l2_line_thickness = 25
l2_start_pos = [0, 0, 0]
l2_completed = False
l2_failed = False
l2_start_time = 0
l2_progress = 0
l2_last_position = [0, 0, 0]

# =============================================================================
# LEVEL 3 SPECIFICS (GLASS BRIDGE)
# =============================================================================

# Glass Bridge variables
l3_bridge_length = 7  # Number of steps per side
l3_step_distance = 60  # Distance between steps
l3_start_platform = [0, 0, 0]
l3_end_platform = [0, 0, -l3_step_distance * (l3_bridge_length + 1)]
l3_current_step = 0
l3_current_position = [0, 0, 0]  # x, y, z position
l3_correct_steps = []  # List of correct steps for each position: True for left, False for right
l3_show_hint = False
l3_completed = False
l3_eliminated = False
l3_platform_radius = 50

# Initialize the correct steps randomly - FIXED: Each step should have one safe and one dangerous option
def init_level_3_steps():
    global l3_correct_steps
    l3_correct_steps = []
    for i in range(l3_bridge_length):
        # Randomly choose left (True) or right (False) as correct step for each position
        # This ensures exactly one safe step per pair (left OR right is safe)
        l3_correct_steps.append(random.choice([True, False]))
    print("Correct steps (True=Left safe, False=Right safe):", l3_correct_steps)  # Debug print

# =============================================================================
# DRAWING HELPER FUNCTIONS
# =============================================================================

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_character(x, y, z):
    """Draws Roblox character with player number 001 on back"""
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Always face forward (towards -Z direction)
    glRotatef(180, 0, 1, 0)

    # TORSO - Deep green square body
    glColor3f(0.0, 0.4, 0.0)  # DEEP GREEN
    glPushMatrix()
    glTranslatef(0, 35, 0)
    glScalef(20, 35, 10)
    glutSolidCube(1)
    glPopMatrix()

    # PLAYER NUMBER "001" ON BACK OF TORSO - IN THE MIDDLE
    glColor3f(1, 1, 1)  # WHITE number
    glPushMatrix()
    glTranslatef(0, 35, 5.2)  # Center of back, slightly behind
    glScalef(0.08, 0.08, 0.08)
    glRotatef(90, 1, 0, 0)
    # Position digits horizontally centered
    for i, ch in enumerate(player_number):
        glPushMatrix()
        glTranslatef((i-1) * 40, 0, 0)
        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(ch))
        glPopMatrix()
    glPopMatrix()

    # HEAD - BLACK and LOWER (attached to body)
    glColor3f(0.1, 0.1, 0.1)  # BLACK
    glPushMatrix()
    glTranslatef(0, 60, 0)  # Lowered from y=70 to y=60 (attached to torso)
    glutSolidSphere(12, 12, 12)
    glPopMatrix()

    # ARMS - Upside down L shape with TINY GAP from body
    glColor3f(0.0, 0.4, 0.0)  # DEEP GREEN
    
    # Left arm - Upside down L shape
    glPushMatrix()
    # Shoulder part (horizontal) - TINY GAP from body
    glTranslatef(-13, 45, 0)  # Moved slightly away from body (-13 instead of -10)
    # Upper arm (vertical part)
    glPushMatrix()
    glTranslatef(0, -5, 0)  # Position for vertical part
    glScalef(5, 20, 5)  # Vertical arm
    glutSolidCube(1)
    glPopMatrix()
    # Lower arm (horizontal part) - extends forward
    glPushMatrix()
    glTranslatef(0, -20, -5)  # Position for horizontal forward part
    glScalef(5, 5, 15)  # Horizontal arm extending forward
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()
    
    # Right arm - Upside down L shape
    glPushMatrix()
    # Shoulder part (horizontal) - TINY GAP from body
    glTranslatef(13, 45, 0)  # Moved slightly away from body (13 instead of 10)
    # Upper arm (vertical part)
    glPushMatrix()
    glTranslatef(0, -5, 0)
    glScalef(5, 20, 5)  # Vertical arm
    glutSolidCube(1)
    glPopMatrix()
    # Lower arm (horizontal part) - extends forward
    glPushMatrix()
    glTranslatef(0, -20, -5)  # Position for horizontal forward part
    glScalef(5, 5, 15)  # Horizontal arm extending forward
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

    # HANDS - BLACK (at end of arms)
    glColor3f(0.1, 0.1, 0.1)  # BLACK
    # Left hand - at end of left arm
    glPushMatrix()
    glTranslatef(-13, 25, -12)  # Position at end of left arm
    glutSolidSphere(4, 8, 8)
    glPopMatrix()
    
    # Right hand - at end of right arm
    glPushMatrix()
    glTranslatef(13, 25, -12)  # Position at end of right arm
    glutSolidSphere(4, 8, 8)
    glPopMatrix()

    # LEGS - Deep green (same as torso)
    glColor3f(0.0, 0.4, 0.0)  # DEEP GREEN
    # Left leg
    glPushMatrix()
    glTranslatef(-6, 10, 0)
    glScalef(6, 25, 6)
    glutSolidCube(1)
    glPopMatrix()
    
    # Right leg
    glPushMatrix()
    glTranslatef(6, 10, 0)
    glScalef(6, 25, 6)
    glutSolidCube(1)
    glPopMatrix()

    # FEET - BLACK
    glColor3f(0.1, 0.1, 0.1)  # BLACK
    # Left foot
    glPushMatrix()
    glTranslatef(-6, 0, 3)
    glScalef(7, 3, 10)
    glutSolidCube(1)
    glPopMatrix()
    
    # Right foot
    glPushMatrix()
    glTranslatef(6, 0, 3)
    glScalef(7, 3, 10)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()

def draw_traffic_lights():
    """Draws 3 traffic lights that ALWAYS show - middle light indicates current state"""
    glPushMatrix()
    glTranslatef(0, 120, l1_finish_z - 50)
    
    # Pole (gray)
    glColor3f(0.4, 0.4, 0.4)
    glPushMatrix()
    glTranslatef(0, -48, 0)
    glScalef(6, 110, 2)
    glutSolidCube(1)
    glPopMatrix()
    
    # Light housing (black box)
    glTranslatef(0, 6, 100)
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glScalef(50, 15, 10)
    glutSolidCube(1)
    glPopMatrix()
    
    # Draw 3 lights
    light_spacing = 15
    for i in range(3):
        glPushMatrix()
        glTranslatef((i-1) * light_spacing, 0, 4)
        
        if l1_traffic_light == "GREEN":
            if i == 1:  # Middle light
                glColor3f(0, 1, 0)  # Bright green
            else:
                glColor3f(0, 0.3, 0)  # Dim green
        else:
            if i == 1:  # Middle light
                glColor3f(1, 0, 0)  # Bright red
            else:
                glColor3f(0.3, 0, 0)  # Dim red
        
        glutSolidSphere(3.5, 10, 10)
        glPopMatrix()
    
    glPopMatrix()

def draw_grid_floor():
    """Draws the game floor with grid lines for Level 1"""
    # Main beige path
    glColor3f(0.96, 0.87, 0.70)
    glBegin(GL_QUADS)
    glVertex3f(-200, 0.1, -GRID_LENGTH)
    glVertex3f(200, 0.1, -GRID_LENGTH)
    glVertex3f(200, 0.1, GRID_LENGTH)
    glVertex3f(-200, 0.1, GRID_LENGTH)
    glEnd()
    
    # Grass on sides
    glColor3f(0.1, 0.6, 0.1)
    # Left grass
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(-200, 0, -GRID_LENGTH)
    glVertex3f(-200, 0, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, 0, GRID_LENGTH)
    glEnd()
    
    # Right grass
    glBegin(GL_QUADS)
    glVertex3f(200, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, GRID_LENGTH)
    glVertex3f(200, 0, GRID_LENGTH)
    glEnd()
    
    # Grid lines
    glColor3f(0.8, 0.7, 0.6)
    glLineWidth(1.0)
    
    for x in range(-200, 201, 40):
        glBegin(GL_LINES)
        glVertex3f(x, 0.2, -GRID_LENGTH)
        glVertex3f(x, 0.2, GRID_LENGTH)
        glEnd()
    
    for z in range(-GRID_LENGTH, GRID_LENGTH + 1, 40):
        glBegin(GL_LINES)
        glVertex3f(-200, 0.2, z)
        glVertex3f(200, 0.2, z)
        glEnd()
    
    glLineWidth(1.0)

def draw_dalgona_floor():
    """Draws dalgona-colored floor for Level 2"""
    glColor3f(0.87, 0.72, 0.53)  # Dalgona caramel color
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, 0, GRID_LENGTH)
    glEnd()

def draw_dalgona_shape():
    """Draws the dalgona shape outline - visited parts turn green as player walks on them"""
    glLineWidth(l2_line_thickness)
    
    # First draw the entire shape in brown (unvisited)
    glColor3f(0.5, 0.3, 0.2)  # Dark brown for unvisited parts
    
    if l2_shape == "CIRCLE":
        glBegin(GL_LINE_LOOP)
        for x, z in l2_path_points:
            glVertex3f(x, 1, z)
        glEnd()
        
    elif l2_shape == "SQUARE":
        half_size = l2_shape_radius
        glBegin(GL_LINE_LOOP)
        glVertex3f(-half_size, 1, -half_size)
        glVertex3f(half_size, 1, -half_size)
        glVertex3f(half_size, 1, half_size)
        glVertex3f(-half_size, 1, half_size)
        glEnd()
        
    elif l2_shape == "TRIANGLE":
        height = l2_shape_radius * math.sqrt(3) / 2
        glBegin(GL_LINE_LOOP)
        glVertex3f(-l2_shape_radius, 1, -height/2)
        glVertex3f(l2_shape_radius, 1, -height/2)
        glVertex3f(0, 1, height)
        glEnd()
    
    # Now overlay green on visited parts - draw directly on top of brown line
    # Only draw if there are visited points
    visited_count = sum(l2_visited_points)
    if visited_count > 0:
        glColor3f(0, 1, 0)  # Green for visited parts
        glLineWidth(l2_line_thickness * 0.8)  # Slightly thinner so it fits inside brown line
        
        if l2_shape == "CIRCLE":
            # For circle, we need to handle wrap-around
            glBegin(GL_LINE_STRIP)
            first_visited_index = -1
            last_visited_index = -1
            
            # Find first visited point
            for i in range(len(l2_path_points)):
                if l2_visited_points[i]:
                    first_visited_index = i
                    break
            
            if first_visited_index >= 0:
                # Start from first visited point
                for i in range(first_visited_index, len(l2_path_points)):
                    if l2_visited_points[i]:
                        x, z = l2_path_points[i]
                        glVertex3f(x, 1.01, z)
                        last_visited_index = i
                    elif last_visited_index >= 0:
                        # Break if we hit an unvisited point after visited ones
                        break
                
                # Check if we need to wrap around to beginning
                if l2_visited_points[0] and last_visited_index == len(l2_path_points) - 1:
                    for i in range(len(l2_path_points)):
                        if l2_visited_points[i]:
                            x, z = l2_path_points[i]
                            glVertex3f(x, 1.01, z)
                        else:
                            break
            glEnd()
            
        elif l2_shape == "SQUARE" or l2_shape == "TRIANGLE":
            # For square and triangle, draw visited segments
            glBegin(GL_LINES)
            for i in range(len(l2_path_points)):
                if l2_visited_points[i]:
                    x1, z1 = l2_path_points[i]
                    # Find next visited point
                    next_index = (i + 1) % len(l2_path_points)
                    if l2_visited_points[next_index]:
                        x2, z2 = l2_path_points[next_index]
                        glVertex3f(x1, 1.01, z1)
                        glVertex3f(x2, 1.01, z2)
            glEnd()
    
    glLineWidth(1.0)

def draw_glass_bridge_floor():
    """Draws the dark floor for Glass Bridge level"""
    # Dark floor
    glColor3f(0.05, 0.05, 0.1)  # Very dark blue/gray
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, 0, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, 0, GRID_LENGTH)
    glEnd()
    
    # Draw the bridge structure (3 bright red lines)
    glLineWidth(5.0)
    glColor3f(1.0, 0.0, 0.0)  # Bright red
    
    # Left line
    glBegin(GL_LINES)
    glVertex3f(-15, 1, 0)
    glVertex3f(-15, 1, l3_end_platform[2])
    glEnd()
    
    # Middle line
    glBegin(GL_LINES)
    glVertex3f(0, 1, 0)
    glVertex3f(0, 1, l3_end_platform[2])
    glEnd()
    
    # Right line
    glBegin(GL_LINES)
    glVertex3f(15, 1, 0)
    glVertex3f(15, 1, l3_end_platform[2])
    glEnd()
    
    glLineWidth(1.0)

def draw_start_platform():
    """Draws the red half-circle starting platform"""
    glPushMatrix()
    glTranslatef(l3_start_platform[0], l3_start_platform[1], l3_start_platform[2])
    
    # Red platform (half circle)
    glColor3f(0.8, 0.0, 0.0)  # Bright red
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0.5, 0)  # Center
    for i in range(19):  # Half circle (180 degrees)
        angle = math.pi * i / 18
        x = l3_platform_radius * math.cos(angle)
        z = l3_platform_radius * math.sin(angle)
        glVertex3f(x, 0.5, z)
    glEnd()
    
    # Platform edge
    glColor3f(1.0, 0.2, 0.2)  # Lighter red for edge
    glLineWidth(3.0)
    glBegin(GL_LINE_STRIP)
    for i in range(19):  # Half circle (180 degrees)
        angle = math.pi * i / 18
        x = l3_platform_radius * math.cos(angle)
        z = l3_platform_radius * math.sin(angle)
        glVertex3f(x, 0.6, z)
    glEnd()
    glLineWidth(1.0)
    
    glPopMatrix()

def draw_end_platform():
    """Draws the red half-circle ending platform"""
    glPushMatrix()
    glTranslatef(l3_end_platform[0], l3_end_platform[1], l3_end_platform[2])
    
    # Red platform (half circle, facing opposite direction)
    glColor3f(0.8, 0.0, 0.0)  # Bright red
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0.5, 0)  # Center
    for i in range(19):  # Half circle (180 degrees) facing back
        angle = math.pi + math.pi * i / 18
        x = l3_platform_radius * math.cos(angle)
        z = l3_platform_radius * math.sin(angle)
        glVertex3f(x, 0.5, z)
    glEnd()
    
    # Platform edge
    glColor3f(1.0, 0.2, 0.2)  # Lighter red for edge
    glLineWidth(3.0)
    glBegin(GL_LINE_STRIP)
    for i in range(19):  # Half circle (180 degrees) facing back
        angle = math.pi + math.pi * i / 18
        x = l3_platform_radius * math.cos(angle)
        z = l3_platform_radius * math.sin(angle)
        glVertex3f(x, 0.6, z)
    glEnd()
    glLineWidth(1.0)
    
    glPopMatrix()

def draw_glass_steps():
    """Draws all the glass steps (7 on each side)"""
    step_size = 20  # Size of each step
    step_height = 0.5
    
    for step in range(l3_bridge_length):
        z_pos = -l3_step_distance * (step + 1)
        
        # Draw left step
        glPushMatrix()
        glTranslatef(-15, step_height, z_pos)
        
        if step < l3_current_step:
            # Already passed steps - show if they were correct or not
            if l3_correct_steps[step] == True:  # Left was correct
                glColor3f(0.2, 0.8, 0.2)  # Green - correct
            else:
                glColor3f(0.8, 0.2, 0.2)  # Red - wrong
        elif step == l3_current_step:
            # Current step - highlight if player is on it
            if l3_current_position[0] < 0:  # Player is on left step
                glColor3f(0.8, 0.8, 0.8)  # Bright white - current position
            else:
                glColor3f(0.5, 0.5, 0.5)  # Regular white
        else:
            # Future steps - show as white
            glColor3f(0.7, 0.7, 0.7)  # White
        
        # Draw the step
        glBegin(GL_QUADS)
        # Top
        glVertex3f(-step_size/2, 0, -step_size/2)
        glVertex3f(step_size/2, 0, -step_size/2)
        glVertex3f(step_size/2, 0, step_size/2)
        glVertex3f(-step_size/2, 0, step_size/2)
        # Sides
        glVertex3f(-step_size/2, -2, -step_size/2)
        glVertex3f(-step_size/2, 0, -step_size/2)
        glVertex3f(-step_size/2, 0, step_size/2)
        glVertex3f(-step_size/2, -2, step_size/2)
        glVertex3f(step_size/2, -2, -step_size/2)
        glVertex3f(step_size/2, 0, -step_size/2)
        glVertex3f(step_size/2, 0, step_size/2)
        glVertex3f(step_size/2, -2, step_size/2)
        glEnd()
        
        glPopMatrix()
        
        # Draw right step
        glPushMatrix()
        glTranslatef(15, step_height, z_pos)
        
        if step < l3_current_step:
            # Already passed steps - show if they were correct or not
            if l3_correct_steps[step] == False:  # Right was correct
                glColor3f(0.2, 0.8, 0.2)  # Green - correct
            else:
                glColor3f(0.8, 0.2, 0.2)  # Red - wrong
        elif step == l3_current_step:
            # Current step - highlight if player is on it
            if l3_current_position[0] > 0:  # Player is on right step
                glColor3f(0.8, 0.8, 0.8)  # Bright white - current position
            else:
                glColor3f(0.5, 0.5, 0.5)  # Regular white
        else:
            # Future steps - show as white
            glColor3f(0.7, 0.7, 0.7)  # White
        
        # Draw the step
        glBegin(GL_QUADS)
        # Top
        glVertex3f(-step_size/2, 0, -step_size/2)
        glVertex3f(step_size/2, 0, -step_size/2)
        glVertex3f(step_size/2, 0, step_size/2)
        glVertex3f(-step_size/2, 0, step_size/2)
        # Sides
        glVertex3f(-step_size/2, -2, -step_size/2)
        glVertex3f(-step_size/2, 0, -step_size/2)
        glVertex3f(-step_size/2, 0, step_size/2)
        glVertex3f(-step_size/2, -2, step_size/2)
        glVertex3f(step_size/2, -2, -step_size/2)
        glVertex3f(step_size/2, 0, -step_size/2)
        glVertex3f(step_size/2, 0, step_size/2)
        glVertex3f(step_size/2, -2, step_size/2)
        glEnd()
        
        glPopMatrix()

# =============================================================================
# LEVEL LOGIC FUNCTIONS
# =============================================================================

def init_level_1():
    global player_pos, l1_timer, l1_next_switch, l1_traffic_light
    global l1_eliminated, l1_light_duration
    
    player_pos = [0, 0, l1_start_z]
    l1_traffic_light = "GREEN"
    l1_timer = time.time()
    l1_light_duration = random.uniform(3, 6)
    l1_next_switch = l1_timer + l1_light_duration
    l1_eliminated = False

def init_level_2():
    """Initialize Dalgona level (Level 2)"""
    global player_pos, l2_shape, l2_path_points, l2_visited_points, l2_start_pos
    global l2_completed, l2_failed, l2_start_time, l2_progress, first_person, l2_last_position
    
    # Reset player to center
    player_pos = [0, 0, 0]
    l2_last_position = [0, 0, 0]
    
    # Choose random shape
    shapes = ["CIRCLE", "SQUARE", "TRIANGLE"]
    l2_shape = random.choice(shapes)
    
    # Generate path points based on shape
    l2_path_points = []
    steps = 100
    
    if l2_shape == "CIRCLE":
        for i in range(steps):
            angle = 2 * math.pi * i / steps
            x = l2_shape_radius * math.cos(angle)
            z = l2_shape_radius * math.sin(angle)
            l2_path_points.append((x, z))
        # Start player at right-most point of circle
        l2_start_pos = [l2_shape_radius, 0, 0]
        
    elif l2_shape == "SQUARE":
        half_size = l2_shape_radius
        # Generate points along square perimeter
        points_per_side = 25
        for i in range(points_per_side):  # Bottom side
            t = i / points_per_side
            x = -half_size + (2 * half_size) * t
            z = -half_size
            l2_path_points.append((x, z))
        for i in range(points_per_side):  # Right side
            t = i / points_per_side
            x = half_size
            z = -half_size + (2 * half_size) * t
            l2_path_points.append((x, z))
        for i in range(points_per_side):  # Top side
            t = i / points_per_side
            x = half_size - (2 * half_size) * t
            z = half_size
            l2_path_points.append((x, z))
        for i in range(points_per_side):  # Left side
            t = i / points_per_side
            x = -half_size
            z = half_size - (2 * half_size) * t
            l2_path_points.append((x, z))
        # Start player at bottom-left corner
        l2_start_pos = [-half_size, 0, -half_size]
        
    elif l2_shape == "TRIANGLE":
        height = l2_shape_radius * math.sqrt(3) / 2
        points_per_side = 33
        # Bottom side
        for i in range(points_per_side):
            t = i / points_per_side
            x = -l2_shape_radius + (2 * l2_shape_radius) * t
            z = -height/2
            l2_path_points.append((x, z))
        # Right side
        for i in range(points_per_side):
            t = i / points_per_side
            x = l2_shape_radius - l2_shape_radius * t
            z = -height/2 + height * t
            l2_path_points.append((x, z))
        # Left side
        for i in range(points_per_side):
            t = i / points_per_side
            x = -l2_shape_radius * t
            z = height - height * t
            l2_path_points.append((x, z))
        # Start player at bottom-left vertex
        l2_start_pos = [-l2_shape_radius, 0, -height/2]
    
    # Initialize visited points (all False)
    l2_visited_points = [False] * len(l2_path_points)
    
    player_pos[0] = l2_start_pos[0]
    player_pos[2] = l2_start_pos[2]
    l2_last_position[0] = player_pos[0]
    l2_last_position[2] = player_pos[2]
    
    # Mark the starting point as visited
    mark_nearby_points_as_visited()
    
    l2_completed = False
    l2_failed = False
    l2_start_time = time.time()
    l2_progress = 0
    first_person = False

def init_level_3():
    """Initialize Glass Bridge level (Level 3)"""
    global player_pos, l3_current_step, l3_current_position
    global l3_completed, l3_eliminated, l3_show_hint, first_person
    
    # Initialize correct steps - FIXED: This now properly randomizes
    init_level_3_steps()
    
    # Reset player to start platform
    player_pos = [l3_start_platform[0], 0, l3_start_platform[2]]
    l3_current_step = 0
    l3_current_position = [l3_start_platform[0], 0, l3_start_platform[2]]
    
    l3_completed = False
    l3_eliminated = False
    l3_show_hint = False
    first_person = False

def mark_nearby_points_as_visited():
    """Mark path points near the player as visited"""
    global l2_visited_points
    px, _, pz = player_pos
    
    for i, (path_x, path_z) in enumerate(l2_path_points):
        distance = math.sqrt((px - path_x)**2 + (pz - path_z)**2)
        if distance < l2_line_thickness / 2:  # Smaller threshold for more precise tracking
            l2_visited_points[i] = True

def check_completion():
    """Check if player has completed tracing the shape - REQUIRES 100%"""
    global l2_progress
    
    # Calculate progress based on visited points
    total_points = len(l2_path_points)
    visited_count = sum(1 for visited in l2_visited_points if visited)
    new_progress = (visited_count / total_points) * 100
    
    # Update progress if increased
    if new_progress > l2_progress:
        l2_progress = new_progress
    
    # Check if completed - NOW REQUIRES 100% (or very close to account for floating point errors)
    if l2_progress >= 99.5:  # Changed from 90% to 99.5%
        return True
    
    return False

def update_level_1():
    global l1_traffic_light, l1_next_switch, l1_light_duration, current_state, l1_eliminated
    
    if l1_eliminated:
        return
    
    # Update traffic light
    now = time.time()
    if now > l1_next_switch:
        if l1_traffic_light == "GREEN":
            l1_traffic_light = "RED"
            l1_light_duration = random.uniform(2, 4)
        else:
            l1_traffic_light = "GREEN"
            l1_light_duration = random.uniform(3, 6)
        l1_next_switch = now + l1_light_duration
    
    # Player movement
    if keys_pressed['w'] and is_moving:
        if l1_traffic_light == "GREEN":
            player_pos[2] -= player_speed
        else:
            l1_eliminated = True
            current_state = STATE_GAMEOVER
            return
    
    # Check if reached finish line
    if player_pos[2] <= l1_finish_z:
        init_level_2()
        current_state = STATE_LEVEL_2
        return

def update_level_2():
    """Update Dalgona level logic"""
    global l2_completed, l2_failed, current_state
    
    if l2_failed:
        current_state = STATE_GAMEOVER
        return
    
    if l2_completed:
        init_level_3()  # Move to level 3 when level 2 is completed
        current_state = STATE_LEVEL_3
        return
    
    # Check if player is on the path
    px, _, pz = player_pos
    on_path = False
    min_distance = float('inf')
    
    for path_x, path_z in l2_path_points:
        distance = math.sqrt((px - path_x)**2 + (pz - path_z)**2)
        if distance < min_distance:
            min_distance = distance
        
        if distance < l2_line_thickness:
            on_path = True
    
    # Mark nearby points as visited
    mark_nearby_points_as_visited()
    
    # Update last position for next frame
    l2_last_position[0] = px
    l2_last_position[2] = pz
    
    # Check completion - NOW REQUIRES NEARLY 100%
    if check_completion():
        l2_completed = True
        return
    
    # If player is too far from the path, they fail
    if not on_path and min_distance > l2_line_thickness * 1.5:
        l2_failed = True
        current_state = STATE_GAMEOVER
        return

def update_level_3():
    """Update Glass Bridge level logic"""
    global l3_completed, l3_eliminated, current_state
    
    if l3_eliminated:
        current_state = STATE_GAMEOVER
        return
    
    if l3_completed:
        current_state = STATE_WIN
        return
    
    # Check if player has reached the end platform
    if l3_current_step >= l3_bridge_length:
        # Player has reached the end
        l3_current_position[0] = l3_end_platform[0]
        l3_current_position[2] = l3_end_platform[2]
        player_pos[0] = l3_end_platform[0]
        player_pos[2] = l3_end_platform[2]
        l3_completed = True
        return

def handle_level_3_input(key_char):
    """Handle input for Glass Bridge level - FIXED: Correct movement logic"""
    global l3_current_step, l3_current_position, l3_eliminated, player_pos
    
    if l3_current_step >= l3_bridge_length:
        return  # Already completed
    
    # First step from start platform
    if key_char == 'a' or key_char == 'd':
        if l3_current_step == 0 and l3_current_position[2] == l3_start_platform[2]:
            if key_char == 'a':  # Choose left step
                l3_current_position = [-15, 0, -l3_step_distance]
                player_pos[0] = -15
                player_pos[2] = -l3_step_distance
                l3_current_step = 1
            elif key_char == 'd':  # Choose right step
                l3_current_position = [15, 0, -l3_step_distance]
                player_pos[0] = 15
                player_pos[2] = -l3_step_distance
                l3_current_step = 1
            
            # Check if the chosen step is correct
            # For first step (index 0), check if choice matches correct step
            if (key_char == 'a' and not l3_correct_steps[0]) or (key_char == 'd' and l3_correct_steps[0]):
                l3_eliminated = True
            return
    
    # For subsequent steps (from step 1 onward)
    elif (key_char == 'w' or key_char == 'r') and l3_current_step > 0:
        if l3_current_step < l3_bridge_length:
            # Determine which step to take based on current position and key pressed
            if l3_current_position[0] < 0:  # Currently on left side
                if key_char == 'w':  # Move forward (stay on left)
                    next_x = -15
                    is_left_step = True
                elif key_char == 'r':  # Move to right
                    next_x = 15
                    is_left_step = False
            else:  # Currently on right side
                if key_char == 'w':  # Move forward (stay on right)
                    next_x = 15
                    is_left_step = False
                elif key_char == 'r':  # Move to left
                    next_x = -15
                    is_left_step = True
            
            # Calculate new position
            new_z = -l3_step_distance * (l3_current_step + 1)
            l3_current_position = [next_x, 0, new_z]
            player_pos[0] = next_x
            player_pos[2] = new_z
            
            # Check if the chosen step is correct
            # Note: We're checking l3_correct_steps[l3_current_step] because we haven't incremented yet
            if (is_left_step and not l3_correct_steps[l3_current_step]) or \
               (not is_left_step and l3_correct_steps[l3_current_step]):
                l3_eliminated = True
            else:
                l3_current_step += 1

# =============================================================================
# INPUT HANDLERS
# =============================================================================

def keyboardListener(key, x, y):
    global current_state, is_moving, keys_pressed, l3_show_hint
    
    try:
        key_char = key.decode('utf-8').lower()
        
        if key_char in keys_pressed:
            keys_pressed[key_char] = True
        
        if current_state == STATE_MENU:
            if key_char == 'p':
                init_level_1()
                current_state = STATE_LEVEL_1
            elif key_char == '\x1b':
                glutLeaveMainLoop()
                
        elif current_state == STATE_LEVEL_1:
            if key_char == 'w':
                is_moving = True
            elif key_char == 'r':
                current_state = STATE_MENU
            elif key_char == '\x1b':
                current_state = STATE_MENU
                
        elif current_state == STATE_LEVEL_2:
            if key_char == 'w':
                player_pos[2] -= player_speed
            elif key_char == 's':
                player_pos[2] += player_speed
            elif key_char == 'a':
                player_pos[0] -= player_speed
            elif key_char == 'd':
                player_pos[0] += player_speed
            elif key_char == 'r':
                current_state = STATE_MENU
            elif key_char == '\x1b':
                current_state = STATE_MENU
        
        elif current_state == STATE_LEVEL_3:
            # Handle M key for hint toggle
            if key_char == 'm':
                l3_show_hint = not l3_show_hint
            else:
                handle_level_3_input(key_char)
            
            # Only allow R to return to menu if it's not being used for movement
            # 'r' is used for sideways movement in level 3, so we need to be careful
            if key_char == 'r' and not l3_show_hint and current_state == STATE_LEVEL_3:
                # Check if we're in a position where 'r' would be movement
                if l3_current_step == 0 or l3_current_step >= l3_bridge_length:
                    current_state = STATE_MENU
            elif key_char == '\x1b':
                current_state = STATE_MENU
                
        elif current_state in [STATE_GAMEOVER, STATE_WIN]:
            if key_char == 'r':
                current_state = STATE_MENU
            elif key_char == '\x1b':
                glutLeaveMainLoop()
                
    except UnicodeDecodeError:
        pass

def keyboardUpListener(key, x, y):
    global is_moving, keys_pressed
    
    try:
        key_char = key.decode('utf-8').lower()
        
        if key_char in keys_pressed:
            keys_pressed[key_char] = False
            
        if key_char == 'w':
            is_moving = False
            
    except UnicodeDecodeError:
        pass

def specialKeyListener(key, x, y):
    global camera_pos
    x, y, z = camera_pos
    
    if key == GLUT_KEY_LEFT:
        x -= 10
    elif key == GLUT_KEY_RIGHT:
        x += 10
    elif key == GLUT_KEY_UP:
        y += 10
    elif key == GLUT_KEY_DOWN:
        y -= 10
    
    camera_pos = (x, y, z)

def mouseListener(button, state, x, y):
    global first_person, current_state
    
    gl_y = WINDOW_HEIGHT - y
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if current_state == STATE_MENU:
            if 400 <= x <= 600 and 350 <= gl_y <= 450: # PLAY
                init_level_1()
                current_state = STATE_LEVEL_1
            elif 400 <= x <= 600 and 250 <= gl_y <= 350: # EXIT 
                glutLeaveMainLoop()
        
        if x >= 950 and gl_y >= 750: #CROSS
            glutLeaveMainLoop()
    
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if current_state in [STATE_LEVEL_1, STATE_LEVEL_2, STATE_LEVEL_3]:
            first_person = not first_person

# =============================================================================
# CAMERA AND DISPLAY - FIXED FIRST PERSON VIEW
# =============================================================================

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if current_state == STATE_MENU:
        gluLookAt(0, 500, 500,
                  0, 0, 0,
                  0, 1, 0)
    elif current_state in [STATE_GAMEOVER, STATE_WIN]:
        gluLookAt(0, 300, 400,
                  0, 0, 0,
                  0, 1, 0)
    else:
        if first_person:
            # FIRST PERSON FROM EYE LEVEL (not inside head)
            # Eye level is approximately at player's head position
            eye_x = player_pos[0]
            eye_y = player_pos[1] + 65  # Eye level (slightly below top of head)
            eye_z = player_pos[2]
            
            # Look direction (forward in -Z direction)
            look_x = eye_x
            look_y = eye_y
            look_z = eye_z - 100  # Look 100 units ahead
            
            gluLookAt(eye_x, eye_y, eye_z,
                      look_x, look_y, look_z,
                      0, 1, 0)
        else:
            # Third person camera
            gluLookAt(player_pos[0], player_pos[1] + 200, player_pos[2] + 300,
                      player_pos[0], player_pos[1] + 50, player_pos[2],
                      0, 1, 0)

def idle():
    if current_state == STATE_LEVEL_1:
        update_level_1()
    elif current_state == STATE_LEVEL_2:
        update_level_2()
    elif current_state == STATE_LEVEL_3:
        update_level_3()
    
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    
    setupCamera()
    
    if current_state == STATE_MENU:
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
        draw_text(400, 600, "SQUID GAMES", GLUT_BITMAP_TIMES_ROMAN_24)
        
        glColor3f(0, 0.5, 0)
        glBegin(GL_QUADS)
        glVertex2f(380, 390)
        glVertex2f(620, 390)
        glVertex2f(620, 450)
        glVertex2f(380, 450)
        glEnd()
        
        glColor3f(0.5, 0, 0)
        glBegin(GL_QUADS)
        glVertex2f(380, 290)
        glVertex2f(620, 290)
        glVertex2f(620, 350)
        glVertex2f(380, 350)
        glEnd()
        
        glColor3f(1, 1, 1)
        draw_text(470, 415, "PLAY")
        draw_text(470, 315, "EXIT")
        
        draw_text(350, 200, "Press P or click PLAY to start")
        draw_text(350, 170, "Right click to toggle camera in game")
        
    elif current_state == STATE_GAMEOVER:
        glClearColor(0.3, 0.0, 0.0, 1.0)
        draw_text(400, 500, "ELIMINATED!", GLUT_BITMAP_TIMES_ROMAN_24)
        
        if current_state == STATE_LEVEL_1 and l1_eliminated:
            draw_text(380, 400, "You moved during Red Light!")
        elif current_state == STATE_LEVEL_2 and l2_failed:
            draw_text(380, 400, "You broke the dalgona shape!")
        elif current_state == STATE_LEVEL_3 and l3_eliminated:
            draw_text(380, 400, "You stepped on the wrong glass!")
        else:
            draw_text(380, 400, "You were eliminated!")
            
        draw_text(380, 350, "Press R to return to Menu")
        draw_text(380, 300, "Press ESC to Exit")
        
    elif current_state == STATE_WIN:
        glClearColor(0.0, 0.3, 0.0, 1.0)
        draw_text(400, 500, "CONGRATULATIONS!", GLUT_BITMAP_TIMES_ROMAN_24)
        
        if l3_completed:
            draw_text(350, 400, "You won 456 billion Zimbabwean dollars!")
            draw_text(380, 350, "Press END to exit the game")
            draw_text(380, 300, "Press R to return to Menu")
        elif l2_completed:
            draw_text(380, 400, f"You completed the {l2_shape} dalgona!")
            draw_text(380, 350, "Press R to return to Menu")
            draw_text(380, 300, "Press ESC to Exit")
        else:
            draw_text(380, 400, "You completed the level!")
            draw_text(380, 350, "Press R to return to Menu")
            draw_text(380, 300, "Press ESC to Exit")
        
    elif current_state == STATE_LEVEL_1:
        # Draw Level 1 environment
        draw_grid_floor()
        draw_traffic_lights()
        
        # Only draw player if not in first person mode
        if not first_person:
            draw_character(player_pos[0], player_pos[1], player_pos[2])
        
        # Draw walls
        glColor3f(0.5, 0.8, 1.0)
        glPushMatrix()
        glTranslatef(-GRID_LENGTH, 150, 0)
        glScalef(5, 300, GRID_LENGTH * 2)
        glutSolidCube(1)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(GRID_LENGTH, 150, 0)
        glScalef(5, 300, GRID_LENGTH * 2)
        glutSolidCube(1)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, 150, -GRID_LENGTH)
        glScalef(GRID_LENGTH * 2, 300, 5)
        glutSolidCube(1)
        
        glColor3f(1, 1, 1)
        for i in range(5):
            glPushMatrix()
            glTranslatef(random.uniform(-300, 300), random.uniform(50, 250), 3)
            glRotatef(90, 0, 1, 0)
            glutSolidSphere(20, 8, 8)
            glPopMatrix()
        glPopMatrix()
        
        # UI Overlay for Level 1
        glColor3f(1, 0, 0)
        draw_text(970, 770, "X")
        
        glColor3f(1, 1, 1)
        draw_text(10, 770, "Red Light, Green Light")
        
        if l1_traffic_light == "GREEN":
            glColor3f(0, 1, 0)
        else:
            glColor3f(1, 0, 0)
        draw_text(10, 745, f"Light: {l1_traffic_light}")
        
        glColor3f(1, 1, 1)
        draw_text(10, 720, "Hold W to move (Green only)")
        draw_text(10, 695, "Release W to stop")
        draw_text(10, 670, f"Player: {player_number}")
        draw_text(10, 645, f"Position: ({int(player_pos[0])}, {int(player_pos[2])})")
        
        if l1_traffic_light == "RED":
            glColor3f(1, 0.5, 0)
            draw_text(10, 595, "STOP! RED LIGHT ACTIVE")
            
    elif current_state == STATE_LEVEL_2:
        # Draw Level 2 environment (Dalgona)
        draw_dalgona_floor()
        
        # Draw the shape outline - visited parts turn green ONLY where player walked
        draw_dalgona_shape()
        
        # Only draw player if not in first person mode
        if not first_person:
            draw_character(player_pos[0], player_pos[1], player_pos[2])
        
        # Draw walls for Level 2
        glColor3f(0.5, 0.8, 1.0)
        glPushMatrix()
        glTranslatef(-GRID_LENGTH, 150, 0)
        glScalef(5, 300, GRID_LENGTH * 2)
        glutSolidCube(1)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(GRID_LENGTH, 150, 0)
        glScalef(5, 300, GRID_LENGTH * 2)
        glutSolidCube(1)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, 150, -GRID_LENGTH)
        glScalef(GRID_LENGTH * 2, 300, 5)
        glutSolidCube(1)
        glPopMatrix()
        
        # UI Overlay for Level 2
        glColor3f(1, 0, 0)
        draw_text(970, 770, "X")
        
        glColor3f(1, 1, 1)
        draw_text(10, 770, "Dalgona Challenge")
        draw_text(10, 745, f"Shape: {l2_shape}")
        draw_text(10, 720, "WASD to trace the shape")
        draw_text(10, 695, "Stay on the thick line!")
        draw_text(10, 670, f"Player: {player_number}")
        
        # Progress bar - NOW SHOWS EXACT PERCENTAGE
        draw_text(10, 645, f"Progress: {l2_progress:.1f}%")
        
        # Draw simple progress bar
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        
        # Progress bar fill
        if l2_progress >= 99.5:
            glColor3f(0, 1, 0)  # Green when complete
        else:
            glColor3f(1, 0.8, 0)  # Orange while in progress
        bar_width = 200 * (l2_progress / 100)
        glBegin(GL_QUADS)
        glVertex2f(10, 630)
        glVertex2f(10 + bar_width, 630)
        glVertex2f(10 + bar_width, 640)
        glVertex2f(10, 640)
        glEnd()
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        # Show how many points are visited
        visited_count = sum(l2_visited_points)
        total_points = len(l2_path_points)
        draw_text(10, 620, f"Visited: {visited_count}/{total_points} points")
        
        # Distance warning
        px, py, pz = player_pos
        min_dist = float('inf')
        for path_x, path_z in l2_path_points:
            dist = math.sqrt((px - path_x)**2 + (pz - path_z)**2)
            if dist < min_dist:
                min_dist = dist
        
        if min_dist > l2_line_thickness:
            glColor3f(1, 0, 0)
            draw_text(10, 605, f"DANGER! {int(min_dist)} units from line")
        elif min_dist > l2_line_thickness / 2:
            glColor3f(1, 1, 0)
            draw_text(10, 605, f"Warning: {int(min_dist)} units from line")
        else:
            glColor3f(0, 1, 0)
            draw_text(10, 605, f"Safe: {int(min_dist)} units from line")
    
    elif current_state == STATE_LEVEL_3:
        # Draw Level 3 environment (Glass Bridge)
        draw_glass_bridge_floor()
        
        # Draw platforms
        draw_start_platform()
        draw_end_platform()
        
        # Draw glass steps
        draw_glass_steps()
        
        # Only draw player if not in first person mode
        if not first_person:
            draw_character(player_pos[0], player_pos[1], player_pos[2])
        
        # Draw dark walls for Level 3
        glColor3f(0.1, 0.1, 0.2)  # Dark blue/gray walls
        glPushMatrix()
        glTranslatef(-GRID_LENGTH, 150, 0)
        glScalef(5, 300, GRID_LENGTH * 2)
        glutSolidCube(1)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(GRID_LENGTH, 150, 0)
        glScalef(5, 300, GRID_LENGTH * 2)
        glutSolidCube(1)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, 150, -GRID_LENGTH)
        glScalef(GRID_LENGTH * 2, 300, 5)
        glutSolidCube(1)
        glPopMatrix()
        
        # UI Overlay for Level 3
        glColor3f(1, 0, 0)
        draw_text(970, 770, "X")
        
        glColor3f(1, 1, 1)
        draw_text(10, 770, "Glass Bridge Challenge")
        draw_text(10, 745, f"Step: {l3_current_step}/{l3_bridge_length}")
        draw_text(10, 720, "Choose the correct glass step!")
        
        if l3_current_step == 0:
            draw_text(10, 695, "Press A for LEFT or D for RIGHT")
        else:
            draw_text(10, 695, "Press W for FORWARD or R for SIDE")
        
        draw_text(10, 670, f"Player: {player_number}")
        draw_text(10, 645, f"Position: ({int(player_pos[0])}, {int(player_pos[2])})")
        
        # Instructions for hint
        draw_text(10, 620, "Press M to get hint for next step")
        
        # Show current position info
        if l3_current_step < l3_bridge_length:
            if l3_current_position[0] < 0:
                position_text = "Left side"
            else:
                position_text = "Right side"
            draw_text(10, 595, f"Current: {position_text}")
        
        # Show hint when M is pressed
        if l3_show_hint and l3_current_step < l3_bridge_length:
            if l3_correct_steps[l3_current_step]:
                hint = "HINT: Next safe step is on the LEFT"
            else:
                hint = "HINT: Next safe step is on the RIGHT"
            glColor3f(0, 1, 0)  # Green color for hint
            draw_text(10, 570, hint)
            draw_text(10, 545, "(Press M again to hide)")
    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Squid Games - Red Light Green Light & Dalgona & Glass Bridge")
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()