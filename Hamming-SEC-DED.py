import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, 
    QMessageBox, QSpinBox, QGroupBox, QGridLayout, QFrame,
    QScrollArea, QSizePolicy, QListWidgetItem, QStatusBar, QShortcut
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QBrush, QKeySequence, QClipboard
import math
import time

class HammingSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.active_code = None
        self.error_positions = set()
        self.clipboard = QApplication.clipboard()
        self.init_ui()
        self.setup_shortcuts()
        self.setup_status_bar()
    
    def init_ui(self):
        self.setWindowTitle("Hamming SEC-DED Kodlayıcı - BLM230 Bilgisayar Mimarisi")
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Başlık
        title_label = QLabel("Hamming SEC-DED Kodlayıcı")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Veri giriş paneli
        self.setup_input_panel(main_layout)
        
        # Hamming kod görselleştirme paneli
        self.setup_visualization_panel(main_layout)
        
        # Hata enjeksiyon paneli
        self.setup_error_panel(main_layout)
        
        # Bellek paneli
        self.setup_memory_panel(main_layout)
        
        # Renk açıklama paneli
        self.setup_legend_panel(main_layout)
        
        # Stil ayarları
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                background-color: white;
            }
            QPushButton {
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QLineEdit, QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #3498db;
            }
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                color: black;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ebf3fd;
                color: black;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
    
    def setup_input_panel(self, main_layout):
        """Veri giriş paneli kurulumu"""
        input_group = QGroupBox("Binary Veri Girişi")
        input_layout = QHBoxLayout(input_group)
        
        input_layout.addWidget(QLabel("Binary Veri:"))
        
        self.data_input = QLineEdit("8, 16 veya 32 bitlik veri giriniz!")
        self.data_input.setPlaceholderText("8, 16 veya 32 bitlik binary veri")
        self.data_input.setFont(QFont("Courier New", 12))
        input_layout.addWidget(self.data_input)
        
        # Focus olayları
        self.data_input.focusInEvent = self.input_focus_in
        self.data_input.focusOutEvent = self.input_focus_out
        
        self.encode_btn = QPushButton("Kodla")
        self.encode_btn.clicked.connect(self.encode_data)
        # Yeşil-mavi renk - kodlama (ana işlem)
        self.encode_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                border: none;
                padding: 12px 25px;
                font-size: 15px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
            QPushButton:pressed {
                background-color: #117a65;
            }
        """)
        input_layout.addWidget(self.encode_btn)
        
        self.save_to_memory_btn = QPushButton("Belleğe Kaydet")
        self.save_to_memory_btn.clicked.connect(self.save_to_memory)
        # Koyu mavi renk - kaydetme
        self.save_to_memory_btn.setStyleSheet("""
            QPushButton {
                background-color: #2471a3;
                color: white;
                border: none;
                padding: 12px 20px;
                font-size: 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1f618d;
            }
            QPushButton:pressed {
                background-color: #1a5276;
            }
        """)
        input_layout.addWidget(self.save_to_memory_btn)
        
        main_layout.addWidget(input_group)
    
    def setup_visualization_panel(self, main_layout):
        """Hamming kod görselleştirme paneli kurulumu"""
        viz_group = QGroupBox("Hamming Kod Görselleştirme")
        viz_layout = QVBoxLayout(viz_group)
        
        # Scroll area for bits
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMinimumHeight(120)
        scroll_area.setMaximumHeight(150)
        
        self.bits_widget = QWidget()
        self.bits_layout = QHBoxLayout(self.bits_widget)
        self.bits_layout.setSpacing(5)
        scroll_area.setWidget(self.bits_widget)
        
        viz_layout.addWidget(scroll_area)
        main_layout.addWidget(viz_group)
    
    def setup_error_panel(self, main_layout):
        """Hata enjeksiyon paneli kurulumu"""
        error_group = QGroupBox("Hata İşlemleri")
        error_layout = QHBoxLayout(error_group)
        
        error_layout.addWidget(QLabel("Hata Pozisyonu:"))
        
        self.error_position_spin = QSpinBox()
        self.error_position_spin.setRange(1, 100)
        error_layout.addWidget(self.error_position_spin)
        
        self.add_error_btn = QPushButton("Hata Ekle")
        self.add_error_btn.clicked.connect(self.add_error)
        # Kırmızı renk - hata ekleme
        self.add_error_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        error_layout.addWidget(self.add_error_btn)
        
        self.correct_btn = QPushButton("Düzelt")
        self.correct_btn.clicked.connect(self.correct_errors)
        # Yeşil renk - düzeltme
        self.correct_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        error_layout.addWidget(self.correct_btn)
        
        main_layout.addWidget(error_group)
    
    def setup_memory_panel(self, main_layout):
        """Bellek paneli kurulumu"""
        memory_group = QGroupBox("Bellek")
        memory_layout = QVBoxLayout(memory_group)
        
        # Memory list
        self.memory_list = QListWidget()
        self.memory_list.setMaximumHeight(200)
        self.memory_list.itemDoubleClicked.connect(self.read_from_memory)
        memory_layout.addWidget(self.memory_list)
        
        # Memory buttons
        memory_btn_layout = QHBoxLayout()
        
        self.read_memory_btn = QPushButton("Bellekten Oku")
        self.read_memory_btn.clicked.connect(self.read_from_memory)
        # Mavi renk - okuma
        self.read_memory_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
                font-size: 13px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        memory_btn_layout.addWidget(self.read_memory_btn)
        
        self.delete_memory_btn = QPushButton("Bellekten Sil")
        self.delete_memory_btn.clicked.connect(self.delete_from_memory)
        # Turuncu renk - silme
        self.delete_memory_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 10px 15px;
                font-size: 13px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #ba4a00;
            }
        """)
        memory_btn_layout.addWidget(self.delete_memory_btn)
        
        self.clear_all_btn = QPushButton("Tümünü Temizle")
        self.clear_all_btn.clicked.connect(self.clear_all)
        # Mor renk - tümünü temizle
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border: none;
                padding: 10px 15px;
                font-size: 13px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7d3c98;
            }
            QPushButton:pressed {
                background-color: #6c3483;
            }
        """)
        memory_btn_layout.addWidget(self.clear_all_btn)
        
        memory_layout.addLayout(memory_btn_layout)
        main_layout.addWidget(memory_group)
    
    def setup_legend_panel(self, main_layout):
        """Renk açıklama paneli kurulumu"""
        legend_group = QGroupBox("Renk Açıklamaları")
        legend_layout = QHBoxLayout(legend_group)
        
        # Veri biti
        data_label = QLabel("Veri Biti")
        data_label.setStyleSheet("background-color: #2ecc71; color: white; border: 2px solid #27ae60; border-radius: 4px; padding: 5px; font-weight: bold;")
        legend_layout.addWidget(data_label)
        
        # Parity biti
        parity_label = QLabel("Parity Biti")
        parity_label.setStyleSheet("background-color: #3498db; color: white; border: 2px solid #2980b9; border-radius: 4px; padding: 5px; font-weight: bold;")
        legend_layout.addWidget(parity_label)
        
        # SEC-DED biti
        secded_label = QLabel("SEC-DED Biti")
        secded_label.setStyleSheet("background-color: #9b59b6; color: white; border: 2px solid #8e44ad; border-radius: 4px; padding: 5px; font-weight: bold;")
        legend_layout.addWidget(secded_label)
        
        # Tek hata
        single_error_label = QLabel("Tek Hata")
        single_error_label.setStyleSheet("background-color: #e74c3c; color: white; border: 2px solid #c0392b; border-radius: 4px; padding: 5px; font-weight: bold;")
        legend_layout.addWidget(single_error_label)
        
        # Çift hata
        double_error_label = QLabel("Çift Hata")
        double_error_label.setStyleSheet("background-color: #f39c12; color: white; border: 2px solid #e67e22; border-radius: 4px; padding: 5px; font-weight: bold;")
        legend_layout.addWidget(double_error_label)
        
        # Klavye kısayolları
        shortcuts_label = QLabel("Kısayollar: Ctrl+N: Temizle | Ctrl+C: Kopyala | Ctrl+V: Yapıştır | F5: Yenile | Del: Sil")
        shortcuts_label.setStyleSheet("color: #7f8c8d; font-size: 11px; font-style: italic;")
        shortcuts_label.setAlignment(Qt.AlignCenter)
        shortcuts_label.setWordWrap(True)
        
        legend_layout.addStretch()
        
        legend_layout_main = QVBoxLayout()
        legend_layout_main.addLayout(legend_layout)
        legend_layout_main.addWidget(shortcuts_label)
        
        legend_group.setLayout(legend_layout_main)
        main_layout.addWidget(legend_group)
    
    def setup_shortcuts(self):
        """Klavye kısayolları kurulumu"""
        # Ctrl+N - Yeni kodlama
        self.new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.new_shortcut.activated.connect(self.clear_all)
        
        # Ctrl+C - Kopyala (aktif kodu)
        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.copy_shortcut.activated.connect(self.copy_active_code)
        
        # Ctrl+V - Yapıştır
        self.paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        self.paste_shortcut.activated.connect(self.paste_code)
        
        # F5 - Yenile
        self.refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        self.refresh_shortcut.activated.connect(self.refresh_visualization)
        
        # Del - Seçili bellek kaydını sil
        self.delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        self.delete_shortcut.activated.connect(self.delete_from_memory)
    
    def setup_status_bar(self):
        """Status bar kurulumu"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hamming SEC-DED Simülatörü Hazır - Binary veri girin ve kodlayın")
    
    def input_focus_in(self, event):
        """Giriş alanına odaklanınca"""
        if self.data_input.text() == "8, 16 veya 32 bitlik veri giriniz!":
            self.data_input.setText("")
        super(QLineEdit, self.data_input).focusInEvent(event)
    
    def input_focus_out(self, event):
        """Giriş alanından çıkınca"""
        if self.data_input.text().strip() == "":
            self.data_input.setText("8, 16 veya 32 bitlik veri giriniz!")
        super(QLineEdit, self.data_input).focusOutEvent(event)
    
    def validate_input(self, data):
        """Giriş verisi kontrolü"""
        if data == "8, 16 veya 32 bitlik veri giriniz!":
            QMessageBox.warning(self, "Hatalı Girdi", "Veri girmediniz!")
            self.status_bar.showMessage("Hata: Veri girilmedi", 3000)
            return False
        
        # Boşlukları temizle
        data = data.replace(" ", "").replace("\t", "").replace("\n", "")
        
        if not data or not all(c in '01' for c in data):
            QMessageBox.warning(self, "Hatalı Girdi", "Sadece 0 ve 1 girilebilir!")
            self.status_bar.showMessage("Hata: Geçersiz karakter", 3000)
            return False
        
        if len(data) not in [8, 16, 32]:
            QMessageBox.warning(self, "Hatalı Uzunluk", f"Lütfen 8, 16 veya 32 bitlik veri giriniz! (Mevcut: {len(data)} bit)")
            self.status_bar.showMessage(f"Hata: Geçersiz uzunluk ({len(data)} bit)", 3000)
            return False
            
        self.status_bar.showMessage(f"Geçerli {len(data)} bitlik veri doğrulandı", 2000)
        return True
    
    def calculate_hamming_code(self, data):
        """Hamming SEC-DED kodu hesaplama"""
        k = len(data)  # Veri uzunluğu
        r = 0  # Parity bit sayısı
        
        # Gerekli parity bit sayısını bulma: 2^r >= k + r + 1
        while (1 << r) < k + r + 1:
            r += 1
        
        n = k + r  # Toplam bit sayısı (SEC-DED hariç)
        code = [0] * n
        
        # Veri bitlerini yerleştirme (2'nin kuvveti olmayan pozisyonlara)
        data_idx = 0
        for i in range(1, n + 1):
            if (i & (i - 1)) != 0:  # 2'nin kuvveti değilse
                code[i - 1] = int(data[data_idx])
                data_idx += 1
        
        # Parity bitlerini hesaplama
        for i in range(r):
            parity_pos = 1 << i  # 2^i
            parity = 0
            
            for j in range(1, n + 1):
                if (j & parity_pos) != 0 and j != parity_pos:
                    parity ^= code[j - 1]
            
            code[parity_pos - 1] = parity
        
        # SEC-DED için genel parity biti ekleme
        secded_code = code + [0]
        overall_parity = 0
        for bit in code:
            overall_parity ^= bit
        secded_code[-1] = overall_parity
        
        return secded_code
    
    def get_parity_positions(self, total_bits):
        """Parity bit pozisyonlarını belirleme"""
        parity_positions = set()
        
        # 2'nin kuvvetleri parity bitleri
        i = 1
        while i < total_bits:
            parity_positions.add(i - 1)  # 0-indexed
            i <<= 1
        
        # Son bit SEC-DED parity biti
        parity_positions.add(total_bits - 1)
        
        return parity_positions
    
    def extract_data_from_code(self, code):
        """Koddan orijinal veriyi çıkarma"""
        data = ""
        for i in range(1, len(code)):
            if (i & (i - 1)) != 0 and i != len(code):  # Veri biti
                data += str(code[i - 1])
        return data
    
    def update_bit_visualization(self, code):
        """Bit görselleştirmesini güncelleme"""
        # Eski widget'ları temizle
        for i in reversed(range(self.bits_layout.count())):
            self.bits_layout.itemAt(i).widget().setParent(None)
        
        if code is None:
            return
        
        parity_positions = self.get_parity_positions(len(code))
        
        for i, bit in enumerate(code):
            # Bit container
            bit_container = QWidget()
            bit_layout = QVBoxLayout(bit_container)
            bit_layout.setContentsMargins(2, 2, 2, 2)
            bit_layout.setSpacing(2)
            
            # Bit değeri
            bit_label = QLabel(str(bit))
            bit_label.setAlignment(Qt.AlignCenter)
            bit_label.setFont(QFont("Courier New", 16, QFont.Bold))
            bit_label.setFixedSize(40, 40)
            
            # Renk belirleme
            if i in self.error_positions:
                if len(self.error_positions) == 1:
                    bit_label.setStyleSheet("background-color: #e74c3c; color: white; border: 2px solid #c0392b; border-radius: 4px;")  # Kırmızı - tek hata
                else:
                    bit_label.setStyleSheet("background-color: #f39c12; color: white; border: 2px solid #e67e22; border-radius: 4px;")  # Sarı - çift hata
            elif i in parity_positions:
                if i == len(code) - 1:  # SEC-DED biti
                    bit_label.setStyleSheet("background-color: #9b59b6; color: white; border: 2px solid #8e44ad; border-radius: 4px;")
                else:  # Parity biti
                    bit_label.setStyleSheet("background-color: #3498db; color: white; border: 2px solid #2980b9; border-radius: 4px;")
            else:  # Veri biti
                bit_label.setStyleSheet("background-color: #2ecc71; color: white; border: 2px solid #27ae60; border-radius: 4px;")
            
            # Tooltip
            if i == len(code) - 1:
                bit_label.setToolTip("SEC-DED Parity (overall parity biti)")
            elif i in parity_positions:
                bit_label.setToolTip("Parity biti")
            else:
                bit_label.setToolTip("Veri biti")
            
            # Pozisyon numarası
            pos_label = QLabel(str(i + 1))
            pos_label.setAlignment(Qt.AlignCenter)
            pos_label.setFont(QFont("Arial", 10))
            pos_label.setFixedHeight(20)
            
            bit_layout.addWidget(bit_label)
            bit_layout.addWidget(pos_label)
            
            self.bits_layout.addWidget(bit_container)
        
        # Güncelleme
        self.bits_widget.update()
    
    def calculate_syndrome(self, code):
        """Sendrom hesaplama"""
        if not code or len(code) <= 1:
            return 0
        
        n = len(code) - 1  # SEC-DED biti hariç
        r = 0
        while (1 << r) < n + 1:
            r += 1
        
        syndrome = 0
        for i in range(r):
            parity_pos = 1 << i
            parity = 0
            
            for j in range(1, n + 1):
                if (j & parity_pos) != 0:
                    parity ^= code[j - 1]
            
            if parity != 0:
                syndrome += parity_pos
        
        return syndrome
    
    def encode_data(self):
        """Veriyi kodlama"""
        data = self.data_input.text().strip()
        
        # Boşlukları temizle
        clean_data = data.replace(" ", "").replace("\t", "").replace("\n", "")
        
        if not self.validate_input(clean_data):
            return
        
        try:
            hamming_code = self.calculate_hamming_code(clean_data)
            self.active_code = hamming_code[:]
            self.error_positions.clear()
            
            # Error position spinner range ayarlama
            self.error_position_spin.setRange(1, len(hamming_code))
            
            # Görselleştirme
            self.update_bit_visualization(hamming_code)
            
            # Giriş alanını temizle
            self.data_input.setText("8, 16 veya 32 bitlik veri giriniz!")
            
            # Status mesajı
            self.status_bar.showMessage(f"Kodlama başarılı! {len(clean_data)} bit veri → {len(hamming_code)} bit kod", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Kodlama Hatası", f"Kodlama sırasında hata oluştu: {str(e)}")
            self.status_bar.showMessage("Kodlama başarısız", 3000)
    
    def add_error(self):
        """Hata ekleme"""
        if self.active_code is None:
            QMessageBox.warning(self, "Uyarı", "Önce bir kod seçmelisiniz!")
            return
        
        pos = self.error_position_spin.value()
        if pos < 1 or pos > len(self.active_code):
            QMessageBox.warning(self, "Uyarı", f"Pozisyon 1 ile {len(self.active_code)} arasında olmalı!")
            return
        
        # Biti ters çevir
        self.active_code[pos - 1] = 1 - self.active_code[pos - 1]
        self.error_positions.add(pos - 1)
        
        # Görselleştirmeyi güncelle
        self.update_bit_visualization(self.active_code)
        
        # Status güncelle
        self.status_bar.showMessage(f"Pozisyon {pos}'da hata eklendi", 2000)
    
    def correct_errors(self):
        """Hataları düzeltme"""
        if self.active_code is None:
            QMessageBox.warning(self, "Uyarı", "Önce bir kod seçmelisiniz!")
            return
        
        syndrome = self.calculate_syndrome(self.active_code)
        
        # Overall parity hesaplama
        overall_parity = 0
        for bit in self.active_code:
            overall_parity ^= bit
        
        # Hata analizi
        if syndrome == 0 and overall_parity == 0:
            # Hata yok
            self.error_positions.clear()
            QMessageBox.information(self, "Bilgi", "Kodda hata bulunamadı!")
            self.status_bar.showMessage("Hata bulunamadı", 2000)
            
        elif syndrome == 0 and overall_parity == 1:
            # SEC-DED biti hatası veya çift hata
            QMessageBox.information(self, "Bilgi", "Sadece SEC-DED parity bitinde hata var veya çift hata (düzeltilemez)!")
            self.status_bar.showMessage("SEC-DED hata veya çift hata", 3000)
            
        elif syndrome > 0 and overall_parity == 1:
            # Tek bit hatası - düzeltilebilir
            error_pos = syndrome - 1
            if 0 <= error_pos < len(self.active_code):
                self.active_code[error_pos] = 1 - self.active_code[error_pos]
                self.error_positions.clear()
                
                # Bellek güncellemesi
                current_row = self.memory_list.currentRow()
                if current_row >= 0:
                    data = self.extract_data_from_code(self.active_code)
                    code_str = ''.join(map(str, self.active_code))
                    new_text = f"Veri: {data} | Kod: {code_str}"
                    self.memory_list.item(current_row).setText(new_text)
                
                QMessageBox.information(self, "Düzeltildi", 
                                      f"Hatalı bit {syndrome}. pozisyonda bulundu, düzeltildi!")
                self.status_bar.showMessage(f"Pozisyon {syndrome}'daki hata düzeltildi", 3000)
            
        else:
            # Çift hata
            QMessageBox.warning(self, "Uyarı", "Birden fazla hata (çift bit hatası, düzeltilemez) tespit edildi!")
            self.status_bar.showMessage("Çift hata tespit edildi - düzeltilemez", 3000)
        
        # Görselleştirmeyi güncelle
        self.update_bit_visualization(self.active_code)
    
    def save_to_memory(self):
        """Belleğe kaydetme"""
        if self.active_code is None:
            QMessageBox.warning(self, "Uyarı", "Önce bir kod üretmelisiniz!")
            return
        
        data = self.extract_data_from_code(self.active_code)
        code_str = ''.join(map(str, self.active_code))
        
        display_text = f"Veri: {data} | Kod: {code_str}"
        self.memory_list.addItem(display_text)
        
        # Belleğe kaydettikten sonra çalışma alanını temizle
        self.active_code = None
        self.error_positions.clear()
        
        # Görselleştirmeyi temizle
        for i in reversed(range(self.bits_layout.count())):
            self.bits_layout.itemAt(i).widget().setParent(None)
        
        # Input alanını temizle
        self.data_input.setText("8, 16 veya 32 bitlik veri giriniz!")
        
        self.status_bar.showMessage("Kod belleğe kaydedildi ve çalışma alanı temizlendi", 3000)
    
    def read_from_memory(self):
        """Bellekten okuma"""
        current_row = self.memory_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Bellekten bir kod seçmelisiniz!")
            return
        
        item_text = self.memory_list.item(current_row).text()
        
        # Kod kısmını çıkarma
        try:
            parts = item_text.split("| Kod: ")
            if len(parts) != 2:
                QMessageBox.warning(self, "Hata", "Kod formatı bozuk!")
                return
            
            code_str = parts[1].strip()
            code = [int(c) for c in code_str]
            
            # Hata kontrolü
            self.error_positions.clear()
            syndrome = self.calculate_syndrome(code)
            overall_parity = sum(code) % 2
            
            if syndrome > 0 and overall_parity == 1:
                # Tek hata
                self.error_positions.add(syndrome - 1)
            elif (syndrome > 0 and overall_parity == 0) or (syndrome == 0 and overall_parity == 1):
                # Çift hata - tüm bitleri sarıya boyama
                for i in range(len(code)):
                    self.error_positions.add(i)
                QMessageBox.warning(self, "Çift Hata", 
                                  "Çift hata tespit edildi! Hatalı bitlerin yeri belirlenemedi. Kod düzeltilemez.")
            
            self.active_code = code[:]
            self.error_position_spin.setRange(1, len(code))
            self.update_bit_visualization(code)
            self.status_bar.showMessage("Bellekten kod okundu", 2000)
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Kod okunamadı: {str(e)}")
            self.status_bar.showMessage("Kod okuma hatası", 3000)
    
    def delete_from_memory(self):
        """Bellekten silme"""
        current_row = self.memory_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Önce silmek istediğiniz kodu seçin!")
            return
        
        self.memory_list.takeItem(current_row)
        
        # Görselleştirmeyi temizle
        for i in reversed(range(self.bits_layout.count())):
            self.bits_layout.itemAt(i).widget().setParent(None)
        
        self.active_code = None
        self.error_positions.clear()
        self.status_bar.showMessage("Bellek kaydı silindi", 2000)
    
    def clear_all(self):
        """Tüm verileri temizle"""
        self.active_code = None
        self.error_positions.clear()
        self.data_input.setText("8, 16 veya 32 bitlik veri giriniz!")
        
        # Görselleştirmeyi temizle
        for i in reversed(range(self.bits_layout.count())):
            self.bits_layout.itemAt(i).widget().setParent(None)
        
        self.status_bar.showMessage("Tüm veriler temizlendi", 2000)
    
    def copy_active_code(self):
        """Aktif kodu panoya kopyala"""
        if self.active_code is None:
            QMessageBox.warning(self, "Uyarı", "Kopyalanacak kod yok!")
            return
        
        code_str = ''.join(map(str, self.active_code))
        self.clipboard.setText(code_str)
        self.status_bar.showMessage("Kod panoya kopyalandı", 2000)
    
    def paste_code(self):
        """Panodan kod yapıştır"""
        clipboard_text = self.clipboard.text().strip()
        
        if not clipboard_text:
            QMessageBox.warning(self, "Uyarı", "Pano boş!")
            return
        
        # Boşlukları temizle
        clipboard_text = clipboard_text.replace(" ", "").replace("\t", "").replace("\n", "")
        
        # Sadece 0 ve 1 kontrolü
        if not all(c in '01' for c in clipboard_text):
            QMessageBox.warning(self, "Hata", "Pano sadece 0 ve 1 karakterleri içermelidir!")
            return
        
        # Input alanına yapıştır
        self.data_input.setText(clipboard_text)
        self.data_input.setFocus()
        self.status_bar.showMessage("Kod input alanına yapıştırıldı", 2000)
    
    def refresh_visualization(self):
        """Görselleştirmeyi yenile"""
        if self.active_code is not None:
            self.update_bit_visualization(self.active_code)
            self.status_bar.showMessage("Görselleştirme yenilendi", 1000)
        else:
            self.status_bar.showMessage("Yenilenecek kod yok", 1000)

def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Uygulama bilgileri
    app.setApplicationName("Hamming SEC-DED Simulator")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("BLM230 Project")
    
    window = HammingSimulator()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 