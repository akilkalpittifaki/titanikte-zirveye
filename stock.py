import random

class Stock:
    """Hisse senedi sınıfı"""
    
    def __init__(self, name, price, volatility):
        self.name = name
        self.price = price
        self.volatility = volatility  # Fiyat oynaklığı (0.0 ile 1.0 arasında)
        self.history = [price]  # Fiyat geçmişi
        
    def update_price(self):
        """Hisse senedi fiyatını güncelleyen fonksiyon"""
        # Rastgele fiyat değişimi
        change_percent = random.uniform(-self.volatility, self.volatility)
        self.price *= (1 + change_percent)
        self.price = max(0.1, min(10000, self.price))  # Minimum ve maksimum fiyat sınırları
        self.price = round(self.price, 2)
        self.history.append(self.price)
        # Sadece son 30 günü tut
        if len(self.history) > 30:
            self.history.pop(0)