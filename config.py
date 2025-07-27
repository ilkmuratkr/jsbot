"""
Yapılandırma ayarları için config dosyası.
Bu dosya, JavaScript tarama botunun tüm ayarlarını içerir.
"""

# Genel ayarlar
CONCURRENT_REQUESTS = 50  # Eşzamanlı istek sayısı
TIMEOUT = 40  # Saniye cinsinden istek zaman aşımı
RETRY_COUNT = 1  # Yeniden deneme sayısı
CHUNK_SIZE = 5000  # İşlenecek domain grubu büyüklüğü

# Hedef dosya yolları
JS_PATHS = [
    "/wp-includes/js/jquery/jquery.js",
    "/wp-includes/js/jquery/jquery.min.js"
]

# Klasörler
FOLDERS = [
    "blog",
    "site",
    "wp",
    "news",
    "wpress",
    "cms",
    "home",
    "main",
    "public",
    "html",
    "wp1",
    "wp2",
    "v1",
    "wp-site",
    "new",
    "test",
    "dev",
    "portal", 
    "newsite", 
    "wpbackup", 
    "backup", 
    "beta", 
    "prod", 
    "site1", 
    "demo", 
    "old", 
    "wordpress"
]

# Subdomainler
SUBDOMAINS = [
    "blog",
    "test",
    "wp",
    "old",
    "dev"
]

# Dosya ayarları
OUTPUT_FILE = "found_js.csv"
DOMAIN_LIST_FILE = "domains.txt"

# Content-Type doğrulama için JavaScript türleri
JS_CONTENT_TYPES = [
    "javascript",
    "application/javascript",
    "text/javascript",
    "application/x-javascript"
]

# HTTP protokolleri (öncelik sırasına göre)
PROTOCOLS = ["https://", "http://"] 