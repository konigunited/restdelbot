#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 ИСПРАВЛЕННЫЙ CateringRulesService v2.1 - FORCED RELOAD
ВНИМАНИЕ: Принудительная перезагрузка расчетов!
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# ПРИНУДИТЕЛЬНОЕ ЛОГИРОВАНИЕ
print("🔥 ЗАГРУЖАЕТСЯ ИСПРАВЛЕННЫЙ CateringRulesService v2.1!")
logger.critical("🔥 ПРИНУДИТЕЛЬНАЯ ПЕРЕЗАГРУЗКА CateringRulesService!")

class CateringRulesService:
    """ИСПРАВЛЕННЫЙ сервис расчета - ПРИНУДИТЕЛЬНАЯ ВЕРСИЯ"""
    
    def __init__(self):
        print("🔧 ИНИЦИАЛИЗАЦИЯ ИСПРАВЛЕННОГО CateringRulesService!")
        logger.critical("🔧 СОЗДАЕТСЯ НОВЫЙ CateringRulesService v2.1!")
        
        # ПРАВИЛЬНЫЕ стандарты Rest Delivery
        self.event_standards = {
            'кофе-брейк': {
                'граммовка_мин': 200,
                'граммовка_макс': 300,
                'цена_мин': 1500,
                'цена_макс': 2500,
                'коэффициент_персонала': 0.03
            },
            'фуршет': {
                'граммовка_мин': 300,
                'граммовка_макс': 500,
                'цена_мин': 2500,
                'цена_макс': 4500,
                'коэффициент_персонала': 0.05
            },
            'банкет': {
                'граммовка_мин': 600,
                'граммовка_макс': 1200,
                'цена_мин': 4000,
                'цена_макс': 8000,
                'коэффициент_персонала': 0.1
            }
        }
        
        logger.critical("✅ ИСПРАВЛЕННЫЕ СТАНДАРТЫ ЗАГРУЖЕНЫ!")
        print("✅ ИСПРАВЛЕННЫЕ СТАНДАРТЫ ЗАГРУЖЕНЫ!")
    
    def calculate_estimate(self, 
                         menu_items: List[Dict[str, Any]], 
                         guest_count: int, 
                         event_type: str = 'фуршет',
                         target_budget: Optional[float] = None) -> Dict[str, Any]:
        """
        🔧 ИСПРАВЛЕННЫЙ расчет сметы - ПРИНУДИТЕЛЬНАЯ ВЕРСИЯ
        """
        print(f"🔧 ИСПРАВЛЕННЫЙ РАСЧЕТ ЗАПУЩЕН! Гостей: {guest_count}, Тип: {event_type}")
        logger.critical(f"🔧 ИСПРАВЛЕННЫЙ РАСЧЕТ! Гостей: {guest_count}, Тип: {event_type}")
        
        try:
            # Нормализуем тип мероприятия
            event_type = self._normalize_event_type(event_type)
            standards = self.event_standards.get(event_type, self.event_standards['фуршет'])
            
            print(f"📊 Стандарты: {standards}")
            logger.critical(f"📊 Используемые стандарты: {standards}")
            
            # ПРОСТОЙ И ПРАВИЛЬНЫЙ расчет
            target_cost_per_guest = (standards['цена_мин'] + standards['цена_макс']) / 2
            target_weight_per_guest = (standards['граммовка_мин'] + standards['граммовка_макс']) / 2
            
            # Ограничиваем количество блюд
            limited_items = menu_items[:8]  # Максимум 8 блюд
            
            # Простой расчет меню
            menu_cost = 0
            processed_items = []
            total_weight_per_guest = 0
            
            for i, item in enumerate(limited_items):
                # Простое количество - 1-2 порции на человека
                quantity = guest_count + (guest_count // 3)  # +33% запас
                
                # Ограничиваем цену за порцию
                item_price = min(item.get('price', 200), 1000)  # Максимум 1000₽ за порцию
                item_weight = item.get('weight', 100)
                
                item_total_cost = quantity * item_price
                item_weight_per_guest = (quantity * item_weight) / guest_count
                
                processed_items.append({
                    'id': item.get('id', i+1),
                    'name': item.get('name', f'Блюдо {i+1}'),
                    'quantity': quantity,
                    'price': item_price,
                    'total_cost': item_total_cost,
                    'weight_per_person': item_weight_per_guest
                })
                
                menu_cost += item_total_cost
                total_weight_per_guest += item_weight_per_guest
            
            # ЗАЩИТА от безумных цен
            max_reasonable_menu_cost = guest_count * target_cost_per_guest * 0.7  # 70% на меню
            if menu_cost > max_reasonable_menu_cost:
                print(f"⚠️ КОРРЕКТИРУЕМ ЦЕНУ! Было: {menu_cost}, станет: {max_reasonable_menu_cost}")
                correction_factor = max_reasonable_menu_cost / menu_cost
                menu_cost = max_reasonable_menu_cost
                for item in processed_items:
                    item['total_cost'] *= correction_factor
            
            # ЗАЩИТА от безумной граммовки  
            if total_weight_per_guest > standards['граммовка_макс']:
                print(f"⚠️ КОРРЕКТИРУЕМ ГРАММОВКУ! Было: {total_weight_per_guest}, станет: {standards['граммовка_макс']}")
                total_weight_per_guest = standards['граммовка_макс']
            
            # Простой расчет услуг (30% от общей стоимости)
            service_cost = menu_cost * 0.43  # 30/70 = 0.43
            total_cost = menu_cost + service_cost
            cost_per_guest = total_cost / guest_count
            
            print(f"💰 ИТОГОВЫЕ РАСЧЕТЫ:")
            print(f"  Меню: {menu_cost:,.0f}₽")
            print(f"  Услуги: {service_cost:,.0f}₽") 
            print(f"  ИТОГО: {total_cost:,.0f}₽ ({cost_per_guest:,.0f}₽/чел)")
            print(f"  Граммовка: {total_weight_per_guest:.0f}г/чел")
            
            logger.critical(f"💰 ИСПРАВЛЕННЫЙ РЕЗУЛЬТАТ: {total_cost:,.0f}₽ ({cost_per_guest:,.0f}₽/чел)")
            logger.critical(f"📊 ИСПРАВЛЕННАЯ ГРАММОВКА: {total_weight_per_guest:.0f}г/чел")
            
            estimate = {
                'id': f"FIXED-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                'event_type': event_type.title(),
                'guest_count': guest_count,
                'menu_items': processed_items,
                'menu_cost': menu_cost,
                'menu_items_count': len(processed_items),
                'weight_per_person': total_weight_per_guest,
                'service_cost': service_cost,
                'total_cost': total_cost,
                'cost_per_guest': cost_per_guest,
                'standards': standards,
                'warnings': [],
                'created_at': datetime.now().isoformat(),
                'version': 'FIXED-v2.1'
            }
            
            return estimate
            
        except Exception as e:
            print(f"❌ ОШИБКА В ИСПРАВЛЕННОМ РАСЧЕТЕ: {e}")
            logger.error(f"❌ Ошибка исправленного расчета: {e}")
            import traceback
            print(traceback.format_exc())
            return self._create_emergency_estimate(guest_count, event_type)
    
    def _normalize_event_type(self, event_type: str) -> str:
        """Нормализация типа мероприятия"""
        event_type = event_type.lower()
        
        if 'банкет' in event_type:
            return 'банкет'
        elif 'фуршет' in event_type:
            return 'фуршет'  
        elif 'кофе' in event_type or 'брейк' in event_type:
            return 'кофе-брейк'
        else:
            return 'фуршет'
    
    def _create_emergency_estimate(self, guest_count: int, event_type: str) -> Dict[str, Any]:
        """Аварийная смета"""
        event_type = self._normalize_event_type(event_type)
        standards = self.event_standards.get(event_type, self.event_standards['фуршет'])
        
        cost_per_guest = (standards['цена_мин'] + standards['цена_макс']) / 2
        total_cost = cost_per_guest * guest_count
        
        print(f"🚨 АВАРИЙНАЯ СМЕТА: {total_cost:,.0f}₽ ({cost_per_guest:,.0f}₽/чел)")
        
        return {
            'id': f"EMERGENCY-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'event_type': event_type.title(),
            'guest_count': guest_count,
            'menu_items': [{'name': 'Стандартный набор', 'quantity': guest_count, 'price': cost_per_guest}],
            'menu_cost': total_cost * 0.7,
            'service_cost': total_cost * 0.3,
            'total_cost': total_cost,
            'cost_per_guest': cost_per_guest,
            'weight_per_person': (standards['граммовка_мин'] + standards['граммовка_макс']) / 2,
            'warnings': ['🚨 Аварийный режим'],
            'created_at': datetime.now().isoformat(),
            'version': 'EMERGENCY'
        }