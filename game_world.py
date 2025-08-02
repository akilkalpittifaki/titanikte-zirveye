import pygame
import math
import random # Duman için eklendi
from datetime import datetime, timedelta
import os

from constants import *
from player import Player
from stock import Stock

class GameWorld:
    """Oyun dünyası sınıfı"""
    def __init__(self):
        """Oyun dünyasını başlatır"""
        # Oyuncuyu başlat (başlangıç pozisyonu: ekranın ortası)
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        
        # Tarih takibi
        self.current_date = "April 10, 1912"
        self.end_date = "April 15, 1912"  # Titanik'in battığı tarih: 15 Nisan 1912
        self.day_count = 1
        
        # Zaman takibi için değişkenler
        self.elapsed_time = 0
        self.day_duration = 5 * 60 * 1000  # 5 dakika (milisaniye cinsinden)
        
        # Arka plan görselleri ve pencere boyutu takibi
        self.backgrounds = {
            "güverte": None,     # Güverte arka plan görseli
            "kabin": None,       # Kabin arka plan görseli
            "çalışma_alanı": None, # Çalışma alanı arka plan görseli
            "borsa": None        # Borsa arka plan görseli
        }
        self.last_window_size = pygame.display.get_surface().get_size()
        
        # Hisse senetleri tanımları
        self.stocks = {
            "WHITE STAR LINE": {"price": 100, "volatility": 0.5, "trend": 0.2, "history": [100]},
            "CUNARD LINE": {"price": 80, "volatility": 0.3, "trend": 0.0, "history": [80]},
            "P&O STEAM": {"price": 60, "volatility": 0.7, "trend": -0.1, "history": [60]},
            "HAMBURG AMERICA": {"price": 75, "volatility": 0.4, "trend": 0.1, "history": [75]},
            "AUSTRO AMERICANA": {"price": 45, "volatility": 0.8, "trend": -0.2, "history": [45]}
        }
        
        # NPCler ve diyaloglar daha sonra eklenecek
        self.npcs = []
        
        self.selected_stock = None
        self.stock_amount = 1
        self.dialog_text = ""
        self.dialog_options = []
        
        # Güverte çizimi için eklenenler
        self.smoke_particles = [] # Bacağı dumanı için
        
        # Altın para için gerekli değişkenler
        self.altin_image = None
        self.altin_pos = (WIDTH - 600, HEIGHT - 400)  # Resimde işaretlenen konum
        self.altin_visible = True
        self.altin_parlama = 0  # Parlama efekti için değer
        self.parlama_yonu = 1   # Parlama yönü (artıyor/azalıyor)
        
        # Çanta sistemi
        self.canta_image = None
        self.canta_visible = False  # Başlangıçta çanta görünmez
        self.canta_position = (WIDTH - 100, HEIGHT - 100)  # Sağ alt köşe
        
        # Diyalog sistemi
        self.dialog_active = False
        self.dialog_text = ""
        self.dialog_options = []
        self.dialog_callback = None  # Diyalog sonrası çağrılacak fonksiyon
        
        # Veritabanı bağlantısını dene
        self.init_database()
        
        # Oyun durumu
        self.game_state = MAIN_MENU
        
    def update(self, dt):
        """Oyun durumunu günceller"""
        if self.game_state == PLAYING:
            # Oyuncu hareket edebilir
            keys = pygame.key.get_pressed()
            self.player.update()
            
            # Altının parıltı efektini güncelle
            if self.player.current_room == "oda3" and self.altin_visible:
                # Buradan update_altin_sparkle metodu kaldırıldı çünkü bu metod tanımlanmamış
                
                # Oyuncu altına yeterince yakınsa ve diyalog gösterilmemişse otomatik olarak diyalog göster
                player_x, player_y = self.player.x, self.player.y
                altin_x, altin_y = self.altin_pos
                
                # Oyuncu ve altın arasındaki mesafeyi hesapla
                distance = ((player_x - altin_x) ** 2 + (player_y - altin_y) ** 2) ** 0.5
                
                # Eğer mesafe belirli bir eşiğin altındaysa ve diyalog aktif değilse
                if distance < 100 and not self.dialog_active:
                    # Doğrudan diyalog göster
                    self.show_dialog(
                        "Yerde bulduğun parayı gerçekten alacak mısın?",
                        ["Evet", "Hayır"],
                        self.altini_al
                    )
            
            # Saat ve tarih güncellemesi
            self.elapsed_time += dt
            if self.elapsed_time >= self.day_duration:
                self.next_day()
                self.elapsed_time = 0
                
        elif self.game_state == DIALOG:
            # Diyalog durumunda hareket yok, sadece seçimler
            pass
        
        # Arka plan resimlerini yükle
        self.load_background_images()
        
        # Pencere boyutunu kontrol et ve değiştiyse arkaplanları yeniden ölçeklendir
        current_size = pygame.display.get_surface().get_size()
        if current_size != self.last_window_size:
            self.resize_backgrounds(current_size)
            self.last_window_size = current_size
        
        # Altın paranın parlama efektini güncelle
        self.update_altin()
        
        # Oyuncunun çıkışlarla etkileşimini kontrol et
        self.check_exits()
        
        # Oyun durumuna göre farklı güncelleme işlemleri
        if self.game_state == PLAYING:
            dx, dy = 0, 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
                
            self.player.move(dx, dy, ROOMS)
            self.player.update() # Oyuncu konumunu ve animasyonunu güncelle
            
            # Çıkışları kontrol et
            current_room = ROOMS[self.player.current_room]
            for exit_name, exit_pos in current_room["exits"].items():
                if self.player.is_near_exit(exit_pos):
                    # Borsa ve diğer odalara geçiş
                    if exit_name == "borsa":
                        self.game_state = STOCK_MARKET
                    elif exit_name == "kabin":
                         self.player.current_room = "kabin"
                    elif exit_name == "çalışma_alanı":
                        self.player.current_room = "çalışma_alanı"
                    # Diğer odalar eklenebilir...
        
        # STOCK_MARKET durumu için ESC kontrolü kaldırıldı
        # sadece event-based handle_key() kullanılacak
    
    def check_exits(self):
        """Oyuncunun çıkışlara yakın olup olmadığını kontrol eder"""
        if self.game_state != PLAYING:
            return
            
        # Mevcut oda bilgilerini al
        current_room = self.player.current_room
        if current_room in ROOMS and "exits" in ROOMS[current_room]:
            exits = ROOMS[current_room]["exits"]
            
            # Her çıkışı kontrol et
            for exit_name, exit_pos in exits.items():
                if self.player.is_near_exit(exit_pos):
                    # Borsa ve diğer odalara geçiş
                    if exit_name == "borsa":
                        self.game_state = STOCK_MARKET
                    elif exit_name == "kabin":
                         self.player.current_room = "kabin"
                    elif exit_name == "çalışma_alanı":
                        self.player.current_room = "çalışma_alanı"
                    elif exit_name == "güverte" and current_room == "çalışma_alanı":
                        # Çalışma alanından güverteye dönüş
                        self.player.current_room = "güverte"
                        # Güverte merkezine ışınla
                        guverte_bounds = ROOMS["güverte"]["bounds"]
                        self.player.x = (guverte_bounds[0] + guverte_bounds[2]) // 2
                        self.player.y = (guverte_bounds[1] + guverte_bounds[3]) // 2 - 50  # Biraz daha yukarıda
                        print(f"Güverteye dönüldü, konum: ({self.player.x}, {self.player.y})")
                    # Diğer odalar eklenebilir...
    
    def load_background_images(self):
        """Farklı odalar için arka plan görsellerini yükler"""
        # Oda ve ilgili dosya ismi eşleştirmesi
        background_files = {
            "güverte": "deck_background.png",  # Deniz arka planı
            "kabin": "cabin_background.png",
            "çalışma_alanı": "study_background.png",
            "borsa": "lounge_background.png"
        }
        
        # Güverte üst görselini ayrıca yükle
        self.ship_deck = None
        ship_deck_path = os.path.join('assets', 'images', 'gemiguverte.png')
        if os.path.exists(ship_deck_path):
            try:
                self.ship_deck = pygame.image.load(ship_deck_path).convert_alpha()
                self.ship_deck = pygame.transform.scale(self.ship_deck, (WIDTH, HEIGHT))
                print(f"Gemi güvertesi görseli yüklendi: {ship_deck_path}")
            except Exception as e:
                print(f"Gemi güvertesi yüklenirken hata: {e}")
        else:
            print(f"Gemi güvertesi bulunamadı: {ship_deck_path}")
        
        # Altın para görselini yükle
        altin_path = os.path.join('assets', 'images', 'altin.png')
        if os.path.exists(altin_path):
            try:
                self.altin_image = pygame.image.load(altin_path).convert_alpha()
                # Boyutu ayarla (orijinal boyutunun iki katı daha küçük)
                altin_width = self.altin_image.get_width() // 2
                altin_height = self.altin_image.get_height() // 2
                self.altin_image = pygame.transform.scale(self.altin_image, (altin_width, altin_height))
                print(f"Altın para görseli yüklendi: {altin_path}")
            except Exception as e:
                print(f"Altın para görseli yüklenirken hata: {e}")
        else:
            print(f"Altın para görseli bulunamadı: {altin_path}")
        
        # Çanta görselini yükle
        canta_path = os.path.join('assets', 'images', 'canta.png')
        if os.path.exists(canta_path):
            try:
                self.canta_image = pygame.image.load(canta_path).convert_alpha()
                # Boyutu ayarla
                canta_width = 80
                canta_height = 80
                self.canta_image = pygame.transform.scale(self.canta_image, (canta_width, canta_height))
                print(f"Çanta görseli yüklendi: {canta_path}")
            except Exception as e:
                print(f"Çanta görseli yüklenirken hata: {e}")
        else:
            print(f"Çanta görseli bulunamadı: {canta_path}")
        
        # Her oda için
        for room, filename in background_files.items():
            # Eğer arka plan yüklenmemişse
            if self.backgrounds[room] is None:
                try:
                    background_path = os.path.join('assets', 'images', filename)
                    if os.path.exists(background_path):
                        self.backgrounds[room] = pygame.image.load(background_path).convert_alpha()
                        self.backgrounds[room] = pygame.transform.scale(self.backgrounds[room], (WIDTH, HEIGHT))
                        print(f"{room} için arka plan yüklendi: {background_path}")
                    else:
                        print(f"{room} için arka plan bulunamadı: {background_path}")
                except Exception as e:
                    print(f"{room} için arka plan yüklenirken hata: {e}")
    
    def resize_backgrounds(self, new_size):
        """Arka plan görsellerini yeni pencere boyutuna ölçeklendirir"""
        for room, bg in self.backgrounds.items():
            if bg is not None:
                try:
                    self.backgrounds[room] = pygame.transform.scale(bg, new_size)
                    print(f"{room} arka planı yeniden boyutlandırıldı: {new_size}")
                except Exception as e:
                    print(f"{room} arka planı yeniden boyutlandırılırken hata: {e}")
        
        # Gemi güvertesini de yeniden boyutlandır
        if self.ship_deck is not None:
            try:
                self.ship_deck = pygame.transform.scale(self.ship_deck, new_size)
                print(f"Gemi güvertesi yeniden boyutlandırıldı: {new_size}")
            except Exception as e:
                print(f"Gemi güvertesi yeniden boyutlandırılırken hata: {e}")
    
    def next_day(self):
        """Sonraki güne geçme"""
        # current_date ve end_date string olarak tanımlanmış, datetime objesi değil
        # Önce current_date'i datetime objesi olarak parse et
        try:
            date_obj = datetime.strptime(self.current_date, "%B %d, %Y")
            # Bir gün ekle
            next_date = date_obj + timedelta(days=1)
            # Aynı formatta string'e çevir
            self.current_date = next_date.strftime("%B %d, %Y")
            print(f"Yeni gün: {self.current_date}")
            
            # Hisse fiyatlarını güncelle
            for stock_name, stock_info in self.stocks.items():
                # Stock sınıfı yoksa manuel güncelleme yap
                price = stock_info["price"]
                volatility = stock_info["volatility"]
                trend = stock_info["trend"]
                
                # Fiyat değişimi hesapla
                change_percent = trend + (random.random() - 0.5) * volatility * 2  # -volatility ile +volatility arasında
                new_price = price * (1 + change_percent / 100)
                
                # Fiyatı güncelle
                self.stocks[stock_name]["price"] = max(1, new_price)  # En düşük 1$
                # Geçmiş fiyatları güncelle
                self.stocks[stock_name]["history"].append(self.stocks[stock_name]["price"])
                
            # Oyuncuyu yeni güne hazırla
            self.player.worked_today = False
            
            # Gün sonu kontrolü
            end_date_obj = datetime.strptime(self.end_date, "%B %d, %Y")
            if next_date >= end_date_obj:
                self.game_over()
        except Exception as e:
            print(f"Tarih güncelleme hatası: {e}")
            # Hata durumunda basit bir gün sayacı kullan
            self.day_count += 1
            if self.day_count >= 5:  # 5 gün sonra oyun bitsin
                self.game_over()
            
    def game_over(self):
        """Oyun sonu"""
        self.game_state = GAME_OVER
        # Oyun sonu puanlaması
        total_assets = self.player.cash
        for stock_name, stock_info in self.player.stocks.items():
            total_assets += stock_info["amount"] * self.stocks[stock_name].price
            
    def draw(self, screen):
        """Oyunu ekrana çizer"""
        # Ekranı temizle
        screen.fill(BLACK)
        
        if self.game_state == MAIN_MENU:
            self.draw_main_menu(screen)
        elif self.game_state == PLAYING:
            self.draw_playing(screen)
        elif self.game_state == STOCK_MARKET:
            self.draw_stock_market(screen)
        elif self.game_state == INVENTORY:
            self.draw_inventory(screen)
        elif self.game_state == DIALOG:
            # Önce oyun ekranını çiz
            self.draw_playing(screen)
            # Sonra diyalog kutusunu çiz
            self.draw_dialog(screen)
        elif self.game_state == GAME_OVER:
            self.draw_game_over(screen)
            
    def draw_main_menu(self, screen):
        """Ana menüyü çizer"""
        screen.fill(DARK_BLUE)
        
        # Başlık
        title = FONT_LARGE.render("TİTANİKTE ZİRVEYE", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        
        # Oyun başlama butonu
        pygame.draw.rect(screen, LIGHT_BLUE, (WIDTH//2 - 100, HEIGHT//2, 200, 50))
        start_text = FONT_MEDIUM.render("OYUNA BAŞLA", True, WHITE)
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 + 10))
        
        # Çıkış butonu
        pygame.draw.rect(screen, LIGHT_BLUE, (WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50))
        exit_text = FONT_MEDIUM.render("ÇIKIŞ", True, WHITE)
        screen.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, HEIGHT//2 + 90))
        
    def draw_playing(self, screen):
        """Oyun ekranını çizer"""
        # Ekranı temizle
        screen.fill(LIGHT_BLUE)
        
        # Oyuncunun mevcut odası
        current_room = self.player.current_room
        
        # Oda için arka plan görselini çiz
        if current_room in self.backgrounds and self.backgrounds[current_room] is not None:
            screen.blit(self.backgrounds[current_room], (0, 0))
            
            # Eğer güvertedeyse ve gemi görseli yüklenmişse, üzerine gemi güvertesini çiz
            if current_room == "güverte" and self.ship_deck is not None:
                screen.blit(self.ship_deck, (0, 0))
        else:
            # Arka plan yüklenmediyse basit arka planı çiz
            if current_room == "güverte":
                pygame.draw.rect(screen, BLUE, (0, HEIGHT // 1.5, WIDTH, HEIGHT // 3))  # Deniz
                pygame.draw.rect(screen, BROWN, (0, HEIGHT // 1.5 - 20, WIDTH, 20))  # Güverte kenarı
            elif current_room == "kabin":
                screen.fill((139, 69, 19))  # Kahverengi arka plan
            elif current_room == "çalışma_alanı":
                screen.fill((72, 61, 139))  # Mor-kahverengi arka plan
            else:
                screen.fill(LIGHT_BLUE)  # Varsayılan arka plan
        
        # Baca ve duman (sadece güvertede ise)
        if current_room == "güverte":
            # Eğer güverte arka plan görseli yoksa baca çiz
            if self.ship_deck is None and self.backgrounds["güverte"] is None:
                # Baca gövdesi
                pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 25, 70, 50, 100))
                pygame.draw.rect(screen, RED, (WIDTH // 2 - 30, 60, 60, 20))  # Baca üstü
            
            # Duman parçacıklarını çiz
            for particle in self.smoke_particles:
                # Parçacığın yaşam süresine bağlı olarak alfa değerini hesapla
                alpha = min(255, int(particle['life'] * 1.5))
                
                # Duman rengi (gri - yaşam süresine bağlı olarak soluklaşır)
                smoke_color = (200, 200, 200, alpha)
                
                # Geçici bir yüzey oluştur
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                
                # Dairesel parçacık çiz
                pygame.draw.circle(
                    particle_surface, 
                    smoke_color, 
                    (particle['size'], particle['size']), 
                    particle['size']
                )
                
                # Yüzeyi ekrana çiz
                screen.blit(particle_surface, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))
            
            # Altın parayı çiz (eğer görünürse)
            if self.altin_visible and self.altin_image is not None:
                # Parlama efekti için orijinal görseli kopyala
                parlayan_altin = self.altin_image.copy()
                
                # Parlama değerini kullanarak rengini değiştir
                # 0-100 arası parlama değeri, 0-50 arası ekstra parlaklık
                parlaklık = self.altin_parlama // 2
                
                # Geçici yüzey oluştur
                parlama_surface = pygame.Surface((parlayan_altin.get_width() + 10, parlayan_altin.get_height() + 10), pygame.SRCALPHA)
                
                # Parlama halkası çiz
                pygame.draw.circle(
                    parlama_surface,
                    (255, 255, 200, parlaklık + 50),  # Sarımsı renk, değişken saydamlık
                    (parlama_surface.get_width() // 2, parlama_surface.get_height() // 2),
                    parlayan_altin.get_width() // 2 + 5
                )
                
                # Parlama yüzeyini çiz
                screen.blit(parlama_surface, (self.altin_pos[0] - 5, self.altin_pos[1] - 5))
                
                # Altın parayı çiz
                screen.blit(parlayan_altin, self.altin_pos)
                
                # Karakter ile altın arasındaki mesafeyi hesapla
                dx = self.player.x - self.altin_pos[0]
                dy = self.player.y - self.altin_pos[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                # AL butonunu çiz (sadece uzaktaysa)
                if distance >= 100:
                    al_button_rect = pygame.Rect(self.altin_pos[0], self.altin_pos[1] + self.altin_image.get_height() + 10, 50, 30)
                    pygame.draw.rect(screen, BUTTON_COLOR, al_button_rect)
                    al_text = FONT_SMALL.render("AL", True, BLACK)
                    screen.blit(al_text, (al_button_rect.centerx - al_text.get_width() // 2, 
                                          al_button_rect.centery - al_text.get_height() // 2))
        
        # Çanta simgesini çiz (eğer görünürse)
        if self.canta_visible and self.canta_image is not None:
            screen.blit(self.canta_image, self.canta_position)
            
            # Envanterdeki öğeleri çanta üzerinde göster
            if "altın" in self.player.inventory:
                # Altın simgesi çiz
                if self.altin_image:
                    # Daha küçük boyutta göster
                    item_size = 30
                    altin_item = pygame.transform.scale(self.altin_image, (item_size, item_size))
                    screen.blit(altin_item, (self.canta_position[0] + 10, self.canta_position[1] - item_size - 5))
        
        # Çıkışları çiz
        self.draw_exits(screen)
        
        # Odaya özel bilgileri çiz
        self.draw_room_details(screen, current_room)
        
        # Oyuncuyu çiz
        self.player.draw(screen)
        
        # Üst bilgi çubuğunu çiz
        self.draw_info_bar(screen)
        
        # Diyalog kutusu (eğer aktifse)
        if self.dialog_active:
            self.draw_dialog_box(screen)
        
    def draw_stock_market(self, screen):
        """Borsa ekranını çizer"""
        screen.fill((50, 30, 20))  # Borsa salonu rengi
        
        # Başlık
        title = FONT_LARGE.render("BORSA SALONU", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        # Tarih ve para bilgisi
        date_text = FONT_MEDIUM.render(f"Tarih: {self.current_date.strftime('%d %B %Y')}", True, WHITE)
        screen.blit(date_text, (WIDTH - 300, 30))
        
        money_text = FONT_MEDIUM.render(f"Para: ${self.player.cash:.2f}", True, GREEN)
        screen.blit(money_text, (WIDTH - 300, 60))
        
        # Hisse senetleri listesi
        y_pos = 120
        for i, (stock_name, stock) in enumerate(self.stocks.items()):
            bg_color = LIGHT_BLUE if self.selected_stock == stock_name else (40, 40, 60)
            pygame.draw.rect(screen, bg_color, (50, y_pos, WIDTH - 100, 50))
            
            # Hisse adı
            stock_text = FONT_MEDIUM.render(stock_name, True, WHITE)
            screen.blit(stock_text, (70, y_pos + 15))
            
            # Hisse fiyatı
            price_text = FONT_MEDIUM.render(f"${stock.price:.2f}", True, WHITE)
            screen.blit(price_text, (300, y_pos + 15))
            
            # Fiyat değişimi (son güne göre)
            if len(stock.history) > 1:
                change = stock.price - stock.history[-2]
                change_percent = (change / stock.history[-2]) * 100
                change_color = GREEN if change >= 0 else RED
                change_text = FONT_MEDIUM.render(f"{change:+.2f} ({change_percent:+.2f}%)", True, change_color)
                screen.blit(change_text, (450, y_pos + 15))
            
            # Sahip olunan hisse miktarı
            if stock_name in self.player.stocks:
                owned = self.player.stocks[stock_name]["amount"]
                owned_text = FONT_MEDIUM.render(f"Sahip: {owned}", True, GOLD)
                screen.blit(owned_text, (650, y_pos + 15))
            
            y_pos += 70
        
        # Seçili hisse için alım-satım paneli
        if self.selected_stock:
            pygame.draw.rect(screen, (60, 60, 80), (50, HEIGHT - 200, WIDTH - 100, 150))
            
            # Hisse adı ve fiyat
            selected = self.stocks[self.selected_stock]
            header_text = FONT_MEDIUM.render(f"{self.selected_stock} - ${selected.price:.2f}", True, WHITE)
            screen.blit(header_text, (70, HEIGHT - 180))
            
            # Miktar seçimi
            amount_text = FONT_MEDIUM.render(f"Miktar: {self.stock_amount}", True, WHITE)
            screen.blit(amount_text, (70, HEIGHT - 140))
            
            # - + butonları
            pygame.draw.rect(screen, RED, (200, HEIGHT - 145, 30, 30))
            screen.blit(FONT_MEDIUM.render("-", True, WHITE), (210, HEIGHT - 143))
            
            pygame.draw.rect(screen, GREEN, (240, HEIGHT - 145, 30, 30))
            screen.blit(FONT_MEDIUM.render("+", True, WHITE), (250, HEIGHT - 143))
            
            # Toplam fiyat
            total_text = FONT_MEDIUM.render(f"Toplam: ${selected.price * self.stock_amount:.2f}", True, WHITE)
            screen.blit(total_text, (300, HEIGHT - 140))
            
            # Al-Sat butonları
            pygame.draw.rect(screen, GREEN, (WIDTH - 300, HEIGHT - 150, 100, 40))
            screen.blit(FONT_MEDIUM.render("AL", True, WHITE), (WIDTH - 270, HEIGHT - 140))
            
            pygame.draw.rect(screen, RED, (WIDTH - 180, HEIGHT - 150, 100, 40))
            screen.blit(FONT_MEDIUM.render("SAT", True, WHITE), (WIDTH - 150, HEIGHT - 140))
            
            # Grafik
            self.draw_stock_chart(screen, selected, (70, HEIGHT - 100, WIDTH - 140, 40))
        
        # Geri butonu
        pygame.draw.rect(screen, DARK_BLUE, (WIDTH//2 - 50, HEIGHT - 40, 100, 30))
        back_text = FONT_SMALL.render("GERİ", True, WHITE)
        screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT - 35))
        
    def draw_stock_chart(self, screen, stock, rect):
        """Hisse senedi grafiği çizer"""
        x, y, width, height = rect
        
        # Çerçeve çiz
        pygame.draw.rect(screen, WHITE, rect, 1)
        
        # Veri yoksa çıkış yap
        if len(stock.history) < 2:
            return
            
        # Min ve max değerler
        min_price = min(stock.history)
        max_price = max(stock.history)
        price_range = max_price - min_price or 1  # 0'a bölmeyi önle
        
        # Grafik çiz
        points = []
        for i, price in enumerate(stock.history):
            point_x = x + (i / (len(stock.history) - 1)) * width
            point_y = y + height - ((price - min_price) / price_range) * height
            points.append((point_x, point_y))
            
        if len(points) > 1:
            pygame.draw.lines(screen, GREEN if stock.history[-1] >= stock.history[0] else RED, False, points, 2)
        
    def draw_inventory(self, screen):
        """Envanter ekranını çizer"""
        # Envanter ekranı - daha sonra eklenecek
        pass
        
    def draw_dialog(self, screen):
        """Diyalog ekranını çizer"""
        if self.dialog_active:
            self.draw_dialog_box(screen)
        
    def draw_game_over(self, screen):
        """Oyun sonu ekranını çizer"""
        screen.fill(DARK_BLUE)
        
        # Başlık
        title = FONT_LARGE.render("OYUN BİTTİ", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        
        # Toplam varlık
        total_assets = self.player.cash
        for stock_name, stock_info in self.player.stocks.items():
            total_assets += stock_info["amount"] * self.stocks[stock_name].price
            
        assets_text = FONT_MEDIUM.render(f"Toplam Varlık: ${total_assets:.2f}", True, WHITE)
        screen.blit(assets_text, (WIDTH//2 - assets_text.get_width()//2, HEIGHT//3))
        
        # Değerlendirme
        if total_assets < 500:
            rating = "Şanssız Temizlikçi"
        elif total_assets < 1000:
            rating = "Küçük Yatırımcı"
        elif total_assets < 5000:
            rating = "Orta Sınıf İşadamı"
        elif total_assets < 10000:
            rating = "Başarılı Tüccar"
        else:
            rating = "Titanik'in Kralı"
            
        rating_text = FONT_MEDIUM.render(f"Statü: {rating}", True, GOLD)
        screen.blit(rating_text, (WIDTH//2 - rating_text.get_width()//2, HEIGHT//2))
        
        # Yeniden başla butonu
        pygame.draw.rect(screen, LIGHT_BLUE, (WIDTH//2 - 100, HEIGHT * 2//3, 200, 50))
        restart_text = FONT_MEDIUM.render("YENİDEN BAŞLA", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT * 2//3 + 10))
        
    def draw_ui(self, screen):
        """UI öğelerini çizer"""
        # Para ve tarih bilgisi
        pygame.draw.rect(screen, (0, 0, 0, 180), (0, 0, WIDTH, 40))
        
        date_text = FONT_MEDIUM.render(f"Tarih: {self.current_date.strftime('%d %B %Y')}", True, WHITE)
        screen.blit(date_text, (20, 10))
        
        money_text = FONT_MEDIUM.render(f"Para: ${self.player.cash:.2f}", True, GREEN)
        screen.blit(money_text, (300, 10))
        
        job_text = FONT_MEDIUM.render(f"İş: {self.player.job}", True, WHITE)
        screen.blit(job_text, (550, 10))
        
        # Oda adı
        room_name = ROOMS[self.player.current_room]["name"]
        room_text = FONT_MEDIUM.render(room_name, True, GOLD)
        screen.blit(room_text, (WIDTH - 200, 10))
        
        # Tuş bilgisi
        key_text = FONT_SMALL.render("ESC: Menü   I: Envanter   N: Sonraki Gün", True, WHITE)
        screen.blit(key_text, (20, HEIGHT - 30))
        
    def exit_stock_market(self):
        print("exit_stock_market fonksiyonu çağrıldı")
        # Tam resetleme yapalım
        self.selected_stock = None  # Seçili hisseyi temizle
        self.stock_amount = 1  # Miktarı sıfırla
        self.game_state = PLAYING  # Oyun durumunu güncelle
        self.player.current_room = "güverte"  # Odayı güncelle
        
        # Oyuncuyu güverte merkezine ışınla
        guverte_bounds = ROOMS["güverte"]["bounds"]
        self.player.x = (guverte_bounds[0] + guverte_bounds[2]) // 2
        self.player.y = (guverte_bounds[1] + guverte_bounds[3]) // 2 - 50  # Biraz daha yukarıda
        
        # Diğer borsa ile ilgili durumları sıfırla
        print(f"Oyun durumu güncellendi: {self.game_state}, Oda: {self.player.current_room}, Konum: ({self.player.x}, {self.player.y})")
        
    def draw_dialog_box(self, screen):
        """Diyalog kutusunu çizer"""
        # Dialog kutusu boyutu ve konumu
        dialog_width = WIDTH - 200
        dialog_height = 200
        dialog_x = 100
        dialog_y = HEIGHT // 2 - dialog_height // 2
        
        # Diyalog arka planı
        dialog_bg = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(screen, (50, 50, 70), dialog_bg)
        pygame.draw.rect(screen, GOLD, dialog_bg, 2)  # Altın renkli çerçeve
        
        # Diyalog metnini çiz
        self.draw_text(screen, self.dialog_text, WIDTH // 2, dialog_y + 50, WHITE)
        
        # Seçenekleri çiz (varsa)
        if self.dialog_options:
            option_y = dialog_y + 100
            option_width = 100
            option_height = 40
            
            self.dialog_buttons = []  # Temizle
            
            for i, option in enumerate(self.dialog_options):
                # Seçenekleri ortala ve aralarında boşluk bırak
                option_x = WIDTH // 2 - (len(self.dialog_options) * option_width + (len(self.dialog_options) - 1) * 20) // 2 + i * (option_width + 20)
                
                # Buton dikdörtgeni
                option_rect = pygame.Rect(option_x, option_y, option_width, option_height)
                pygame.draw.rect(screen, BUTTON_COLOR, option_rect)
                
                # Buton metni
                self.draw_text(screen, option, option_rect.centerx, option_rect.centery, BLACK)
                
                # Butonu kaydet
                self.dialog_buttons.append((option_rect, i))
                
    def handle_click(self, pos):
        """Fare tıklamalarını işler"""
        print(f"Fare tıklama: {pos}, Oyun durumu: {self.game_state}")
        
        # Diyalog aktifse, seçenek tıklamalarını kontrol et
        if self.dialog_active:
            if hasattr(self, 'dialog_buttons'):
                for button, choice_index in self.dialog_buttons:
                    if button.collidepoint(pos):
                        self.handle_dialog_choice(choice_index)
                        return
            else:
                # Seçenek yoksa, tıklamayla diyalogu kapat
                self.dialog_active = False
                return
        
        if self.game_state == MAIN_MENU:
            # Başla butonu
            if WIDTH//2 - 100 <= pos[0] <= WIDTH//2 + 100 and HEIGHT//2 <= pos[1] <= HEIGHT//2 + 50:
                self.game_state = PLAYING
                
            # Çıkış butonu
            elif WIDTH//2 - 100 <= pos[0] <= WIDTH//2 + 100 and HEIGHT//2 + 80 <= pos[1] <= HEIGHT//2 + 130:
                return "quit"
        
        elif self.game_state == PLAYING:
            # Altın para AL butonuna tıklama kontrolü
            if self.player.current_room == "güverte" and self.altin_visible and self.altin_image:
                # AL butonu sınırlarını hesapla
                al_button_rect = pygame.Rect(
                    self.altin_pos[0], 
                    self.altin_pos[1] + self.altin_image.get_height() + 10, 
                    50, 30
                )
                
                if al_button_rect.collidepoint(pos):
                    # Oyuncuyu altının yanına hareket ettir ve diyalog göster
                    self.player.target_x = self.altin_pos[0] - 50
                    self.player.target_y = self.altin_pos[1]
                    
                    # Diyalog göster
                    self.show_dialog(
                        "Yerde bulduğun parayı gerçekten alacak mısın?",
                        ["Evet", "Hayır"],
                        self.altini_al
                    )
                    return
                
        elif self.game_state == STOCK_MARKET:
            # Hisselere tıklama
            y_pos = 120
            for stock_name in self.stocks:
                if 50 <= pos[0] <= WIDTH - 50 and y_pos <= pos[1] <= y_pos + 50:
                    self.selected_stock = stock_name
                    self.stock_amount = 1
                y_pos += 70
                
            # Seçili hisse varsa, butonlara tıklama
            if self.selected_stock:
                # Miktar azaltma butonu
                if 200 <= pos[0] <= 230 and HEIGHT - 145 <= pos[1] <= HEIGHT - 115:
                    self.stock_amount = max(1, self.stock_amount - 1)
                
                # Miktar artırma butonu
                elif 240 <= pos[0] <= 270 and HEIGHT - 145 <= pos[1] <= HEIGHT - 115:
                    self.stock_amount += 1
                
                # Satın al butonu
                elif WIDTH - 300 <= pos[0] <= WIDTH - 200 and HEIGHT - 150 <= pos[1] <= HEIGHT - 110:
                    selected = self.stocks[self.selected_stock]
                    self.player.buy_stock(self.selected_stock, self.stock_amount, selected.price)
                
                # Sat butonu
                elif WIDTH - 180 <= pos[0] <= WIDTH - 80 and HEIGHT - 150 <= pos[1] <= HEIGHT - 110:
                    selected = self.stocks[self.selected_stock]
                    self.player.sell_stock(self.selected_stock, self.stock_amount, selected.price)
            
            # Geri butonu
            if WIDTH//2 - 50 <= pos[0] <= WIDTH//2 + 50 and HEIGHT - 40 <= pos[1] <= HEIGHT - 10:
                print("GERİ butonuna tıklandı!")
                self.exit_stock_market()
                print(f"Yeni oyun durumu: {self.game_state}, Oda: {self.player.current_room}")
                
        elif self.game_state == GAME_OVER:
            # Yeniden başla butonu
            if WIDTH//2 - 100 <= pos[0] <= WIDTH//2 + 100 and HEIGHT * 2//3 <= pos[1] <= HEIGHT * 2//3 + 50:
                self.__init__()  # Oyunu sıfırla
                self.game_state = MAIN_MENU

    def draw_exits(self, screen):
        """Mevcut odadaki çıkışları çizer"""
        current_room = self.player.current_room
        
        # Odadaki çıkışları al
        if current_room in ROOMS and "exits" in ROOMS[current_room]:
            exits = ROOMS[current_room]["exits"]
            self.current_exits = {}
            
            # Her çıkışı çiz
            for exit_name, exit_pos in exits.items():
                # Çıkış dikdörtgeni
                exit_rect = pygame.Rect(exit_pos[0] - 50, exit_pos[1] - 30, 100, 60)
                pygame.draw.rect(screen, DARK_BROWN, exit_rect)
                
                # Çıkış metni
                self.draw_text(screen, exit_name.capitalize(), exit_rect.centerx, exit_rect.centery, WHITE)
                
                # Çıkışı kaydet
                self.current_exits[exit_name] = exit_rect
    
    def draw_room_details(self, screen, current_room):
        """Odaya özel detayları çizer"""
        if current_room == "borsa":
            # Borsa odası için hisse senedi fiyatlarını göster
            self.draw_text(screen, "BORSA", WIDTH // 2, 30, WHITE)
            
            # Hisse senedi listesini göster
            y_offset = 80
            for i, (stock_name, stock_info) in enumerate(self.stocks.items()):
                price = stock_info["price"]
                change = stock_info["trend"]
                
                # Fiyat değişimi rengini belirle
                color = GREEN if change > 0 else RED if change < 0 else WHITE
                
                # Hisse bilgisini yaz
                self.draw_text(screen, f"{stock_name}: ${price:.2f} ({change:+.2f}%)", 
                              WIDTH // 2, y_offset + i * 40, color)
        
        elif current_room == "kabin":
            # Kabin bilgilerini göster
            self.draw_text(screen, "KABİN", WIDTH // 2, 30, WHITE)
            self.draw_text(screen, f"Mevcut Nakit: ${self.player.cash:.2f}", WIDTH // 2, 80, WHITE)
            self.draw_text(screen, f"Mevcut Gün: {self.current_date}/{self.end_date}", WIDTH // 2, 120, WHITE)
            
            # Sahip olunan hisseler
            self.draw_text(screen, "Hisseleriniz:", WIDTH // 2, 180, WHITE)
            y_pos = 220
            for stock_name, amount in self.player.stocks.items():
                if amount > 0:
                    price = self.stocks[stock_name]["price"]
                    value = amount * price
                    self.draw_text(screen, f"{stock_name}: {amount} adet (${value:.2f})", WIDTH // 2, y_pos, WHITE)
                    y_pos += 40
            
            # Uyku butonu (yeni güne geç)
            sleep_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 200, 200, 80)
            pygame.draw.rect(screen, BUTTON_COLOR, sleep_button)
            self.draw_text(screen, "Uyu (Sonraki Gün)", sleep_button.centerx, sleep_button.centery, BLACK)
            
            # Uyku butonunu kaydet
            self.sleep_button = sleep_button
        
        elif current_room == "calisma":
            # Çalışma alanı bilgilerini göster
            self.draw_text(screen, "ÇALIŞMA ALANI", WIDTH // 2, 30, WHITE)
            
            # Çalışma alanı
            work_area = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 75, 300, 150)
            pygame.draw.rect(screen, GRAY, work_area)
            
            if not self.player.worked_today:
                self.draw_text(screen, "Çalışmak için E tuşuna bas", 
                              work_area.centerx, work_area.centery, WHITE)
                self.draw_text(screen, "Günlük kazanç: $100", 
                              work_area.centerx, work_area.centery + 40, GREEN)
            else:
                self.draw_text(screen, "Bugün yeterince çalıştın!", 
                              work_area.centerx, work_area.centery, WHITE)
    
    def draw_text(self, screen, text, x, y, color):
        """Ekrana metin çizer"""
        if isinstance(text, str):  # Metin kontrolü
            font = FONT_MEDIUM  # Varsayılan font
            
            # Metin uzunluğuna göre font boyutunu ayarla
            if len(text) > 30:
                font = FONT_SMALL
            elif len(text) < 10:
                font = FONT_LARGE
                
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
        else:
            print(f"HATA: draw_text metni string değil: {text}")
    
    def draw_info_bar(self, screen):
        """Üst bilgi çubuğunu çizer"""
        # Üst bilgi çubuğu arka planı
        info_bar_rect = pygame.Rect(0, 0, WIDTH, 40)
        pygame.draw.rect(screen, DARK_BLUE, info_bar_rect)
        
        # Para bilgisi
        money_text = f"${self.player.cash:.2f}"
        self.draw_text(screen, money_text, 80, 20, WHITE)
        
        # Gün bilgisi
        date_text = f"Gün: {self.current_date}/{self.end_date}"
        self.draw_text(screen, date_text, WIDTH // 2, 20, WHITE)
        
        # Mevcut oda bilgisi
        room_text = f"Oda: {self.player.current_room.capitalize()}"
        self.draw_text(screen, room_text, WIDTH - 120, 20, WHITE)
        
        # Tam ekran/pencere modu için ipucu
        tips_text = "F11: Tam Ekran   ESC: Çıkış"
        self.draw_text(screen, tips_text, WIDTH // 2, HEIGHT - 20, WHITE)

    def show_dialog(self, text, options=None, callback=None):
        """Diyalog ekranını göster"""
        self.dialog_active = True
        self.dialog_text = text
        self.dialog_options = options if options else []
        self.dialog_callback = callback
        
    def handle_dialog_choice(self, choice_index):
        """Diyalog seçimini işle"""
        if self.dialog_callback:
            self.dialog_callback(choice_index)
        self.dialog_active = False
        
    def altini_al(self, choice_index):
        """Altın parayı alma seçimini işle"""
        if choice_index == 0:  # Evet seçildi
            self.altin_visible = False  # Parayı görünmez yap
            self.canta_visible = True   # Çantayı görünür yap
            self.player.inventory.append("altın")  # Envantere ekle
            
            # Veritabanına kaydet
            self.save_item_to_db("altın")
            
            self.show_dialog("Yerde bulduğun parayı aldın. Bu durum ileride senin için bir takım sorunlar ortaya çıkarabilir.")
        else:  # Hayır seçildi
            self.show_dialog("Bunu gerçekten almaman gerektiği için mi almadın yoksa birisi görür diye mi korktun?")
            
    def update_altin(self):
        """Altın paranın parlama efektini güncelle"""
        if self.altin_visible:
            # Parlama değerini güncelle (0-100 arasında)
            self.altin_parlama += self.parlama_yonu
            if self.altin_parlama >= 100:
                self.parlama_yonu = -1
            elif self.altin_parlama <= 0:
                self.parlama_yonu = 1

    def handle_key(self, key):
        """Tuş basışlarını işler"""
        print(f"Tuşa basıldı: {key}, Oyun durumu: {self.game_state}")
        
        if self.game_state == PLAYING:
            if key == pygame.K_ESCAPE:
                # ESC tuşuna basılınca her zaman güverteye dön
                if self.player.current_room != "güverte":
                    self.player.current_room = "güverte"
                    # Güverte üzerinde güvenli bir konuma ışınla
                    guverte_bounds = ROOMS["güverte"]["bounds"]
                    self.player.x = (guverte_bounds[0] + guverte_bounds[2]) // 2
                    self.player.y = (guverte_bounds[1] + guverte_bounds[3]) // 2 - 50  # Güverte üzerinde biraz daha yukarıda
                    print(f"ESC ile güverteye dönüldü, konum: ({self.player.x}, {self.player.y})")
                else:
                    # Zaten güvertedeyse ana menüye dön
                    self.game_state = MAIN_MENU
            elif key == pygame.K_i:
                self.game_state = INVENTORY
            elif key == pygame.K_n:
                self.next_day()
            elif key == pygame.K_e:
                # Çalışma alanında çalışma
                if self.player.current_room == "çalışma_alanı" and not self.player.worked_today:
                    self.player.work()
                    
        elif self.game_state == INVENTORY:
            if key == pygame.K_ESCAPE:
                self.game_state = PLAYING
                
        elif self.game_state == STOCK_MARKET:
            if key == pygame.K_ESCAPE:
                print("ESC tuşuna basıldı - borsa ekranından çıkılıyor")
                self.exit_stock_market()
                print(f"Yeni oyun durumu: {self.game_state}, Oda: {self.player.current_room}")
                
        elif self.game_state == MAIN_MENU:
            if key == pygame.K_RETURN:
                self.game_state = PLAYING

    def init_database(self):
        """MySQL veritabanı bağlantısını başlatır (titan veritabanı)"""
        try:
            import mysql.connector
            self.db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",  # Geliştirme ortamında boş şifre
                database="titan"
            )
            self.db_cursor = self.db_connection.cursor()
            
            # İtemler tablosunu oluştur (yoksa)
            self.db_cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_id INT NOT NULL,
                    item_name VARCHAR(100) NOT NULL,
                    acquired_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.db_connection.commit()
            print("Veritabanı bağlantısı başarılı")
            return True
        except ImportError:
            print("MySQL connector modülü bulunamadı!")
            return False
        except Exception as e:
            print(f"Veritabanı bağlantı hatası: {e}")
            return False
    
    def save_item_to_db(self, item_name):
        """Bir öğeyi veritabanına kaydeder"""
        if hasattr(self, 'db_cursor') and self.db_cursor:
            try:
                self.db_cursor.execute("""
                    INSERT INTO items (player_id, item_name)
                    VALUES (%s, %s)
                """, (1, item_name))  # player_id 1 olarak sabit
                self.db_connection.commit()
                print(f"{item_name} veritabanına kaydedildi")
                return True
            except Exception as e:
                print(f"Veritabanı kayıt hatası: {e}")
                return False
        return False