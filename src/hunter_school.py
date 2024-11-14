import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Supernatural Hunter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
BROWN = (165, 42, 42)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
DARK_RED = (139, 0, 0)  # Dunkleres Rot für Boss

# Player
player_size = 40
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 5
player_alive = True

# Bullets
bullets = []
bullet_speed = 10
bullet_size = 5

# Monster bullets
monster_bullets = []
monster_bullet_speed = 4  # Von 8 auf 4 reduziert für langsamere Boss-Kugeln
monster_bullet_size = 8

# Monsters
monster_size = 40
monsters = []
monster_speed = 1
# Skalierung der Monster-Leben mit Level
monster_max_health = 3  # Basis-Lebenspunkte, wird mit Level multipliziert
monster_health = monster_max_health

# Boss
boss = None
boss_size = 80
boss_base_health = 10  # Basis-Gesundheit für Level 1
boss_base_speed = 0.5  # Basis-Geschwindigkeit für Level 1
boss_shoot_delay = 90  # Von 60 auf 90 erhöht für langsameres Schießen
boss_attack_patterns = ['single', 'triple', 'circle', 'spiral', 'wave']  # Erweiterte Angriffsmuster

# Boss Intro Animation
boss_intro_active = False
boss_intro_timer = 0
BOSS_INTRO_DURATION = 180  # 3 Sekunden
boss_intro_text_size = 1
boss_intro_flash = False

# Level Complete Screen
level_complete = False
level_complete_confirmed = False

# Konfetti
confetti_particles = []
confetti_colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255)]
confetti_active = False
confetti_timer = 0
CONFETTI_DURATION = 120  # 2 Sekunden bei 60 FPS

# Wave System
current_wave = 1
monsters_per_wave = 3
wave_active = True
wave_cleared = False
level = 1

# Locations
locations = [
    {"name": "Hunter Schule", "color": GREEN},
    {"name": "Verlassenes Haus", "color": BROWN},
    {"name": "Friedhof", "color": GRAY}
]
current_location = 0

# Font
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Game State
game_started = False

def create_confetti():
    for _ in range(100):
        particle = {
            'x': random.randint(0, WIDTH),
            'y': random.randint(-50, 0),
            'speed_y': random.randint(5, 15),
            'speed_x': random.randint(-3, 3),
            'color': random.choice(confetti_colors),
            'size': random.randint(5, 10)
        }
        confetti_particles.append(particle)

def update_confetti():
    global confetti_particles
    for particle in confetti_particles[:]:
        particle['y'] += particle['speed_y']
        particle['x'] += particle['speed_x']
        if particle['y'] > HEIGHT:
            confetti_particles.remove(particle)

def draw_confetti():
    for particle in confetti_particles:
        pygame.draw.rect(screen, particle['color'], 
                        (particle['x'], particle['y'], 
                         particle['size'], particle['size']))

def draw_player():
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))
    pygame.draw.circle(screen, WHITE, (player_x + 10, player_y + 15), 5)
    pygame.draw.circle(screen, WHITE, (player_x + 30, player_y + 15), 5)

def draw_ghost(x, y, health):
    pygame.draw.circle(screen, WHITE, (x + 20, y + 20), 20)
    pygame.draw.rect(screen, WHITE, (x, y + 20, 40, 20))
    pygame.draw.circle(screen, BLACK, (x + 13, y + 15), 4)
    pygame.draw.circle(screen, BLACK, (x + 27, y + 15), 4)
    # Lebensleiste
    max_health = monster_max_health * level  # Skalierung mit Level
    health_width = (health / max_health) * monster_size
    pygame.draw.rect(screen, RED, (x, y - 10, monster_size, 5))
    pygame.draw.rect(screen, GREEN, (x, y - 10, health_width, 5))

def draw_zombie(x, y, health):
    pygame.draw.rect(screen, GREEN, (x, y, 40, 40))
    pygame.draw.circle(screen, RED, (x + 10, y + 10), 5)
    pygame.draw.circle(screen, RED, (x + 30, y + 10), 5)
    pygame.draw.line(screen, BLACK, (x + 10, y + 30), (x + 30, y + 30), 3)
    # Lebensleiste
    max_health = monster_max_health * level  # Skalierung mit Level
    health_width = (health / max_health) * monster_size
    pygame.draw.rect(screen, RED, (x, y - 10, monster_size, 5))
    pygame.draw.rect(screen, GREEN, (x, y - 10, health_width, 5))

def draw_vampire(x, y, health):
    pygame.draw.polygon(screen, PURPLE, [(x, y + 40), (x + 20, y), (x + 40, y + 40)])
    pygame.draw.circle(screen, RED, (x + 13, y + 20), 4)
    pygame.draw.circle(screen, RED, (x + 27, y + 20), 4)
    pygame.draw.polygon(screen, WHITE, [(x + 15, y + 30), (x + 20, y + 40), (x + 25, y + 30)])
    # Lebensleiste
    max_health = monster_max_health * level  # Skalierung mit Level
    health_width = (health / max_health) * monster_size
    pygame.draw.rect(screen, RED, (x, y - 10, monster_size, 5))
    pygame.draw.rect(screen, GREEN, (x, y - 10, health_width, 5))

def draw_boss():
    if boss:
        x, y = boss['x'], boss['y']
        # Hauptkörper
        pygame.draw.rect(screen, DARK_RED, (x, y, boss_size, boss_size))
        
        # Gruselige Augen
        eye_color = RED
        pygame.draw.circle(screen, eye_color, (x + 20, y + 20), 15)
        pygame.draw.circle(screen, eye_color, (x + 60, y + 20), 15)
        pygame.draw.circle(screen, BLACK, (x + 20, y + 20), 8)
        pygame.draw.circle(screen, BLACK, (x + 60, y + 20), 8)
        
        # Zackiger Mund
        mouth_points = [(x + 10, y + 50), (x + 25, y + 60), 
                       (x + 40, y + 50), (x + 55, y + 60), 
                       (x + 70, y + 50)]
        pygame.draw.lines(screen, BLACK, False, mouth_points, 4)
        
        # Hörner
        pygame.draw.polygon(screen, BLACK, [(x, y), (x - 10, y - 20), (x + 20, y)])
        pygame.draw.polygon(screen, BLACK, [(x + boss_size, y), 
                                         (x + boss_size + 10, y - 20), 
                                         (x + boss_size - 20, y)])
        
        # Health bar
        health_width = (boss['health'] / (boss_base_health * level)) * boss_size  # Skalierung mit Level
        pygame.draw.rect(screen, RED, (x, y - 10, boss_size, 5))
        pygame.draw.rect(screen, GREEN, (x, y - 10, health_width, 5))

def draw_boss_intro():
    global boss_intro_text_size, boss_intro_flash
    
    # Hintergrund-Flash-Effekt
    if boss_intro_flash:
        screen.fill(RED)
    else:
        screen.fill(BLACK)
    boss_intro_flash = not boss_intro_flash
    
    # Pulsierender Text
    boss_text = large_font.render("BOSS KAMPF!", True, WHITE)
    text_width = boss_text.get_width() * boss_intro_text_size
    text_height = boss_text.get_height() * boss_intro_text_size
    scaled_text = pygame.transform.scale(boss_text, (int(text_width), int(text_height)))
    
    screen.blit(scaled_text, 
                (WIDTH//2 - text_width//2, 
                 HEIGHT//2 - text_height//2))
    
    # Text-Größe aktualisieren
    boss_intro_text_size = 1 + abs(math.sin(pygame.time.get_ticks() * 0.005))

def draw_level_complete():
    screen.fill(BLACK)
    complete_text = large_font.render(f"Level {level} Complete!", True, WHITE)
    continue_text = font.render("Drücke LEERTASTE zum Fortfahren", True, WHITE)
    
    screen.blit(complete_text, 
                (WIDTH//2 - complete_text.get_width()//2, 
                 HEIGHT//2 - complete_text.get_height()))
    screen.blit(continue_text,
                (WIDTH//2 - continue_text.get_width()//2,
                 HEIGHT//2 + continue_text.get_height()))

def draw_monsters():
    for monster in monsters:
        if monster['type'] == 'ghost':
            draw_ghost(monster['x'], monster['y'], monster['health'])
        elif monster['type'] == 'zombie':
            draw_zombie(monster['x'], monster['y'], monster['health'])
        elif monster['type'] == 'vampire':
            draw_vampire(monster['x'], monster['y'], monster['health'])
    if boss:
        draw_boss()

def spawn_monster():
    # Mindestabstand zum Spieler
    min_distance = 200
    
    while True:
        x = random.randint(0, WIDTH - monster_size)
        y = random.randint(0, HEIGHT - monster_size)
        
        # Berechne Abstand zum Spieler
        dx = x - player_x
        dy = y - player_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Wenn der Abstand groß genug ist, spawne das Monster
        if distance >= min_distance:
            monster_type = random.choice(['ghost', 'zombie', 'vampire'])
            monsters.append({
                'x': x, 
                'y': y, 
                'type': monster_type,
                'health': monster_max_health * level  # Skalierung mit Level
            })
            break

def spawn_boss():
    global boss, boss_intro_active, boss_intro_timer
    # Boss spawnt immer oben mittig
    boss = {
        'x': WIDTH // 2 - boss_size // 2,
        'y': -boss_size,  # Startet außerhalb des Bildschirms
        'health': boss_base_health * level,  # Skalierung mit Level
        'shoot_cooldown': 0,
        'target_y': 50,  # Zielposition für die Eingangsanimation
        'pattern': random.choice(boss_attack_patterns[:min(level + 2, len(boss_attack_patterns))])  # Mehr Muster mit höherem Level
    }
    boss_intro_active = True
    boss_intro_timer = 0

def boss_shoot_pattern(pattern, x, y):
    global monster_bullets
    dx = player_x - x
    dy = player_y - y
    dist = math.sqrt(dx * dx + dy * dy)
    if dist != 0:
        dx = dx / dist
        dy = dy / dist
        
        if pattern == 'single':
            monster_bullets.append({'x': x, 'y': y, 'dx': dx, 'dy': dy})
        elif pattern == 'triple':
            angles = [-30, 0, 30]
            for angle in angles:
                rad = math.radians(angle)
                new_dx = dx * math.cos(rad) - dy * math.sin(rad)
                new_dy = dx * math.sin(rad) + dy * math.cos(rad)
                monster_bullets.append({'x': x, 'y': y, 'dx': new_dx, 'dy': new_dy})
        elif pattern == 'circle':
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                monster_bullets.append({
                    'x': x, 
                    'y': y, 
                    'dx': math.cos(rad), 
                    'dy': math.sin(rad)
                })
        elif pattern == 'spiral':
            angle = pygame.time.get_ticks() / 100
            rad = math.radians(angle)
            monster_bullets.append({
                'x': x,
                'y': y,
                'dx': math.cos(rad),
                'dy': math.sin(rad)
            })
        elif pattern == 'wave':
            for i in range(3):
                offset = math.sin(pygame.time.get_ticks() / 500 + i)
                monster_bullets.append({
                    'x': x,
                    'y': y,
                    'dx': dx + offset * 0.5,
                    'dy': dy
                })

def move_monsters():
    global player_alive
    for monster in monsters:
        dx = player_x - monster['x']
        dy = player_y - monster['y']
        dist = math.sqrt(dx * dx + dy * dy)
        if dist != 0:
            dx = dx / dist * monster_speed
            dy = dy / dist * monster_speed
            monster['x'] += dx
            monster['y'] += dy
        
        if (abs(monster['x'] - player_x) < player_size and 
            abs(monster['y'] - player_y) < player_size):
            player_alive = False
            
    if boss and not boss_intro_active:
        # Normale Boss-Bewegung
        if boss['y'] < boss['target_y']:
            boss['y'] += 2  # Sanfte Eingangsanimation
        else:
            dx = player_x - boss['x']
            dy = player_y - boss['y']
            dist = math.sqrt(dx * dx + dy * dy)
            if dist != 0:
                dx = dx / dist * (boss_base_speed * (1 + level * 0.1))  # Skalierung mit Level
                dy = dy / dist * (boss_base_speed * (1 + level * 0.1))
                boss['x'] += dx
                boss['y'] += dy
            
        if (abs(boss['x'] - player_x) < player_size + boss_size//2 and 
            abs(boss['y'] - player_y) < player_size + boss_size//2):
            player_alive = False
            
        # Boss shooting
        boss['shoot_cooldown'] -= 1
        if boss['shoot_cooldown'] <= 0:
            boss_shoot_pattern(
                boss['pattern'],
                boss['x'] + boss_size//2,
                boss['y'] + boss_size//2
            )
            boss['shoot_cooldown'] = boss_shoot_delay

def draw_bullets():
    for bullet in bullets:
        pygame.draw.circle(screen, YELLOW, (int(bullet['x']), int(bullet['y'])), bullet_size)
    for bullet in monster_bullets:
        pygame.draw.circle(screen, RED, (int(bullet['x']), int(bullet['y'])), monster_bullet_size)

def move_bullets():
    for bullet in bullets[:]:
        bullet['x'] += bullet['dx'] * bullet_speed
        bullet['y'] += bullet['dy'] * bullet_speed
        if bullet['x'] < 0 or bullet['x'] > WIDTH or bullet['y'] < 0 or bullet['y'] > HEIGHT:
            bullets.remove(bullet)
            
    for bullet in monster_bullets[:]:
        bullet['x'] += bullet['dx'] * monster_bullet_speed
        bullet['y'] += bullet['dy'] * monster_bullet_speed
        if bullet['x'] < 0 or bullet['x'] > WIDTH or bullet['y'] < 0 or bullet['y'] > HEIGHT:
            monster_bullets.remove(bullet)
        elif (abs(bullet['x'] - player_x - player_size//2) < player_size//2 and
              abs(bullet['y'] - player_y - player_size//2) < player_size//2):
            monster_bullets.remove(bullet)
            global player_alive
            player_alive = False

def check_bullet_collision():
    global monsters, bullets, wave_cleared, boss, level, confetti_active, level_complete  
    for bullet in bullets[:]:
        for monster in monsters[:]:
            if (monster['x'] < bullet['x'] < monster['x'] + monster_size and
                monster['y'] < bullet['y'] < monster['y'] + monster_size):
                monster['health'] -= 1
                bullets.remove(bullet)
                if monster['health'] <= 0:
                    monsters.remove(monster)
                if len(monsters) == 0 and not boss:
                    wave_cleared = True
                break
                
        if boss and bullet in bullets:  # Check if bullet wasn't already removed
            if (boss['x'] < bullet['x'] < boss['x'] + boss_size and
                boss['y'] < bullet['y'] < boss['y'] + boss_size):
                boss['health'] -= 1
                bullets.remove(bullet)
                if boss['health'] <= 0:
                    boss = None
                    wave_cleared = True
                    level_complete = True
                    confetti_active = True
                    create_confetti()

def draw_hud():
    location_text = font.render(f"Location: {locations[current_location]['name']}", True, WHITE)
    screen.blit(location_text, (10, 10))
    monsters_text = font.render(f"Monsters: {len(monsters)}", True, WHITE)
    screen.blit(monsters_text, (10, 50))
    wave_text = font.render(f"Wave: {current_wave} Level: {level}", True, WHITE)
    screen.blit(wave_text, (10, 90))

def draw_start_screen():
    screen.fill(BLACK)
    
    title_text = font.render("Grüße an Tag-Team double M,", True, WHITE)
    subtitle_text = font.render("Viel Spasß in der Hunter School.", True, WHITE)
    author_text = font.render("by Jason flying with cursor", True, WHITE)
    
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 100))
    screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//2))
    screen.blit(author_text, (WIDTH//2 - author_text.get_width()//2, HEIGHT//2 + 100))
    
    pygame.draw.line(screen, WHITE, (WIDTH//4, HEIGHT//2 + 50), (3*WIDTH//4, HEIGHT//2 + 50), 2)

def main():
    global player_x, player_y, current_location, monsters, bullets, current_wave
    global wave_active, wave_cleared, monsters_per_wave, player_alive, boss, monster_bullets
    global level, confetti_active, confetti_timer, game_started, boss_intro_active
    global boss_intro_timer, level_complete, level_complete_confirmed

    # Initialisiere erste Welle mit Monstern
    for _ in range(monsters_per_wave):
        spawn_monster()

    clock = pygame.time.Clock()
    shoot_cooldown = 0
    shoot_delay = 10  # Verzögerung zwischen Schüssen (in Frames)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not game_started:
                    game_started = True
                elif level_complete and event.key == pygame.K_SPACE:
                    level_complete_confirmed = True

        if not game_started:
            draw_start_screen()
            pygame.display.flip()
            continue

        if not player_alive:
            game_over_text = font.render("Game Over! Drücke R zum Neustarten", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - 200, HEIGHT//2))
            pygame.display.flip()
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                player_alive = True
                player_x = WIDTH // 2
                player_y = HEIGHT // 2
                monsters = []
                bullets = []
                monster_bullets = []
                current_wave = 1
                monsters_per_wave = 3  # Start mit 3 Monstern
                wave_cleared = False
                wave_active = True
                current_location = 0
                boss = None
                level = 1
                confetti_active = False
                confetti_particles.clear()
                level_complete = False
                level_complete_confirmed = False
                # Initialisiere erste Welle nach Neustart
                for _ in range(monsters_per_wave):
                    spawn_monster()
            continue

        if level_complete:
            draw_level_complete()
            pygame.display.flip()
            if level_complete_confirmed:
                level += 1
                current_wave = 1
                monsters_per_wave = 3
                wave_cleared = False
                wave_active = True
                level_complete = False
                level_complete_confirmed = False
                confetti_active = False
                confetti_particles.clear()
                # Automatischer Locationwechsel bei neuem Level
                current_location = (current_location + 1) % len(locations)
                for _ in range(monsters_per_wave):
                    spawn_monster()
            continue

        keys = pygame.key.get_pressed()
        
        # Bewegung
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y > 0:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < HEIGHT - player_size:
            player_y += player_speed
        
        # Schießen
        if shoot_cooldown == 0:
            if keys[pygame.K_w]:
                bullets.append({'x': player_x + player_size // 2, 'y': player_y + player_size // 2, 'dx': 0, 'dy': -1})
                shoot_cooldown = shoot_delay
            elif keys[pygame.K_s]:
                bullets.append({'x': player_x + player_size // 2, 'y': player_y + player_size // 2, 'dx': 0, 'dy': 1})
                shoot_cooldown = shoot_delay
            elif keys[pygame.K_a]:
                bullets.append({'x': player_x + player_size // 2, 'y': player_y + player_size // 2, 'dx': -1, 'dy': 0})
                shoot_cooldown = shoot_delay
            elif keys[pygame.K_d]:
                bullets.append({'x': player_x + player_size // 2, 'y': player_y + player_size // 2, 'dx': 1, 'dy': 0})
                shoot_cooldown = shoot_delay

        # Wave System
        if wave_cleared and not wave_active:
            if current_wave % 5 == 0:  # Boss wave
                if not boss_intro_active and not boss:
                    spawn_boss()
            else:
                current_wave += 1
                monsters_per_wave = 3 + (current_wave + level - 1) // 2
                for _ in range(monsters_per_wave):
                    spawn_monster()
                wave_active = True
                wave_cleared = False
        
        if len(monsters) == 0 and not boss and wave_active:
            wave_active = False
            wave_cleared = True

        # Boss Intro Animation
        if boss_intro_active:
            boss_intro_timer += 1
            draw_boss_intro()
            if boss_intro_timer >= BOSS_INTRO_DURATION:
                boss_intro_active = False
                wave_active = True
                wave_cleared = False
        else:
            move_monsters()
            move_bullets()
            check_bullet_collision()

            if shoot_cooldown > 0:
                shoot_cooldown -= 1

            # Alles zeichnen
            screen.fill(locations[current_location]['color'])
            draw_player()
            draw_monsters()
            draw_bullets()
            draw_hud()
            
            if confetti_active:
                update_confetti()
                draw_confetti()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()