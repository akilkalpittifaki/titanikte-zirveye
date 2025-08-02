import pygame
import sys

from constants import WIDTH, HEIGHT, FPS, STOCK_MARKET, PLAYING, WHITE, BLACK
from game_world import GameWorld

def main():
    """Ana oyun fonksiyonu"""
    # Pygame başlat
    pygame.init()
    
    # Pencere modu - Yeniden boyutlandırılabilir pencere
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Titanikte Zirveye")
    clock = pygame.time.Clock()
    
    # Ekran boyutları
    current_width, current_height = WIDTH, HEIGHT
    
    # Ekran boyutu önayarları
    resolution_presets = [
        (800, 600),    # Küçük ekran
        (1280, 720),   # HD
        (1600, 900),   # HD+
        (1920, 1080)   # Full HD
    ]
    current_preset_index = 3  # Başlangıçta Full HD
    
    # Tam ekran durumu
    fullscreen = False
    
    # Oyun dünyasını oluştur
    game_world = GameWorld()
    game_world.game_state = PLAYING  # Direkt oyun modunda başlat
    
    # ESC tuşu için flag - KALDIRILDI
    # exit_stock_flag = False
    last_state = PLAYING
    
    # Bilgi mesajı ve zamanlayıcı
    info_message = ""
    info_timer = 0
    
    # Ana oyun döngüsü
    running = True
    while running:
        # FPS sınırla
        dt = clock.tick(FPS)
        
        # Zorla oyun durumu kontrolü ve güncelleme - KALDIRILDI
        # if exit_stock_flag:
        #     game_world.game_state = PLAYING
        #     game_world.player.current_room = "güverte"
        #     exit_stock_flag = False
        #     print("Ana döngüde zorla güncelleme yapıldı!")
        
        # Zorla ekran güncellemesi - KALDIRILDI
        # if exit_stock_flag:
        #     game_world.draw(screen)
        #     pygame.display.flip()
        #     print("Ekran zorla güncellendi!")
        
        # Durum değişimi kontrolü
        if last_state != game_world.game_state:
            print(f"Oyun durumu değişti: {last_state} -> {game_world.game_state}")
            pygame.time.wait(100)  # Durum değişiminde kısa bir bekleme
            last_state = game_world.game_state
        
        # Olayları kontrol et
        for event in pygame.event.get():
            # Çıkış
            if event.type == pygame.QUIT:
                running = False
            
            # Pencere yeniden boyutlandırma
            elif event.type == pygame.VIDEORESIZE:
                if not fullscreen:  # Tam ekran modunda değilse yeniden boyutlandır
                    current_width, current_height = event.size
                    screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
                    print(f"Pencere yeniden boyutlandırıldı: {current_width}x{current_height}")
            
            # ESC tuşuna basıldığında - tam ekrandan çıkış
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if fullscreen:
                    # Tam ekrandaysa pencere moduna geç
                    fullscreen = False
                    screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
                    info_message = "Pencere Modu"
                    info_timer = 60  # 1 saniye göster (60 FPS)
                elif game_world.game_state == STOCK_MARKET:
                    # Borsa ekranındayken çıkış
                    print("Ana döngüde ESC tuşu algılandı!")
                    game_world.exit_stock_market()
                else:
                    # Ana oyun ekranında çık
                    running = False
                continue
                
            # Fare tıklaması
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sol tık
                    print(f"Ana döngüde fare tıklaması: {event.pos}")
                    
                    # Başlık çubuğuna tıklama kontrolü (üst 40 piksel)
                    if event.pos[1] <= 40:
                        print("Başlık çubuğuna tıklandı! Tam ekran modunu değiştir.")
                        fullscreen = not fullscreen
                        
                        # Tam ekran modunu değiştir
                        if fullscreen:
                            screen = pygame.display.set_mode((current_width, current_height), pygame.FULLSCREEN)
                            info_message = "Tam Ekran Modu"
                        else:
                            screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
                            info_message = "Pencere Modu"
                        info_timer = 60  # 1 saniye göster
                        continue
                    
                    # Borsa ekranında GERİ butonuna tıklama kontrolü
                    if game_world.game_state == STOCK_MARKET:
                        if current_width//2 - 50 <= event.pos[0] <= current_width//2 + 50 and current_height - 40 <= event.pos[1] <= current_height - 10:
                            print("Ana döngüde geri butonu algılandı!")
                            game_world.exit_stock_market() # Doğrudan çağrı yeterli
                            continue
                    
                    result = game_world.handle_click(event.pos)
                    if result == "quit":
                        running = False
            
            # Tuş basımı
            elif event.type == pygame.KEYDOWN:
                print(f"Ana döngüde tuş basımı: {event.key}")
                
                # F11 tuşu ile tam ekran modunu değiştir
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((current_width, current_height), pygame.FULLSCREEN)
                        info_message = "Tam Ekran Modu"
                    else:
                        screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
                        info_message = "Pencere Modu"
                    info_timer = 60  # 1 saniye göster
                
                # F1, F2, F3, F4 tuşları ile çözünürlük değiştir (pencere modunda)
                elif event.key in [pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4] and not fullscreen:
                    preset_index = event.key - pygame.K_F1  # F1=0, F2=1, F3=2, F4=3
                    
                    if 0 <= preset_index < len(resolution_presets):
                        current_preset_index = preset_index
                        current_width, current_height = resolution_presets[preset_index]
                        screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
                        info_message = f"Çözünürlük: {current_width}x{current_height}"
                        info_timer = 60  # 1 saniye göster
                
                else:
                    game_world.handle_key(event.key)
        
        # Oyunu güncelle
        game_world.update(dt)
        
        # Çiz
        game_world.draw(screen)
        
        # Bilgi mesajını göster
        if info_timer > 0:
            # Bilgi mesajı için yarı saydam arka plan
            info_font = pygame.font.SysFont("Arial", 24)
            info_text = info_font.render(info_message, True, WHITE)
            info_rect = info_text.get_rect(center=(current_width // 2, 40))
            
            # Arka plan dikdörtgeni
            bg_rect = info_rect.copy()
            bg_rect.inflate_ip(20, 10)  # Biraz daha büyük yap
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(180)  # Yarı saydam
            bg_surface.fill(BLACK)
            screen.blit(bg_surface, bg_rect)
            
            # Mesajı çiz
            screen.blit(info_text, info_rect)
            
            # Zamanlayıcıyı azalt
            info_timer -= 1
        
        # Ekranı güncelle
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

# Oyunu başlat
if __name__ == "__main__":
    main()
