import pygame
import math
from main import Projector

# --- 기본 설정 ---
WIDTH, HEIGHT = 800, 600
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Cube - Rotation Control")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# --- 3D 설정 ---
projector = Projector(WIDTH, HEIGHT)

# 정육면체의 원본 꼭짓점 (수정되지 않음)
vertices = [
    (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
    (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)
]

edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # 앞면
    (4, 5), (5, 6), (6, 7), (7, 4),  # 뒷면
    (0, 4), (1, 5), (2, 6), (3, 7)   # 옆면
]

# --- 카메라 및 마우스 설정 ---
camera_pos = [0, 0, -5]
mouse_last_pos = None
mouse_clicked = False
mouse_sensitivity = 2

# --- 회전 관련 변수 및 함수 ---
rotation_angles = [0, 0, 0]  # [x, y, z] 축에 대한 회전 각도 (라디안)
rotation_speed = 0.02

def multiply_matrix_vector(matrix, vector):
    """3x3 행렬과 3D 벡터를 곱합니다."""
    result = [0, 0, 0]
    for i in range(3):
        for j in range(3):
            result[i] += matrix[i][j] * vector[j]
    return tuple(result)

def get_rotation_matrix(axis, angle):
    """지정된 축과 각도에 대한 회전 행렬을 반환합니다."""
    c, s = math.cos(angle), math.sin(angle)
    if axis == 'x':
        return [[1, 0, 0], [0, c, -s], [0, s, c]]
    elif axis == 'y':
        return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    elif axis == 'z':
        return [[c, -s, 0], [s, c, 0], [0, 0, 1]]

# --- 메인 루프 ---
run = True
while run:
    # --- 이벤트 및 입력 처리 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # 마우스 카메라 이동 이벤트
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True
            mouse_last_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_clicked = False
            mouse_last_pos = None
        elif event.type == pygame.MOUSEWHEEL:
            camera_pos[2] += event.y * 0.5

    # 키보드 회전 입력
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]: rotation_angles[0] -= rotation_speed
    if keys[pygame.K_a]: rotation_angles[0] += rotation_speed
    if keys[pygame.K_w]: rotation_angles[1] -= rotation_speed
    if keys[pygame.K_s]: rotation_angles[1] += rotation_speed
    if keys[pygame.K_e]: rotation_angles[2] -= rotation_speed
    if keys[pygame.K_d]: rotation_angles[2] += rotation_speed
    if keys[pygame.K_SPACE]: rotation_angles = [0,0,0]

    # 마우스 드래그 카메라 이동
    if mouse_clicked and mouse_last_pos:
        current_mouse_pos = pygame.mouse.get_pos()
        dx = (current_mouse_pos[0] - mouse_last_pos[0]) / (WIDTH / 2) * mouse_sensitivity
        dy = (mouse_last_pos[1] - current_mouse_pos[1]) / (HEIGHT / 2) * mouse_sensitivity
        camera_pos[0] -= dx
        camera_pos[1] -= dy
        mouse_last_pos = current_mouse_pos

    # --- 렌더링 ---
    screen.fill((0, 0, 0))

    # 회전 행렬 계산 (Z -> X -> Y 순서로 적용)
    rot_mat_z = get_rotation_matrix('z', rotation_angles[2])
    rot_mat_x = get_rotation_matrix('x', rotation_angles[0])
    rot_mat_y = get_rotation_matrix('y', rotation_angles[1])

    projected_points = []
    for vertex in vertices:
        # 1. 회전 변환 (Model space -> World space, rotated)
        rotated_vertex = multiply_matrix_vector(rot_mat_z, vertex)
        rotated_vertex = multiply_matrix_vector(rot_mat_x, rotated_vertex)
        rotated_vertex = multiply_matrix_vector(rot_mat_y, rotated_vertex)

        # 2. 카메라 시점 변환 (World space -> View space)
        view_vertex = (
            rotated_vertex[0] - camera_pos[0],
            rotated_vertex[1] - camera_pos[1],
            rotated_vertex[2] - camera_pos[2]
        )

        # 3. 투영 변환 (View space -> Screen space)
        projected_point = projector.project(view_vertex)
        projected_points.append(projected_point)

    # 모서리 그리기
    for edge in edges:
        start_point = projected_points[edge[0]]
        end_point = projected_points[edge[1]]
        pygame.draw.line(screen, (255, 255, 255), start_point, end_point, 2)

    # 카메라 좌표 표시
    cam_text = f"Camera X: {camera_pos[0]:.2f} Y: {camera_pos[1]:.2f} Z: {camera_pos[2]:.2f}"
    text_surface = font.render(cam_text, True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))

    information = "Q,A : x-axis rotation\n W,S : y-axis rotation\n E,D : z-axis rotation"
    screen.blit(font.render(information, True, (255, 255, 255)), (10, 30))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
