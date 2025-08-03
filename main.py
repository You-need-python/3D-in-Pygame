import math

class Projector:
    """
    3D 좌표를 2D 화면 좌표로 변환하는 역할을 담당합니다.
    """
    def __init__(self, width, height, fov=60):
        self.width = width
        self.height = height
        self.fov = fov
        self.aspect_ratio = width / height
        # 시야각(fov)과 탄젠트를 이용해 투영 평면까지의 거리(d)를 계산합니다.
        self.d = 1 / math.tan(math.radians(self.fov / 2))

    def project(self, point_3d):
        """
        주어진 3D 점을 2D 화면 좌표로 투영합니다.
        """
        x, y, z = point_3d
        
        # 점이 카메라와 같은 평면에 있어 0으로 나누는 것을 방지합니다.
        if z == 0:
            z = 0.00001

        # 3D 좌표를 정규화된 장치 좌표(NDC)로 변환합니다.
        # 이 좌표는 보통 화면 비율에 맞춰진 -1에서 1 사이의 값을 가집니다.
        ndc_x = (x * self.d) / (self.aspect_ratio * z)
        ndc_y = (y * self.d) / z

        # NDC 좌표를 실제 Pygame 화면 좌표로 변환합니다.
        # 화면의 중앙을 (0, 0)으로 간주하여 계산합니다.
        screen_x = int(ndc_x * self.width / 2 + self.width / 2)
        # Pygame의 y축은 아래로 갈수록 증가하므로 y좌표의 부호를 반전시킵니다.
        screen_y = int(-ndc_y * self.height / 2 + self.height / 2)

        return (screen_x, screen_y)