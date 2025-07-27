"""
Dosya işlemleri modülü.
Domain listesi okuma ve sonuçları kaydetme işlemlerini yönetir.
"""

import os
import csv
from typing import List, Set
import asyncio
from utils import logger, normalize_domain

class FileHandler:
    def __init__(self, domain_file: str, output_file: str):
        """
        Dosya işleyici sınıfını başlatır.
        
        Args:
            domain_file: Domain listesini içeren dosya yolu
            output_file: Sonuçların kaydedileceği dosya yolu
        """
        self.domain_file = domain_file
        self.output_file = output_file
        self._lock = asyncio.Lock()  # Asenkron yazma işlemleri için kilit
        
        # CSV başlığını oluştur
        if not os.path.exists(self.output_file):
            self._create_csv_header()
        
    def _create_csv_header(self):
        """CSV dosyasına başlık satırını ekler"""
        try:
            with open(self.output_file, 'w', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['url', 'js_path'])
        except Exception as e:
            logger.error(f"CSV başlık oluşturma hatası: {str(e)}")
        
    def read_domains(self) -> List[str]:
        """
        Domain listesini dosyadan okur ve normalize eder.
        
        Returns:
            List[str]: Normalize edilmiş domain listesi
        """
        if not os.path.exists(self.domain_file):
            logger.error(f"Domain dosyası bulunamadı: {self.domain_file}")
            return []
        
        try:
            with open(self.domain_file, 'r', encoding='utf-8') as file:
                domains = [normalize_domain(line) for line in file if line.strip()]
            
            # Yinelenen domainleri kaldır
            domains = list(dict.fromkeys(domains))
            
            logger.info(f"Toplam {len(domains)} domain okundu")
            return domains
        except Exception as e:
            logger.error(f"Domain dosyası okuma hatası: {str(e)}")
            return []
    
    async def save_result(self, domain: str, description: str, js_path: str) -> None:
        """
        Başarılı bir JavaScript bulma sonucunu CSV dosyasına kaydeder.
        
        Args:
            domain: Bulunan domain
            description: Açıklama (kök, klasör adı veya subdomain)
            js_path: Bulunan JavaScript dosyasının yolu
        """
        domain = normalize_domain(domain)
        
        # URL'yi oluştur
        url = self._format_url(domain, description)
        
        async with self._lock:  # Dosyaya eşzamanlı yazmak için kilit kullanılıyor
            try:
                with open(self.output_file, 'a', encoding='utf-8', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([url, js_path])
                    
                logger.info(f"Sonuç kaydedildi: {url},{js_path}")
            except Exception as e:
                logger.error(f"Sonuç kaydetme hatası: {str(e)}")
    
    def _format_url(self, domain: str, description: str) -> str:
        """
        URL'yi istenilen formatta oluşturur
        
        Args:
            domain: Domain adı
            description: Açıklama (root, folder(xxx), subdomain(xxx))
            
        Returns:
            str: Formatlanmış URL
        """
        if description == "root":
            return domain
        elif description.startswith("folder("):
            folder = description[7:-1]  # folder(blog) -> blog
            return f"{domain}/{folder}"
        elif description.startswith("subdomain("):
            subdomain = description[10:-1]  # subdomain(blog) -> blog
            return f"{subdomain}.{domain}"
        else:
            return domain
    
    async def save_results_batch(self, results: List[tuple]) -> None:
        """
        Her sonucu hemen kaydet, toplu kaydetme yerine tekli kaydetme yap
        
        Args:
            results: (domain, description, js_path) üçlülerinden oluşan liste
        """
        if not results:
            return
        
        for domain, description, js_path in results:
            await self.save_result(domain, description, js_path)
    
    def get_already_processed_domains(self) -> Set[str]:
        """
        Daha önce işlenmiş domainleri döndürür (eğer dosya varsa).
        
        Returns:
            Set[str]: İşlenmiş domainler kümesi
        """
        processed = set()
        
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8', newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader, None)  # Başlık satırını atla
                    
                    for row in reader:
                        if row and len(row) >= 1:
                            url = row[0]
                            # URL'den domain'i çıkar
                            if "/" in url:
                                domain = url.split("/")[0]
                            elif "." in url and url.count(".") > 1:
                                domain = ".".join(url.split(".")[-2:])
                            else:
                                domain = url
                                
                            processed.add(domain)
                            
            except Exception as e:
                logger.error(f"İşlenmiş domainleri okuma hatası: {str(e)}")
        
        return processed 