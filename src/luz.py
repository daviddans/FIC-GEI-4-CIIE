import pygame

class Light:
    def __init__(self, pos, radius, intensidad=180):
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.intensidad = intensidad

        self.image = self._crear_luz(radius)
        self.rect = self.image.get_rect(center=pos)

    def _crear_luz(self, radius):
        luz = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

        for r in range(radius, 0, -1):
            alpha = int(self.intensidad * (r / radius))
            pygame.draw.circle(
                luz,
                (255, 255, 200, alpha),
                (radius, radius),
                r
            )
        return luz

    def update(self, pos):
        self.pos = pygame.Vector2(pos)
        self.rect.center = pos

    # -------------------------------
    # Raycast genérico
    # -------------------------------
    def raycast(self, destino, grupo_sprites):
        objeto_mas_cercano = None
        distancia_minima = float("inf")

        for sprite in grupo_sprites:
            if sprite.rect.clipline(self.pos, destino):
                distancia = self.pos.distance_to(sprite.rect.center)

                if distancia < distancia_minima:
                    distancia_minima = distancia
                    objeto_mas_cercano = sprite

        return objeto_mas_cercano

    # -------------------------------
    # Iluminar un objeto específico
    # -------------------------------
    def iluminar_objeto(self, surface, obj, grupo_sprites):
        # Comprobar distancia
        if self.pos.distance_to(obj.rect.center) > self.radius:
            return

        # Comprobar que no haya algo bloqueando
        impacto = self.raycast(obj.rect.center, grupo_sprites)
        if impacto != obj:
            return

        # Calcular offset relativo
        offset_x = obj.rect.x - (self.pos.x - self.radius)
        offset_y = obj.rect.y - (self.pos.y - self.radius)

        # Superficie temporal del tamaño del objeto
        temp = pygame.Surface(obj.rect.size, pygame.SRCALPHA)
        temp.blit(self.image, (-offset_x, -offset_y))

        # Aplicar brillo
        surface.blit(temp, obj.rect.topleft, special_flags=pygame.BLEND_ADD)