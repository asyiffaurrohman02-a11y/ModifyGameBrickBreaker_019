

    def draw_background(self):
        # Smooth dark-indigo to midnight gradient.
        for y in range(HEIGHT):
            t = y / HEIGHT
            color = (int(17 - 9 * t), int(22 - 10 * t), int(48 - 18 * t))
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))
        # Fine geometric grid.
        for x in range(0, WIDTH, 50):
            pygame.draw.line(screen, (22, 31, 59), (x, PLAY_TOP), (x, HEIGHT), 1)
        for y in range(PLAY_TOP, HEIGHT, 50):
            pygame.draw.line(screen, (22, 31, 59), (0, y), (WIDTH, y), 1)
        # Decorative orbital arcs in the corners.
        pygame.draw.arc(screen, (34, 51, 83), (-130, 100, 360, 360), 4.2, 5.8, 2)
        pygame.draw.arc(screen, (34, 51, 83), (WIDTH - 240, 250, 340, 340), 1.0, 2.7, 2)
        for x, y, radius, speed in self.stars:
            pygame.draw.circle(screen, (95, 115, 155), (int(x), int(y)), radius)
        pygame.draw.line(screen, (75, 130, 150), (18, PLAY_TOP - 9),
                         (WIDTH - 18, PLAY_TOP - 9), 2)

    