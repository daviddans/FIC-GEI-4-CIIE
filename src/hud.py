import pygame


class DebugHUD:
    def __init__(self, pantalla, ancho, alto):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.visible = True

        self.fuente = pygame.font.SysFont("Consolas", 16)

        self.COLOR_FONDO  = (10, 10, 10, 180)
        self.COLOR_TEXTO  = (0, 255, 100)
        self.COLOR_BORDE  = (0, 180, 60)
        self.COLOR_DIALOG = (255, 220, 80)   # amarillo para el diálogo activo

    def toggle(self):
        self.visible = not self.visible

    def draw(self, fps, jugador_pos, escena, dialogo_activo=None):
        """
        dialogo_activo — None, o dict con claves:
            "hablante" : str   (nombre del personaje)
            "texto"    : str   (línea actual)
            "progreso" : str   (p.ej. "2/3")
        """
        if not self.visible:
            return

        padding    = 10
        ancho_caja = 320
        line_h     = 22

        # ── Líneas fijas ─────────────────────────────────────────────
        lineas_fijas = [
            (f"FPS        : {fps:.0f}",                          self.COLOR_TEXTO),
            (f"Jugador    : ({jugador_pos[0]:.0f}, {jugador_pos[1]:.0f})", self.COLOR_TEXTO),
            (f"Escena     : {escena}",                           self.COLOR_TEXTO),
        ]

        # ── Bloque de diálogo ────────────────────────────────────────
        if dialogo_activo:
            progreso  = dialogo_activo.get("progreso", "")
            hablante  = dialogo_activo.get("hablante", "?")
            texto_raw = dialogo_activo.get("texto", "")
            # Truncar el texto si es muy largo para que quepa en la caja
            texto = texto_raw if len(texto_raw) <= 28 else texto_raw[:25] + "..."

            lineas_dialog = [
                (f"Diálogo    : [{progreso}]",          self.COLOR_DIALOG),
                (f"  Quién    : {hablante}",             self.COLOR_DIALOG),
                (f"  Texto    : {texto}",                self.COLOR_DIALOG),
            ]
        else:
            lineas_dialog = [
                ("Diálogo    : —",                       self.COLOR_TEXTO),
            ]

        todas = lineas_fijas + lineas_dialog
        alto_caja = len(todas) * line_h + padding * 2

        x = self.ancho - ancho_caja - 10
        y = 10

        # Fondo semitransparente
        superficie = pygame.Surface((ancho_caja, alto_caja), pygame.SRCALPHA)
        superficie.fill(self.COLOR_FONDO)
        self.pantalla.blit(superficie, (x, y))
        pygame.draw.rect(self.pantalla, self.COLOR_BORDE,
                         (x, y, ancho_caja, alto_caja), 1, border_radius=4)

        # Texto
        for i, (linea, color) in enumerate(todas):
            surf = self.fuente.render(linea, True, color)
            self.pantalla.blit(surf, (x + padding, y + padding + i * line_h))