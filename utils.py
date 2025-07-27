"""
Yardımcı fonksiyonlar modülü.
URL manipülasyonu ve içerik doğrulama fonksiyonlarını içerir.
"""

import logging
from typing import List, Tuple
import config

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("js_scanner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("js_scanner")

def is_javascript_content_type(content_type: str) -> bool:
    """
    Bir Content-Type başlığının JavaScript içeriğini belirtip belirtmediğini kontrol eder.
    
    Args:
        content_type: HTTP yanıtından alınan Content-Type başlığı
        
    Returns:
        bool: JavaScript içeriği ise True, değilse False
    """
    if not content_type:
        return False
    
    content_type = content_type.lower()
    return any(js_type in content_type for js_type in config.JS_CONTENT_TYPES)

def normalize_domain(domain: str) -> str:
    """
    Bir domain adını normalize eder (http://, https://, www. gibi önekleri kaldırır).
    
    Args:
        domain: Normalize edilecek domain adı
        
    Returns:
        str: Normalize edilmiş domain adı
    """
    domain = domain.strip().lower()
    for prefix in ["http://", "https://", "www."]:
        if domain.startswith(prefix):
            domain = domain[len(prefix):]
    
    if domain.endswith("/"):
        domain = domain[:-1]
    
    return domain

def build_urls(domain: str, js_paths: List[str], use_folders: bool = False, 
              folder: str = None, use_subdomain: bool = False, 
              subdomain: str = None) -> List[Tuple[str, str]]:
    """
    Belirli bir domain ve JavaScript yolları için URL listesi oluşturur.
    
    Args:
        domain: Taranacak domain adı
        js_paths: JavaScript dosya yolları listesi
        use_folders: Klasörleri kullanıp kullanmayacağını belirten bayrak
        folder: Kullanılacak klasör (use_folders=True ise)
        use_subdomain: Subdomain kullanıp kullanmayacağını belirten bayrak
        subdomain: Kullanılacak subdomain (use_subdomain=True ise)
        
    Returns:
        List[Tuple[str, str]]: (tam_url, açıklama) çiftlerinden oluşan liste
    """
    urls = []
    domain = normalize_domain(domain)
    
    for protocol in config.PROTOCOLS:
        base_url = ""
        description = ""
        
        if use_subdomain and subdomain:
            base_url = f"{protocol}{subdomain}.{domain}"
            description = f"subdomain({subdomain})"
        elif use_folders and folder:
            base_url = f"{protocol}{domain}/{folder}"
            description = f"folder({folder})"
        else:
            base_url = f"{protocol}{domain}"
            description = "root"
        
        for js_path in js_paths:
            url = f"{base_url}{js_path}"
            urls.append((url, description))
    
    return urls

def chunk_list(input_list: List, chunk_size: int) -> List[List]:
    """
    Bir listeyi belirli boyutlarda parçalara ayırır.
    
    Args:
        input_list: Parçalanacak liste
        chunk_size: Her parçanın maksimum boyutu
        
    Returns:
        List[List]: Parçalanmış liste
    """
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)] 