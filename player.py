import pygame
import math
import random
import os
from constants import WHITE, GREEN, BLACK, GOLD, RED, BLUE

class Player:
    """Oyuncuyu temsil eden sınıf"""
    def __init__(self, x, y):
        """Oyuncu sınıfını başlatır"""
        self.x = x
        self.y = y
        self.width = 50  # Başlangıç genişliği
        self.height = 100  # Başlangıç yüksekliği
        self.color = (255, 0, 0)  # Kırmızı renk
        self.speed = 8  # Hareket hızı arttırıldı (5'ten 8'e)
        self.direction = "down"  # Başlangıç yönü
        self.cash = 1000  # Başlangıç parası
        self.stocks = {}  # Hisse senetleri
        self.current_room = "güverte"  # Başlangıç odası
        self.worked_today = False  # Bugün çalıştı mı?
        self.job = "İşsiz"  # Meslek
        self.inventory = []  # Envanter sistemi
        
        # Hedefe doğru yumuşak hareketi desteklemek için
        self.target_x = x
        self.target_y = y
        
        # Animasyon için sprite'ları yükle
        self.sprites = {}
        self.current_frame = 0
        self.animation_cooldown = 150  # ms cinsinden
        self.last_update = pygame.time.get_ticks()
        self.load_images()
        
    def load_images(self):
        """Karakter görselleri için PNG dosyalarını yükler."""
        print("load_images çağrıldı.") # Debug
        # Görseller için klasörü kontrol et
        images_dir = os.path.join("assets", "images")
        print(f"Görsel klasörü kontrol ediliyor: {images_dir}") # Debug
        if not os.path.exists(images_dir):
            print(f"UYARI: {images_dir} klasörü bulunamadı. Çizilen karakterler kullanılacak.")
            return
        else:
            print(f"{images_dir} klasörü bulundu.") # Debug
            
        # Her yön için sprite'ları yükle
        directions = ["down", "up", "left", "right"]
        frames_per_direction = 4  # Her yön için frame sayısı
        found_any_image = False # En az bir görsel bulundu mu?
        
        for direction in directions:
            self.sprites[direction] = []
            print(f"Yön için görseller yükleniyor: {direction}") # Debug
            
            # Her frame için görsel yükle
            for i in range(frames_per_direction):
                file_path = os.path.join(images_dir, f"player_{direction}_{i}.png")
                print(f"  Kontrol ediliyor: {file_path}") # Debug
                
                if os.path.exists(file_path):
                    print(f"    Bulundu: {file_path}") # Debug
                    try:
                        original_img = pygame.image.load(file_path).convert_alpha()
                        # Görseli %50 oranında küçült (eskisi %20 idi)
                        scale_factor = 1  # 0.2'den 0.5'e yükseltildi - daha iyi kalite için
                        new_width = int(original_img.get_width() * scale_factor)
                        new_height = int(original_img.get_height() * scale_factor)
                        scaled_img = pygame.transform.scale(original_img, (new_width, new_height))
                        
                        # Boyutları güncelle - daha doğru çarpışma kontrolü için
                        if i == 0:  # İlk frameden boyut bilgisini al
                            self.width = new_width
                            self.height = new_height
                            print(f"    Karakter boyutu güncellendi: {self.width}x{self.height}")
                        
                        self.sprites[direction].append(scaled_img)
                        found_any_image = True # Görsel bulundu işaretle
                        print(f"    Başarıyla yüklendi ve eklendi: {file_path}") # Debug
                    except pygame.error as e:
                        print(f"UYARI: {file_path} yüklenirken hata: {e}")
                    except Exception as e:
                        print(f"BEKLENMEDİK HATA: {file_path} işlenirken: {e}") # Genel hata yakalama
                else:
                    print(f"    Bulunamadı: {file_path}") # Debug
                    # Eğer bu frame için görsel yoksa, yön için hiç görsel ekleme
                    # ve döngüden çık - bu yön için çizilen karaktere geri dön
                    # ÖNEMLİ: Eğer sadece ilk frame (0) eksikse, diğerleri yüklenmez.
                    # Bu yön için hiç frame yüklenmemiş olacak.
                    print(f"    {direction} yönü için frame {i} bulunamadı. Bu yön için görsel yüklemesi durduruldu.") # Debug
                    break # Bu yönün kalan framelerini aramayı bırak
                    
            # Eğer bu yön için hiç görsel yüklenmediyse, sprites[direction] listesi boş kalacak
            if not self.sprites[direction]:
                print(f"UYARI: {direction} yönü için hiç görsel yüklenemedi.")
            else:
                print(f"'{direction}' yönü için {len(self.sprites[direction])} frame yüklendi.")
                    
        # Eğer hiç görsel yüklenmediyse genel bir uyarı ver
        if not found_any_image:
            print("UYARI: Hiçbir yöne ait karakter görseli yüklenemedi. Çizilen karakter kullanılacak.")

    def update(self):
        """Oyuncu durumunu günceller"""
        # Hedef konuma doğru yumuşak hareket
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        # Eğer hedef ile mevcut konum arasında fark varsa
        if abs(dx) > 0.1 or abs(dy) > 0.1:
            # Birim vektör üzerine hareket hızını uygula
            distance = math.sqrt(dx * dx + dy * dy)
            dx = dx / distance * min(self.speed, distance)
            dy = dy / distance * min(self.speed, distance)
            
            # Konumu güncelle
            self.x += dx
            self.y += dy
            
            # Yön belirleme
            if abs(dx) > abs(dy):
                if dx > 0:
                    self.direction = "right"
                else:
                    self.direction = "left"
            else:
                if dy > 0:
                    self.direction = "down"
                else:
                    self.direction = "up"
                    
            # Animasyon karesini güncelle
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update > self.animation_cooldown:
                self.current_frame = (self.current_frame + 1) % 4  # 4 kare arasında döngü
                self.last_update = current_time

    def move(self, dx, dy, rooms):
        """Oyuncuyu hareket ettiren fonksiyon - yumuşatılmış hareket ile"""
        # Hareket hedeflerini ayarla
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Oda sınırlarını kontrol et
        current_room = rooms[self.current_room]
        room_bounds = current_room["bounds"]
        
        # Debug bilgisi (optimize edildi)
        if dx != 0 or dy != 0:
            print(f"Hareket: ({self.x}, {self.y}) -> ({new_x}, {new_y})")
        
        # Geminin şeklini hesaba katan sınırlar (güverte için özel işlem)
        valid_x = True
        valid_y = True
        
        if current_room == "güverte":
            # Geminin merkezden uzaklığa göre daralan yapısını hesapla
            center_x = (room_bounds[0] + room_bounds[2]) / 2
            distance_from_center = abs(new_x - center_x)
            
            # Geminin kenarlarına yaklaştıkça (x ekseni) y ekseninde sınır yükselir
            # Geminin en geniş hali ortada, kenarlara doğru inceliyor
            max_distance = (room_bounds[2] - room_bounds[0]) / 2
            narrowing_factor = distance_from_center / max_distance  # 0 ile 1 arasında değer
            
            # Geminin şekline göre y ekseninde sınırı hesapla
            # Yüzde 50'lik bir daralma uyguluyoruz (ihtiyaca göre değiştirilebilir)
            ship_shape_y = room_bounds[1] + narrowing_factor * 350  # 350 daralma faktörü
            
            # Şimdi sınırları kontrol et
            if new_x < room_bounds[0]:
                valid_x = False
                print("Sol sınıra çarpıldı")
            elif new_x + self.width > room_bounds[2]:
                valid_x = False
                print("Sağ sınıra çarpıldı")
                
            if new_y < ship_shape_y:
                valid_y = False
                print(f"Geminin kenarına çarpıldı (Üst sınır: {ship_shape_y})")
            elif new_y + self.height > room_bounds[3]:
                valid_y = False
                print("Alt sınıra çarpıldı")
        else:
            # Diğer odalar için normal sınır kontrolü
            if new_x < room_bounds[0]:
                valid_x = False
                print("Sol sınıra çarpıldı")
            elif new_x + self.width > room_bounds[2]:
                valid_x = False
                print("Sağ sınıra çarpıldı")
                
            if new_y < room_bounds[1]:
                valid_y = False
                print("Üst sınıra çarpıldı")
            elif new_y + self.height > room_bounds[3]:
                valid_y = False
                print("Alt sınıra çarpıldı")
            
        # Geçerli hareketleri uygula
        if valid_x:
            self.target_x = new_x
        if valid_y:
            self.target_y = new_y
        
        # Yön değişikliği (hareket olmasa bile)
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        if dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

    def draw(self, screen):
        """Oyuncuyu çizen fonksiyon"""
        # Görseller yüklenmişse onları kullan
        sprite_available = False
        if self.direction in self.sprites and len(self.sprites[self.direction]) > 0:
            # Frame indeksinin geçerli olduğundan emin ol
            num_frames = len(self.sprites[self.direction])
            safe_frame_index = self.current_frame % num_frames # Döngüsel index
            if safe_frame_index < len(self.sprites[self.direction]): # Ekstra güvenlik kontrolü
                 sprite = self.sprites[self.direction][safe_frame_index]
                 screen.blit(sprite, (self.x, self.y))
                 sprite_available = True
            else:
                 print(f"HATA: Geçersiz frame index! Yön: {self.direction}, İndex: {self.current_frame}, Güvenli İndex: {safe_frame_index}, Frame Sayısı: {num_frames}")
        
        if not sprite_available:
            # Görsel yoksa veya yüklenememişse basit şekil çiz
            # print(f"Uygun sprite bulunamadı ({self.direction}, frame {self.current_frame}). Şekil çiziliyor.") # Çok fazla log üretebilir
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            # Yön göstergesi çiz
            if self.direction == "down":
                pygame.draw.polygon(screen, BLACK, [(self.x + self.width // 2, self.y + self.height),
                                                       (self.x + self.width // 4, self.y + self.height - 10),
                                                       (self.x + 3 * self.width // 4, self.y + self.height - 10)])
            elif self.direction == "up":
                pygame.draw.polygon(screen, BLACK, [(self.x + self.width // 2, self.y),
                                                       (self.x + self.width // 4, self.y + 10),
                                                       (self.x + 3 * self.width // 4, self.y + 10)])
            elif self.direction == "right":
                pygame.draw.polygon(screen, BLACK, [(self.x + self.width, self.y + self.height // 2),
                                                       (self.x + self.width - 10, self.y + self.height // 4),
                                                       (self.x + self.width - 10, self.y + 3 * self.height // 4)])
            elif self.direction == "left":
                pygame.draw.polygon(screen, BLACK, [(self.x, self.y + self.height // 2),
                                                       (self.x + 10, self.y + self.height // 4),
                                                       (self.x + 10, self.y + 3 * self.height // 4)])

    def is_near_exit(self, exit_pos):
        """
        Oyuncunun belirtilen çıkışa yakın olup olmadığını kontrol eder
        """
        # Oyuncunun merkezi
        player_center_x = self.x + self.width / 2
        player_center_y = self.y + self.height / 2
        
        # Çıkış ile oyuncu arasındaki mesafe
        distance = math.sqrt((player_center_x - exit_pos[0])**2 + (player_center_y - exit_pos[1])**2)
        
        # 50 piksel içindeyse yakın sayılır
        return distance < 50

    def add_stock(self, stock_name, amount, price_per_unit):
        """
        Oyuncunun hisse senedi portföyüne ekleme yapar
        """
        total_cost = amount * price_per_unit
        
        # Yeterli para var mı?
        if total_cost > self.cash:
            return False
        
        # Parayı azalt
        self.cash -= total_cost
        
        # Hisse senedini ekle
        if stock_name in self.stocks:
            # Mevcut hisseyi güncelle
            current_amount = self.stocks[stock_name]["amount"]
            current_value = self.stocks[stock_name]["amount"] * self.stocks[stock_name]["price"]
            
            new_amount = current_amount + amount
            new_value = current_value + total_cost
            new_price = new_value / new_amount
            
            self.stocks[stock_name] = {
                "amount": new_amount,
                "price": new_price
            }
        else:
            # Yeni hisse ekle
            self.stocks[stock_name] = {
                "amount": amount,
                "price": price_per_unit
            }
        
        return True
    
    def sell_stock(self, stock_name, amount, price_per_unit):
        """
        Oyuncunun hisse senedi portföyünden satış yapar
        """
        # Hisse var mı ve miktar yeterli mi?
        if (stock_name not in self.stocks or 
            self.stocks[stock_name]["amount"] < amount):
            return False
        
        # Satış değerini hesapla
        sell_value = amount * price_per_unit
        
        # Parayı artır
        self.cash += sell_value
        
        # Hisse miktarını güncelle
        self.stocks[stock_name]["amount"] -= amount
        
        # Eğer hisse kalmadıysa, portföyden çıkar
        if self.stocks[stock_name]["amount"] <= 0:
            del self.stocks[stock_name]
        
        return True

    def work(self):
        """Oyuncunun çalışmasını sağlar"""
        if not self.worked_today:
            earnings = random.randint(50, 200)  # Rastgele kazanç
            self.cash += earnings
            self.worked_today = True
            print(f"Çalıştın ve {earnings}$ kazandın!")
            return earnings
        return 0