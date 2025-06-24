#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""База данных клиентов для EventBot AI v2.0"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ClientDatabase:
    def __init__(self, db_file="data/clients.json"):
        self.db_file = Path(db_file)
        self.logger = logging.getLogger(__name__)
        self.data = {"clients": [], "estimates": [], "statistics": {}}
        self._ensure_db_exists()
        self._load_database()
    
    def _ensure_db_exists(self):
        """Создание файла БД если не существует"""
        try:
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
            
            if not self.db_file.exists():
                initial_data = {
                    "clients": [
                        {
                            "id": "client_001",
                            "telegram_id": 7722156884,
                            "username": "manager",
                            "first_name": "Менеджер",
                            "registration_date": datetime.now().isoformat(),
                            "total_orders": 0,
                            "total_amount": 0
                        }
                    ],
                    "estimates": [],
                    "statistics": {
                        "total_estimates": 0,
                        "total_revenue": 0,
                        "created_date": datetime.now().isoformat()
                    }
                }
                
                with open(self.db_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, ensure_ascii=False, indent=2)
                
                self.logger.info("База данных создана")
                
        except Exception as e:
            self.logger.error(f"Ошибка создания БД: {e}")
    
    def _load_database(self):
        """Загрузка базы данных"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            self.logger.info("База данных загружена")
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки БД: {e}")
            self.data = {"clients": [], "estimates": [], "statistics": {}}
    
    def save_estimate(self, estimate_id: str, estimate_data: Dict, request_data: Dict) -> bool:
        """Сохранение сметы"""
        try:
            estimate_record = {
                "id": estimate_id,
                "date": datetime.now().isoformat(),
                "event_type": request_data.get('event_type'),
                "guest_count": request_data.get('guest_count'),
                "total_cost": estimate_data.get('total_cost'),
                "cost_per_guest": estimate_data.get('cost_per_guest'),
                "status": "created"
            }
            
            self.data["estimates"].append(estimate_record)
            
            # Обновляем статистику
            stats = self.data.get("statistics", {})
            stats["total_estimates"] = stats.get("total_estimates", 0) + 1
            stats["total_revenue"] = stats.get("total_revenue", 0) + estimate_data.get('total_cost', 0)
            stats["last_update"] = datetime.now().isoformat()
            
            self._save_database()
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения сметы: {e}")
            return False
    
    def _save_database(self):
        """Сохранение базы данных"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Ошибка сохранения БД: {e}")
    
    def get_statistics(self) -> Dict:
        """Получение статистики"""
        return self.data.get("statistics", {})
