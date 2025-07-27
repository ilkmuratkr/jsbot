"""
JavaScript Tarama Botu Ana Programı

Bu program, verilen domain listesini ve belirtilen JavaScript dosyalarını asenkron olarak tarar.
"""

import asyncio
import time
import sys
from typing import List, Dict, Any, Set
from collections import defaultdict

import config
from utils import logger, chunk_list
from file_handler import FileHandler
from requester import JSRequester

class JSScannerBot:
    def __init__(self):
        """JavaScript Tarama Botunu başlatır"""
        self.file_handler = FileHandler(
            domain_file=config.DOMAIN_LIST_FILE,
            output_file=config.OUTPUT_FILE
        )
        self.requester = JSRequester(
            timeout=config.TIMEOUT,
            retry_count=config.RETRY_COUNT
        )
        self.processed_domains: Set[str] = set()
        self.domain_found_count: Dict[str, int] = defaultdict(int)  # Her domain'in kaç kez bulunduğunu takip eder
        self.success_count = 0
        self.start_time = time.time()
    
    async def scan_domain_list_for_js(self, domains: List[str], js_paths: List[str], 
                                     location_info: Dict[str, Any]) -> None:
        """
        Domain listesini JavaScript dosyaları için tarar.
        
        Args:
            domains: Taranacak domain listesi
            js_paths: Kontrol edilecek JavaScript yolları
            location_info: Konum bilgisi (kök, klasör, subdomain)
        """
        tasks = []
        
        # 3 kez bulunmuş domainleri filtrele
        domains_to_scan = []
        for domain in domains:
            if self.domain_found_count[domain] < 3:
                domains_to_scan.append(domain)
        
        if not domains_to_scan:
            return
        
        # Her domain için tarama görevi oluştur
        for domain in domains_to_scan:
            task = asyncio.create_task(self._scan_and_save_domain(
                domain, js_paths, location_info
            ))
            tasks.append(task)
        
        # Tüm görevleri çalıştır ve tamamlanmasını bekle
        await asyncio.gather(*tasks)
    
    async def _scan_and_save_domain(self, domain: str, js_paths: List[str], 
                                   location_info: Dict[str, Any]) -> None:
        """
        Bir domaini tarar ve bulduğu anda sonucu kaydeder.
        
        Args:
            domain: Taranacak domain
            js_paths: Kontrol edilecek JavaScript yolları
            location_info: Konum bilgisi (kök, klasör, subdomain)
        """
        result = await self.requester.scan_domain_for_js(domain, js_paths, location_info)
        if result:
            domain, description, js_path = result
            # Sonucu hemen kaydet
            await self.file_handler.save_result(domain, description, js_path)
            
            # Domain bulunma sayısını artır
            self.domain_found_count[domain] += 1
            self.success_count += 1
            
            # Eğer domain 3 kez bulunduysa log'a yaz
            if self.domain_found_count[domain] == 3:
                logger.info(f"Domain {domain} 3 kez bulundu, daha fazla tarama yapılmayacak")
    
    async def process_domains_in_chunks(self, domains: List[str], js_paths: List[str], 
                                      location_info: Dict[str, Any]) -> None:
        """
        Domain listesini parçalar halinde işler.
        
        Args:
            domains: Taranacak domain listesi
            js_paths: Kontrol edilecek JavaScript yolları
            location_info: Konum bilgisi (kök, klasör, subdomain)
        """
        # Domainleri parçalara ayır
        domain_chunks = chunk_list(domains, config.CHUNK_SIZE)
        
        total_chunks = len(domain_chunks)
        for i, chunk in enumerate(domain_chunks):
            chunk_desc = location_info.get("description", "root")
            logger.info(f"Chunk {i+1}/{total_chunks} taranıyor ({chunk_desc}): {len(chunk)} domain")
            
            await self.scan_domain_list_for_js(chunk, js_paths, location_info)
            
            # İlerleme raporu
            elapsed = time.time() - self.start_time
            domains_per_second = i * config.CHUNK_SIZE / elapsed if elapsed > 0 else 0
            logger.info(f"İlerleme: {i+1}/{total_chunks} chunk, {self.success_count} başarılı, "
                       f"{domains_per_second:.2f} domain/s")
    
    async def run(self) -> None:
        """Ana tarama işlemini başlatır"""
        try:
            # Domainleri oku
            domains = self.file_handler.read_domains()
            if not domains:
                logger.error("Taranacak domain bulunamadı. Çıkılıyor.")
                return
            
            # Daha önce işlenmiş domainleri al
            self.processed_domains = self.file_handler.get_already_processed_domains()
            if self.processed_domains:
                logger.info(f"{len(self.processed_domains)} domain daha önce işlenmiş, atlanacak")
            
            # 1. Kök dizin taraması
            logger.info(f"Kök dizin taraması başlatılıyor ({len(domains)} domain)")
            await self.process_domains_in_chunks(
                domains, 
                config.JS_PATHS, 
                {"description": "root"}
            )
            
            # 2. Klasör taraması
            for folder in config.FOLDERS:
                logger.info(f"Klasör taraması başlatılıyor: {folder}")
                await self.process_domains_in_chunks(
                    domains,
                    config.JS_PATHS,
                    {
                        "use_folders": True,
                        "folder": folder,
                        "description": f"folder({folder})"
                    }
                )
            
            # 3. Subdomain taraması
            for subdomain in config.SUBDOMAINS:
                logger.info(f"Subdomain taraması başlatılıyor: {subdomain}")
                await self.process_domains_in_chunks(
                    domains,
                    config.JS_PATHS,
                    {
                        "use_subdomain": True,
                        "subdomain": subdomain,
                        "description": f"subdomain({subdomain})"
                    }
                )
            
            # Toplam çalışma süresi
            total_time = time.time() - self.start_time
            logger.info(f"Tarama tamamlandı: {self.success_count} başarılı sonuç, "
                       f"{total_time:.2f} saniyede")
            
        except KeyboardInterrupt:
            logger.info("Kullanıcı tarafından durduruldu")
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {str(e)}")
        finally:
            # Kaynakları temizle
            await self.requester.close()

async def main():
    """Ana program giriş noktası"""
    scanner = JSScannerBot()
    await scanner.run()

if __name__ == "__main__":
    # Windows için gerekli yapılandırma
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Ana program döngüsünü başlat
    asyncio.run(main()) 