# JavaScript Tarama Botu

Bu bot, belirtilen domain listesindeki sitelerde JavaScript dosyalarının varlığını asenkron olarak tarar. Özellikle WordPress sitelerindeki JavaScript dosyalarını tespit etmek için tasarlanmıştır.

## 🌟 Özellikler

- ⚡ Asenkron HTTP HEAD istekleri ile hızlı tarama
- 🔄 HTTP/HTTPS protokol desteği
- ✅ Content-Type doğrulama
- 📁 Klasör ve subdomain tarama desteği
- 🏗️ Modüler yapı
- 🛡️ Hata yönetimi ve yeniden deneme mekanizması
- 📊 İlerleme takibi ve loglama
- 🔄 Kaldığı yerden devam edebilme
- 📄 Sonuçları CSV formatında kaydetme
- 💾 Anında sonuç kaydetme (RAM optimizasyonu)
- 🎯 3 kez bulunma limiti ile performans optimizasyonu

## 📋 Gereksinimler

- Python 3.7+
- aiohttp kütüphanesi

## 🚀 Kurulum

### GitHub'dan Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/ilkmuratkr/jsbot.git

# Proje dizinine gidin
cd jsbot

# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt
```

### Manuel Kurulum

```bash
# aiohttp kütüphanesini yükleyin
pip install aiohttp>=3.8.0
```

## 📝 Kullanım

### 1. Domain Listesi Hazırlama

`domains.txt` dosyasına taranacak domainleri ekleyin (her satıra bir domain):

```txt
example.com
another-example.com
test-site.org
```

### 2. Yapılandırma

`config.py` dosyasından ayarları yapılandırın:

```python
# Eşzamanlı istek sayısı (sunucu kaynaklarınıza göre ayarlayın)
CONCURRENT_REQUESTS = 200

# İstek zaman aşımı süresi (saniye)
TIMEOUT = 30

# Taranacak JavaScript dosya yolları
JS_PATHS = [
    "/wp-includes/js/jquery/jquery.js",
    "/wp-includes/js/wp-embed.min.js",
    "/wp-includes/js/jquery/jquery-migrate.min.js",
    "/wp-includes/js/jquery/jquery.min.js"
]

# Taranacak klasörler
FOLDERS = ["blog", "wp", "site", "news", ...]

# Taranacak subdomainler
SUBDOMAINS = ["blog", "dev", "test", ...]
```

### 3. Botu Çalıştırma

```bash
python main.py
```

## ⚙️ Yapılandırma Seçenekleri

`config.py` dosyasından şu ayarları değiştirebilirsiniz:

| Ayar | Açıklama | Varsayılan |
|------|----------|------------|
| `CONCURRENT_REQUESTS` | Eşzamanlı istek sayısı | 200 |
| `TIMEOUT` | İstek zaman aşımı süresi (saniye) | 30 |
| `RETRY_COUNT` | Başarısız istekler için yeniden deneme sayısı | 1 |
| `CHUNK_SIZE` | İşlenecek domain grubu büyüklüğü | 1000 |
| `JS_PATHS` | Taranacak JavaScript dosya yolları | WordPress JS dosyaları |
| `FOLDERS` | Taranacak klasörler | 27 farklı klasör |
| `SUBDOMAINS` | Taranacak subdomainler | 5 farklı subdomain |

## 📊 Çıktı Formatı

Sonuçlar `found_js.csv` dosyasına kaydedilir:

```csv
url,js_path
example.com,/wp-includes/js/jquery/jquery.min.js
example.com/blog,/wp-includes/js/jquery/jquery.js
blog.another-example.com,/wp-includes/js/wp-embed.min.js
```

## 🔄 Tarama Sırası

Bot şu sırayla tarama yapar:

1. **Kök Dizin:** `example.com/wp-includes/js/...`
2. **Klasörler:** `example.com/blog/wp-includes/js/...`
3. **Subdomainler:** `blog.example.com/wp-includes/js/...`

Her domain için maksimum 3 kez JavaScript bulunduktan sonra o domain taranmaz.

## 📁 Proje Yapısı

```
jsbot/
├── main.py              # Ana program
├── config.py            # Yapılandırma ayarları
├── requester.py         # Asenkron HTTP istekleri
├── file_handler.py      # Dosya işlemleri
├── utils.py             # Yardımcı fonksiyonlar
├── requirements.txt     # Gerekli kütüphaneler
├── README.md           # Bu dosya
├── .gitignore          # Git ignore dosyası
├── domains.txt         # Taranacak domainler (kullanıcı tarafından eklenir)
├── found_js.csv        # Bulunan sonuçlar (otomatik oluşturulur)
└── js_scanner.log      # Log dosyası (otomatik oluşturulur)
```

## 🛠️ Geliştirme

### Yeni JavaScript Yolları Ekleme

`config.py` dosyasındaki `JS_PATHS` listesine yeni yollar ekleyebilirsiniz:

```python
JS_PATHS = [
    "/wp-includes/js/jquery/jquery.js",
    "/wp-includes/js/wp-embed.min.js",
    "/wp-includes/js/jquery/jquery-migrate.min.js",
    "/wp-includes/js/jquery/jquery.min.js",
    "/wp-content/plugins/your-plugin/assets/script.js",  # Yeni yol
]
```

### Yeni Klasörler Ekleme

`config.py` dosyasındaki `FOLDERS` listesine yeni klasörler ekleyebilirsiniz:

```python
FOLDERS = [
    "blog", "site", "wp", "news", "wpress", "cms",
    "home", "main", "public", "html", "wp1", "wp2",
    "v1", "wp-site", "new", "test", "dev", "portal",
    "newsite", "wpbackup", "backup", "beta", "prod",
    "site1", "demo", "old", "wordpress",
    "your-custom-folder",  # Yeni klasör
]
```

## 📈 Performans İpuçları

- **Eşzamanlı İstek Sayısı:** Sunucu kaynaklarınıza göre ayarlayın (200-500 arası önerilir)
- **Chunk Boyutu:** Büyük domain listeleri için 1000-5000 arası önerilir
- **Zaman Aşımı:** Yavaş sunucular için 30-60 saniye ayarlayın
- **Bellek Kullanımı:** Anında kaydetme özelliği sayesinde RAM kullanımı optimize edilmiştir

## 🐛 Sorun Giderme

### Yaygın Hatalar

1. **ModuleNotFoundError: No module named 'aiohttp'**
   ```bash
   pip install aiohttp>=3.8.0
   ```

2. **Domain dosyası bulunamadı**
   - `domains.txt` dosyasının proje dizininde olduğundan emin olun

3. **Çok fazla bağlantı hatası**
   - `CONCURRENT_REQUESTS` değerini düşürün
   - `TIMEOUT` değerini artırın

### Log Dosyası

Hata ayıklama için `js_scanner.log` dosyasını kontrol edin:

```bash
tail -f js_scanner.log
```

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📞 İletişim

- GitHub: [@ilkmuratkr](https://github.com/ilkmuratkr)
- Repository: [https://github.com/ilkmuratkr/jsbot](https://github.com/ilkmuratkr/jsbot) 