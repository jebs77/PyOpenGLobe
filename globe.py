import pygame
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import numpy

import math

import csv

def load_data_from_csv(file_path):
    data_points = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header if it exists
        for row in reader:
            lat = float(row[0])
            lon = float(row[1])
            data_fields = row[2:5]  # Three additional data fields
            data_points.append((lat, lon, data_fields))
    return data_points

def lat_lon_to_cartesian(lat, lon, radius=1):
    """
    Converts latitude and longitude to Cartesian coordinates on a sphere.
    - `lat` and `lon` are in degrees.
    - `radius` is the sphere's radius (default is 1).
    """
    # Convert latitude and longitude from degrees to radians
    lat_rad = math.radians(-lat)
    lon_rad = math.radians(-(lon + 90))

    # Convert to Cartesian coordinates
    x = radius * math.cos(lat_rad) * math.cos(lon_rad)
    y = radius * math.cos(lat_rad) * math.sin(lon_rad)
    z = radius * math.sin(lat_rad)

    return x, y, z


    
def render_coordinates(coordinates):
    """
    Renders small green spheres at the specified coordinates.
    - `coordinates` is a list of tuples [(lat, lon, data_fields), ...].
    """
    glColor3f(0.0, 1.0, 0.0)  # Green color
    for lat, lon, data_fields in coordinates:  # Unpacking 3 values: lat, lon, and data_fields
        x, y, z = lat_lon_to_cartesian(lat, lon, radius=1.0)  # Slightly above the globe
        glPushMatrix()
        glTranslatef(x, y, z)  # Move to the coordinate position
        qobj = gluNewQuadric()
        gluSphere(qobj, 0.005, 10, 10)  # Small sphere
        gluDeleteQuadric(qobj)
        glPopMatrix()

def read_texture(filename):
    """
    Reads an image file and converts to a OpenGL-readable textID format
    """
    img = Image.open(filename)
    img_data = numpy.array(list(img.getdata()), numpy.int8)
    textID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textID)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                 img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return textID



def render_popups(coordinates):
    """
    Renders popups at the specified coordinates. Each popup shows data fields.
    - `coordinates` is a list of tuples [(lat, lon, data_fields), ...].
    """
    for lat, lon, data_fields in coordinates:  # Unpack lat, lon, and data_fields
        x, y, z = lat_lon_to_cartesian(lat, lon, radius=1.0)  # Convert coordinates to 3D space
        
        # Push the current matrix state to isolate the popup's transformations
        glPushMatrix()

        glTranslatef(x, y, z)  # Move the popup to the coordinate position

        glColor3f(1.0, 0.0, 0.0)  # Red color for popups (or any other color)

        # Render the popup data (this is where you can draw text or other popup elements)
        # For example, you can render the `data_fields` in 3D space
        # You would need to use OpenGL text rendering methods here (not implemented yet)

        glPopMatrix()


def main():
    pygame.init()
    display = (pygame.display.Info().current_w, pygame.display.Info().current_h)  # Get screen dimensions
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | pygame.FULLSCREEN)  # Set full-screen mode
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption('PyOpenGLobe')
    pygame.key.set_repeat(1, 10)  # Allows press and hold of buttons
    gluPerspective(40, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)  # Sets initial zoom so we can see the globe
    lastPosX = 0
    lastPosY = 0
    texture = read_texture('world.jpg')
    glRotatef(180, 0, 1, 0)  # Rotate the sphere 180° around the Y-axis
    glRotatef(90, 1, 0, 0)

    # Load data from CSV
    coordinates = load_data_from_csv('sites.csv')  # Replace with your file path
    selected_point = None  # To hold the selected point's data

    while True:
        for event in pygame.event.get():  # User activities are called events
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    glRotatef(1, 0, 0, 1)
                if event.key == pygame.K_RIGHT:
                    glRotatef(1, 0, 0, -1)
                if event.key == pygame.K_UP:
                    glRotatef(1, -1, 0, 0)
                if event.key == pygame.K_DOWN:
                    glRotatef(1, 1, 0, 0)

            # Zoom in and out with mouse wheel
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # wheel rolled up
                    glScaled(1.05, 1.05, 1.05)
                if event.button == 5:  # wheel rolled down
                    glScaled(0.95, 0.95, 0.95)

            # Rotate with mouse click and drag
            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                dx = x - lastPosX
                dy = y - lastPosY
                mouseState = pygame.mouse.get_pressed()
                if mouseState[0]:

                    modelView = (GLfloat * 16)()
                    mvm = glGetFloatv(GL_MODELVIEW_MATRIX, modelView)

                    # To combine x-axis and y-axis rotation
                    temp = (GLfloat * 3)()
                    temp[0] = modelView[0]*dy + modelView[1]*dx
                    temp[1] = modelView[4]*dy + modelView[5]*dx
                    temp[2] = modelView[8]*dy + modelView[9]*dx
                    norm_xy = math.sqrt(temp[0]*temp[0] + temp[1] * temp[1] + temp[2]*temp[2])
                    glRotatef(math.sqrt(dx*dx + dy*dy), temp[0]/norm_xy, temp[1]/norm_xy, temp[2]/norm_xy)

                lastPosX = x
                lastPosY = y

        # Clears the screen and draws the globe
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        qobj = gluNewQuadric()
        gluQuadricTexture(qobj, GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        gluSphere(qobj, 1, 50, 50)
        gluDeleteQuadric(qobj)
        glDisable(GL_TEXTURE_2D)

        # Renders the coordinate points
        render_coordinates(coordinates)

        # Renders the popups with data fields
        render_popups(coordinates)  # Pass coordinates directly

        # If a point is selected, display its data fields
        if selected_point:
            lat, lon, data_fields = selected_point
            glColor3f(1, 1, 1)
            glRasterPos3f(0, 0, -2)
            font = pygame.font.SysFont(None, 24)
            text = f"Data: {data_fields}"
            text_surface = font.render(text, True, (255, 255, 255))
            text_data = pygame.image.tostring(text_surface, "RGB", 1)
            glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGB, GL_UNSIGNED_BYTE, text_data)

        pygame.display.flip()
        pygame.time.wait(10)

main()