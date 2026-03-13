import pygame

class DebugHUD:
    def __init__(self, pantalla, ancho, alto):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.visible = True  # toggle con F3

        self.fuente = pygame.font.SysFont("Consolas", 16)

        self.COLOR_FONDO  = (10, 10, 10, 180)
        self.COLOR_TEXTO  = (0, 255, 100)    # verde terminal
        self.COLOR_BORDE  = (0, 180, 60)

    def toggle(self):
        self.visible = not self.visible

    def draw(self, fps, jugador_pos, escena, dialogo_activo=None):
        if not self.visible:
            return

        lineas = [
            f"FPS        : {fps:.0f}",
            f"Jugador    : ({jugador_pos[0]:.0f}, {jugador_pos[1]:.0f})",
            f"Escena     : {escena}",
            f"Diálogo    : {dialogo_activo if dialogo_activo else '—'}",
        ]

        padding  = 10
        ancho_caja = 260
        alto_caja  = len(lineas) * 22 + padding * 2

        x = self.ancho - ancho_caja - 10
        y = 10

        # Fondo semitransparente
        superficie = pygame.Surface((ancho_caja, alto_caja), pygame.SRCALPHA)
        superficie.fill(self.COLOR_FONDO)
        self.pantalla.blit(superficie, (x, y))
        pygame.draw.rect(self.pantalla, self.COLOR_BORDE,
                         (x, y, ancho_caja, alto_caja), 1, border_radius=4)

        # Líneas de texto
        for i, linea in enumerate(lineas):
            surf = self.fuente.render(linea, True, self.COLOR_TEXTO)
            self.pantalla.blit(surf, (x + padding, y + padding + i * 22))