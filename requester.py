"""
Asenkron HTTP istekleri modülü.
JavaScript dosyalarını taramak için asenkron HEAD isteklerini yönetir.
"""

import asyncio
import aiohttp
from typing import List, Tuple, Optional, Dict, Any
import time
from aiohttp.client_exceptions import (
    ClientConnectorError, ClientSSLError, ClientError,
    ServerTimeoutError, TooManyRedirects
)

import config
from utils import logger, is_javascript_content_type

class JSRequester:
    def __init__(self, timeout: int = config.TIMEOUT, retry_count: int = config.RETRY_COUNT):
        """
        JavaScript istek sınıfını başlatır.
        
        Args:
            timeout: İstek zaman aşımı süresi (saniye)
            retry_count: Başarısız istekler için yeniden deneme sayısı
        """
        self.timeout = timeout
        self.retry_count = retry_count
        self.session = None
    
    async def initialize(self):
        """Oturum başlatma işlemi"""
        if self.session is None or self.session.closed:
            # SSL doğrulama devre dışı bırakılabilir (gerekirse)
            conn = aiohttp.TCPConnector(
                limit=config.CONCURRENT_REQUESTS,
                ttl_dns_cache=300,
                ssl=False
            )
            self.session = aiohttp.ClientSession(connector=conn)
    
    async def close(self):
        """Oturumu kapatma işlemi"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def check_js_file(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Belirtilen URL'de JavaScript dosyasının varlığını kontrol eder.
        
        Args:
            url: Kontrol edilecek URL
            
        Returns:
            Tuple[bool, Optional[str]]: (başarılı mı, content type)
        """
        for attempt in range(self.retry_count + 1):
            try:
                await self.initialize()
                
                # HEAD isteği gönder, yönlendirmeleri takip etme
                async with self.session.head(
                    url, 
                    timeout=self.timeout,
                    allow_redirects=False,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; JSScanner/1.0)"}
                ) as response:
                    # Sadece 200 OK başarılı sayılır
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")
                        
                        # JavaScript içeriği doğrulama
                        if is_javascript_content_type(content_type):
                            return True, content_type
                    
                    return False, None
                    
            except ClientSSLError:
                # SSL hatalarında URL'yi HTTP protokolüne geçirip tekrar deneyeceğiz
                # Bu, otomatik olarak protokol döngüsü ile yapılacak
                logger.debug(f"SSL hatası: {url}")
                return False, None
                
            except (ClientConnectorError, ServerTimeoutError) as e:
                if attempt < self.retry_count:
                    wait_time = 1 * (attempt + 1)
                    logger.debug(f"Bağlantı hatası ({e.__class__.__name__}), {url} için {wait_time}s bekleyip tekrar deneniyor")
                    await asyncio.sleep(wait_time)
                else:
                    logger.debug(f"Bağlantı başarısız: {url} - {str(e)}")
                    return False, None
                    
            except (TooManyRedirects, asyncio.TimeoutError) as e:
                logger.debug(f"İstek hatası: {url} - {str(e)}")
                return False, None
                
            except Exception as e:
                logger.debug(f"Beklenmeyen hata: {url} - {str(e)}")
                return False, None
        
        return False, None

    async def scan_domain_for_js(self, domain: str, js_paths: List[str], 
                                location_info: Dict[str, Any]) -> Optional[Tuple[str, str, str]]:
        """
        Bir domain için JavaScript dosyalarını tarar.
        
        Args:
            domain: Taranacak domain
            js_paths: Kontrol edilecek JavaScript yolları
            location_info: Konum bilgisi (kök, klasör, subdomain)
            
        Returns:
            Optional[Tuple[str, str, str]]: Başarılıysa (domain, açıklama, js_yolu), değilse None
        """
        urls = []
        
        # URL'leri oluştur
        if location_info.get("use_subdomain", False):
            from utils import build_urls
            urls = build_urls(
                domain, 
                js_paths, 
                use_subdomain=True,
                subdomain=location_info.get("subdomain")
            )
        elif location_info.get("use_folders", False):
            from utils import build_urls
            urls = build_urls(
                domain, 
                js_paths, 
                use_folders=True,
                folder=location_info.get("folder")
            )
        else:
            from utils import build_urls
            urls = build_urls(domain, js_paths)
        
        # URL'leri tara
        for url, description in urls:
            is_js, content_type = await self.check_js_file(url)
            if is_js:
                # JS dosyasının yolunu çıkar
                js_path = self._extract_js_path(url, domain, description)
                
                logger.info(f"JavaScript bulundu: {url} ({content_type})")
                return domain, description, js_path
        
        return None
    
    def _extract_js_path(self, url: str, domain: str, description: str) -> str:
        """
        URL'den JavaScript dosyasının yolunu çıkarır
        
        Args:
            url: Tam URL
            domain: Domain adı
            description: Açıklama (root, folder(xxx), subdomain(xxx))
            
        Returns:
            str: JavaScript dosya yolu (/wp-includes/js/jquery/jquery.min.js gibi)
        """
        if description.startswith("subdomain("):
            subdomain = description[10:-1]  # subdomain(blog) -> blog
            base = f"{subdomain}.{domain}"
            if base in url:
                return url.split(base, 1)[1]
        elif description.startswith("folder("):
            folder = description[7:-1]  # folder(blog) -> blog
            base = f"{domain}/{folder}"
            if base in url:
                return url.split(base, 1)[1]
        else:
            # Kök dizin
            if domain in url:
                parts = url.split(domain, 1)
                if len(parts) > 1:
                    return parts[1]
        
        # Fallback: protokolü kaldır ve domain'den sonrasını al
        protocol_parts = url.split("://", 1)
        if len(protocol_parts) > 1:
            domain_parts = protocol_parts[1].split("/", 1)
            if len(domain_parts) > 1:
                return "/" + domain_parts[1]
        
        return url  # Son çare olarak tam URL'yi döndür 