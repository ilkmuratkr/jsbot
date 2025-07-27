# JavaScript Tarama Botu

Bu bot, belirtilen domain listesindeki sitelerde JavaScript dosyalarının varlığını asenkron olarak tarar.

## Özellikler

- Asenkron HTTP HEAD istekleri ile hızlı tarama
- HTTP/HTTPS protokol desteği
- Content-Type doğrulama
- Klasör ve subdomain tarama desteği
- Modüler yapı
- Hata yönetimi ve yeniden deneme mekanizması
- İlerleme takibi ve loglama
- Kaldığı yerden devam edebilme
- Sonuçları CSV formatında kaydetme
- Anında sonuç kaydetme (RAM optimizasyonu)

## Gereksinimler

```
aiohttp>=3.8.0
```

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

1. `domains.txt` dosyasına taranacak domainleri ekleyin (her satıra bir domain)
2. `config.py` dosyasından ayarları yapılandırın
3. Botu çalıştırın:

```bash
python main.py
```

## Yapılandırma

`config.py` dosyasından şu ayarları değiştirebilirsiniz:

- `CONCURRENT_REQUESTS`: Eşzamanlı istek sayısı
- `TIMEOUT`: İstek zaman aşımı süresi (saniye)
- `RETRY_COUNT`: Başarısız istekler için yeniden deneme sayısı
- `JS_PATHS`: Taranacak JavaScript dosya yolları
- `FOLDERS`: Taranacak klasörler
- `SUBDOMAINS`: Taranacak subdomainler

## Örnek Çıktı

Sonuçlar `found_js.csv` dosyasına kaydedilir:

```
url,js_path
example.com,/wp-includes/js/jquery/jquery.min.js
example.com/blog,/wp-includes/js/jquery/jquery.js
blog.another-example.com,/wp-includes/js/jquery/jquery.min.js
```

## Modüller

- `main.py`: Ana program
- `requester.py`: Asenkron HTTP istekleri
- `file_handler.py`: Dosya işlemleri
- `utils.py`: Yardımcı fonksiyonlar
- `config.py`: Yapılandırma ayarları 