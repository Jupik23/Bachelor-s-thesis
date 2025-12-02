import httpx
import logging
import os
import tempfile
#import openpyxl
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.medication import PolishMedication
from app.schemas.medication import RplDownloadStats

RPL_XLSX_URL = "https://rejestrymedyczne.ezdrowie.gov.pl/api/rpl/medicinal-products/public-pl-report/get-xlsx"

class RPLService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def update_database_from_rpl(self) -> RplDownloadStats:
        self.logger.info("Rozpoczynanie aktualizacji bazy RPL (tryb Excel)...")
        stats = RplDownloadStats(total_processed=0, added=0, errors=0)
        
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                tmp_path = tmp_file.name
                self.logger.info(f"Pobieranie XLSX z {RPL_XLSX_URL} do: {tmp_path}")
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                async with httpx.AsyncClient(timeout=600.0, verify=False) as client:
                    async with client.stream("GET", RPL_XLSX_URL, headers=headers) as response:
                        response.raise_for_status()
                        async for chunk in response.aiter_bytes():
                            tmp_file.write(chunk)
            self.logger.info("Czyszczenie tabeli polish_medications...")
            try:
                self.db.execute(text("TRUNCATE TABLE polish_medications RESTART IDENTITY CASCADE;"))
            except Exception:
                self.db.query(PolishMedication).delete()
            self.db.commit()
            self.logger.info("Otwieranie pliku Excel...")
            wb = openpyxl.load_workbook(tmp_path, read_only=True)
            ws = wb.active
            
            batch = []
            BATCH_SIZE = 5000 
            
            rows = ws.iter_rows(values_only=True)
            
            try:
                header_row = next(rows)
                header_map = {str(col).strip().lower(): idx for idx, col in enumerate(header_row) if col}
                self.logger.info(f"Znalezione kolumny: {list(header_map.keys())[:5]}...")
            except StopIteration:
                self.logger.error("Plik Excel jest pusty!")
                return stats

            col_name_idx = header_map.get('nazwa produktu leczniczego', 0)
            col_subst_idx = header_map.get('nazwa powszechnie stosowana', 1)
            col_moc_idx = header_map.get('moc', 2)
            col_form_idx = header_map.get('postać farmaceutyczna', 3)

            self.logger.info("Rozpoczynanie importu wierszy...")

            for row in rows:
                stats.total_processed += 1
                try:
                    name = row[col_name_idx]
                    
                    if name:
                        substance = row[col_subst_idx] if col_subst_idx < len(row) else None
                        strength = row[col_moc_idx] if col_moc_idx < len(row) else None
                        form = row[col_form_idx] if col_form_idx < len(row) else None

                        new_med = PolishMedication(
                            trade_name=str(name)[:250],
                            active_substance=str(substance)[:250] if substance else "N/A",
                            strength=str(strength)[:100] if strength else None,
                            form=str(form)[:200] if form else None
                        )
                        batch.append(new_med)

                except Exception:
                    stats.errors += 1
                
                if len(batch) >= BATCH_SIZE:
                    self.db.bulk_save_objects(batch)
                    self.db.commit()
                    stats.added += len(batch)
                    batch = []

            if batch:
                self.db.bulk_save_objects(batch)
                self.db.commit()
                stats.added += len(batch)
            
            wb.close()

        except Exception as e:
            self.logger.error(f"Krytyczny błąd importu RPL: {e}")
            raise e
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        
        final_count = self.db.query(PolishMedication).count()
        self.logger.info(f"Zakończono import. Rekordów w bazie: {final_count}. Statystyki: {stats}")
        return stats

    def search_polish_medications(self, query: str, limit: int = 50):
        search_query = f"%{query}%"
        results = self.db.query(PolishMedication).filter(
            PolishMedication.trade_name.ilike(search_query)
        ).limit(limit).all()
        
        return [f"{r.trade_name} || {r.active_substance}" for r in results]
    def get_exact_medication(self, name: str):
        name = name.strip()
        med = self.db.query(PolishMedication).filter(
            PolishMedication.trade_name == name
        ).first()
        
        if med:
            self.logger.info(f"Exact match for: {name}")
            return med
        med = self.db.query(PolishMedication).filter(
            PolishMedication.trade_name.ilike(name)
        ).first()
        
        if med:
            self.logger.info(f"Case-insensitive match for: {name}")
            return med
        med = self.db.query(PolishMedication).filter(
            PolishMedication.trade_name.ilike(f"{name}%")
        ).first()
        
        if med:
            self.logger.info(f"Prefix match for: {name} -> {med.trade_name}")
            return med
        med = self.db.query(PolishMedication).filter(
            PolishMedication.trade_name.ilike(f"%{name}%")
        ).first()
        
        if med:
            self.logger.info(f"Partial match for: {name} -> {med.trade_name}")
            return med
        
        self.logger.warning(f"No match found for: {name}")
        return None

    def get_active_substance(self, trade_name: str) -> str:
        med = self.get_exact_medication(trade_name)
        if med and med.active_substance and med.active_substance != "N/A":
            return med.active_substance
        return None