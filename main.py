import pygame
import math

MAP_SIZE = 8
NUM_RAYS = 200
WIDTH, HEIGHT = 800, 600

# 8x8 2D 맵
tilemap = [
    [1,1,1,1,1,1,1,1],
    [1,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,1],
    [1,0,0,0,0,1,0,1],
    [1,0,0,0,0,0,0,1],
    [1,0,0,0,1,1,1,1],
    [1,1,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1],
]

def tile_render(tilemap, surf):
    tile_size = surf.get_width() / MAP_SIZE
    for i in range(MAP_SIZE):
        for j in range(MAP_SIZE):
            if tilemap[i][j]:
                pygame.draw.rect(surf, (195,195,195),
                                 pygame.Rect(tile_size * j, tile_size * i, tile_size, tile_size))
                pygame.draw.rect(surf, (0,0,0),
                                 pygame.Rect(tile_size * j, tile_size * i, tile_size, tile_size), width=1)
                
NEIGHBOR_OFFSET = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]

def tiles_around(pos):
    tiles = []
    tile_loc = (int(pos[0]), int(pos[1]))
    for offset in NEIGHBOR_OFFSET:
        check_loc = (tile_loc[0] + offset[0], tile_loc[1] + offset[1])
        if 0 <= check_loc[0] < MAP_SIZE and 0 <= check_loc[1] < MAP_SIZE and tilemap[check_loc[1]][check_loc[0]]:
            tiles.append(pygame.Rect(check_loc[0], check_loc[1], 1, 1))
    return tiles

def ray_points(pos, tilemap, angle, fov, num_rays=NUM_RAYS):
    px, py = pos  # pos는 '타일 좌표계'로 가정
    rays = []
    for i in range(num_rays):
        # 방향 단위 벡터(크기가 1임)
        ray_angle = math.radians(angle - fov/2 + (fov/num_rays)*i)
        rayDirX = math.cos(ray_angle)
        rayDirY = math.sin(ray_angle)

        # 타일 좌표
        mapX = int(px)
        mapY = int(py)

        deltaDistX = abs(1 / rayDirX) if rayDirX != 0 else float('inf') # y 방향으로 1타일 이동할 때 거리 
        deltaDistY = abs(1 / rayDirY) if rayDirY != 0 else float('inf') # x 방향으로 1타일 이동할 때 거리

        # 첫 타일까지의 거리
        if rayDirX < 0:
            stepX = -1
            sideDistX = (px - mapX) * deltaDistX
        else:
            stepX = 1
            sideDistX = (mapX + 1.0 - px) * deltaDistX

        if rayDirY < 0:
            stepY = -1
            sideDistY = (py - mapY) * deltaDistY
        else:
            stepY = 1
            sideDistY = (mapY + 1.0 - py) * deltaDistY

        hit = False
        while not hit:
            if sideDistX < sideDistY:
                sideDistX += deltaDistX
                mapX += stepX
                side = 0
            else:
                sideDistY += deltaDistY
                mapY += stepY
                side = 1

            # 범위 체크 (IndexError 방지)
            if mapX < 0 or mapX >= MAP_SIZE or mapY < 0 or mapY >= MAP_SIZE:
                hit = True
                break

            if tilemap[mapY][mapX]:
                hit = True

        if side == 0:
            dist = (mapX - px + (1 - stepX) / 2) / rayDirX
        else:
            dist = (mapY - py + (1 - stepY) / 2) / rayDirY

        endX = px + rayDirX * dist
        endY = py + rayDirY * dist
        corrected_dist = dist * math.cos(ray_angle - math.radians(angle))
        rays.append([(endX, endY), corrected_dist, side])

    return rays

def render_3d_view(surf, rays):
    wall_slice_width = WIDTH / NUM_RAYS
    for i, (point, dist, side) in enumerate(rays):
        if dist >= float('inf'): continue

        # 거리에 반비례하여 벽 높이 계산
        wall_height = HEIGHT / dist if dist > 0 else HEIGHT

        # 벽을 화면 중앙에 정렬
        draw_start = (HEIGHT / 2) - (wall_height / 2)
        draw_end = (HEIGHT / 2) + (wall_height / 2)

        # 거리에 따라 명암 조절 (멀수록 어둡게)
        shading = max(50, 255 - dist * 15)
        color = (shading, shading, shading)
        
        # X축, Y축 벽 색상 구분
        if side == 1:
            color = (max(0, color[0]-50), max(0, color[1]-50), max(0, color[2]-50))

        pygame.draw.rect(surf, color, (i * wall_slice_width, draw_start, wall_slice_width + 1, wall_height))

def ray_render(surf, pos, rays):
    tile_size = surf.get_width() / MAP_SIZE
    # pos를 타일 좌표계에서 픽셀 좌표로 변환
    player_px = pos[0] * tile_size
    player_py = pos[1] * tile_size

    points = [_[0] for _ in rays]
    for endX, endY in points:
        pygame.draw.line(surf, (255,255,0),
                         (player_px, player_py),
                         (endX * tile_size, endY * tile_size), 1)

def move_player(pos, angle, vel):
    rad_angle = math.radians(angle)
    
    # 전진/후진
    dx = math.cos(rad_angle) * vel[1]
    dy = math.sin(rad_angle) * vel[1]
    
    # 좌우 평행이동 (Strafe)
    dx += math.cos(rad_angle + math.pi/2) * vel[0]
    dy += math.sin(rad_angle + math.pi/2) * vel[0]

    # X축 이동
    pos[0] += dx
    hitbox = pygame.Rect(pos[0], pos[1], 1, 1)
    for tile in tiles_around(pos):
        if hitbox.colliderect(tile):
            if dx > 0:  # 오른쪽 충돌
                pos[0] = tile.left - 0.01
            elif dx < 0:  # 왼쪽 충돌
                pos[0] = tile.right + 0.01

    # Y축 이동
    pos[1] += dy
    hitbox = pygame.Rect(pos[0], pos[1], 1, 1)
    for tile in tiles_around(pos):
        if hitbox.colliderect(tile):
            if dy > 0:  # 아래쪽 충돌
                pos[1] = tile.top - 0.01
            elif dy < 0:  # 위쪽 충돌
                pos[1] = tile.bottom + 0.01

    return pos

def player_render(surf, pos):
    tile_size = surf.get_width() / MAP_SIZE
    pygame.draw.circle(surf, (255,0,0),
                       (int(pos[0] * tile_size), int(pos[1] * tile_size)), 3)

def draw_gradient_sky(surf):
    top_color = (135, 206, 235)  # 밝은 하늘색
    bottom_color = (0, 0, 0)     # 중앙에서 검정
    step = int(WIDTH / 60)       # 색상 변화 간격

    for y in range(0, HEIGHT // 2, step):
        # 진행 비율 (0 ~ 1)
        t = y * 2 / (HEIGHT)
        # 색 보간 (Lerp)
        r = int(top_color[0] * (1 - t) + bottom_color[0] * (t))
        g = int(top_color[1] * (1 - t) + bottom_color[1] * (t))
        b = int(top_color[2] * (1 - t) + bottom_color[2] * (t))

        pygame.draw.rect(surf, (r, g, b), (0, y, WIDTH, step))

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("레이캐스팅 구현")
clock = pygame.time.Clock()

display = pygame.Surface((200,200))

player_pos = [2.5, 2.5]  # 타일 좌표

x_movement = [False, False]
y_movement = [False, False]

velocity = 0.05
angle_speed = 2
player_angle = 0

mouse_last_pos = [0,0]
mouse_sensitivity = 0.5

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                y_movement[0] = True
            if event.key == pygame.K_s:
                y_movement[1] = True
            if event.key == pygame.K_d:
                x_movement[0] = True
            if event.key == pygame.K_a:
                x_movement[1] = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                y_movement[0] = False
            if event.key == pygame.K_s:
                y_movement[1] = False
            if event.key == pygame.K_d:
                x_movement[0] = False
            if event.key == pygame.K_a:
                x_movement[1] = False


    current_mouse_pos = pygame.mouse.get_pos()
    dx = (current_mouse_pos[0] - mouse_last_pos[0]) * mouse_sensitivity
    player_angle += dx
    mouse_last_pos = current_mouse_pos
        
    if pygame.key.get_pressed()[pygame.K_LEFT]: player_angle -= angle_speed
    if pygame.key.get_pressed()[pygame.K_RIGHT]: player_angle += angle_speed

    move_player(player_pos, player_angle, [(x_movement[0] - x_movement[1]) * velocity, (y_movement[0] - y_movement[1]) * velocity])

    draw_gradient_sky(screen)
    pygame.draw.rect(screen, (100, 100, 100), (0, HEIGHT/2, WIDTH, HEIGHT/2)) # 바닥 회색

    rays = ray_points(player_pos, tilemap, player_angle, 60)
    render_3d_view(screen, rays)
    display.fill((255,255,255))

    tile_render(tilemap, display)
    ray_render(display, player_pos, rays)
    player_render(display, player_pos)

    screen.blit(display, (WIDTH-200, HEIGHT-200))
    pygame.display.update()
    clock.tick(60)

pygame.quit()
