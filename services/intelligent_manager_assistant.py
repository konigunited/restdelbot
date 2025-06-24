#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 SuperAIAgent - Интеллектуальный ассистент для EventBot
Продвинутая обработка запросов с учетом контекста бизнеса РестДеливери
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class IntelligentAssistant:
    """Базовый интеллектуальный ассистент"""
    
    def __init__(self, claude_service, menu_service, catering_rules):
        self.claude_service = claude_service
        self.menu_service = menu_service
        self.catering_rules = catering_rules
        logger.info("✅ IntelligentAssistant инициализирован")
    
    async def get_smart_response(self, user_message: str) -> str:
        """Получение умного ответа на запрос пользователя"""
        try:
            # Анализируем тип запроса
            request_type = self._analyze_request_type(user_message)
            
            if request_type == "estimate":
                return await self._handle_estimate_request(user_message)
            elif request_type == "menu_info":
                return await self._handle_menu_info(user_message)
            elif request_type == "pricing":
                return await self._handle_pricing_info(user_message)
            else:
                return await self._handle_general_request(user_message)
                
        except Exception as e:
            logger.error(f"❌ Ошибка IntelligentAssistant: {e}")
            return "😔 Произошла ошибка при обработке запроса. Попробуйте переформулировать."
    
    def _analyze_request_type(self, message: str) -> str:
        """Анализ типа запроса"""
        message_lower = message.lower()
        
        # Ключевые слова для определения типа
        estimate_keywords = ['человек', 'персон', 'гостей', 'бюджет', 'корпоратив', 'банкет', 'фуршет']
        menu_keywords = ['меню', 'блюда', 'что есть', 'ассортимент', 'позиции']
        pricing_keywords = ['цена', 'стоимость', 'сколько', 'тариф', 'прайс']
        
        if any(keyword in message_lower for keyword in estimate_keywords):
            return "estimate"
        elif any(keyword in message_lower for keyword in menu_keywords):
            return "menu_info"
        elif any(keyword in message_lower for keyword in pricing_keywords):
            return "pricing"
        else:
            return "general"
    
    async def _handle_estimate_request(self, message: str) -> str:
        """Обработка запроса на смету"""
        return (
            "📋 Для создания сметы мне нужна информация:\n\n"
            "• Количество гостей\n"
            "• Формат мероприятия (фуршет, банкет, корпоратив)\n"
            "• Желаемый бюджет (если есть ограничения)\n\n"
            "Пример: `Корпоратив 50 человек бюджет 150000`"
        )
    
    async def _handle_menu_info(self, message: str) -> str:
        """Информация о меню"""
        menu_stats = self.menu_service.get_menu_stats()
        return (
            f"📋 **Наше меню:**\n\n"
            f"• Всего позиций: {menu_stats['total_items']}\n"
            f"• Категорий: {menu_stats['categories']}\n\n"
            f"Популярные категории:\n"
            f"• Канапе и брускетты\n"
            f"• Салаты и закуски\n"
            f"• Горячие блюда\n"
            f"• Десерты\n\n"
            f"Отправьте параметры мероприятия для подбора меню!"
        )
    
    async def _handle_pricing_info(self, message: str) -> str:
        """Информация о ценах"""
        return (
            "💰 **Ориентировочные цены:**\n\n"
            "**Кофе-брейк:** 1000-2000₽/чел\n"
            "**Фуршет:** 2000-4000₽/чел\n"
            "**Банкет:** 4000-8000₽/чел\n"
            "**VIP:** от 8000₽/чел\n\n"
            "Точная стоимость зависит от:\n"
            "• Выбранного меню\n"
            "• Необходимых услуг\n"
            "• Количества персонала\n\n"
            "Отправьте запрос для точного расчета!"
        )
    
    async def _handle_general_request(self, message: str) -> str:
        """Обработка общих запросов"""
        if self.claude_service and self.claude_service.is_available():
            try:
                response = await self.claude_service.get_response(message)
                return response
            except:
                pass
        
        return (
            "👋 Я помогу вам с организацией мероприятия!\n\n"
            "Что я могу:\n"
            "• Рассчитать смету для вашего события\n"
            "• Подобрать оптимальное меню\n"
            "• Рассчитать количество персонала\n"
            "• Ответить на вопросы о наших услугах\n\n"
            "Просто опишите ваше мероприятие!"
        )


class SuperAIAgent:
    """🧠 Супер ИИ-агент с продвинутой логикой обработки запросов"""
    
    def __init__(self, claude_service, menu_service, catering_rules):
        self.claude_service = claude_service
        self.menu_service = menu_service
        self.catering_rules = catering_rules
        self.excel_generator = None  # Будет установлен извне
        
        # Загружаем бизнес-контекст
        self._load_business_context()
        
        logger.info("🎉 SuperAIAgent инициализирован!")
    
    def _load_business_context(self):
        """Загрузка контекста бизнеса РестДеливери"""
        self.business_context = {
            'company_name': 'РестДеливери',
            'services': ['фуршет', 'банкет', 'корпоратив', 'кофе-брейк'],
            'min_order': 10000,
            'delivery_area': 'Москва и область',
            'working_hours': '9:00-21:00',
            'order_deadline': 'за сутки до мероприятия',
            'special_features': [
                'Премиальные блюда от шеф-повара',
                'Красивая подача и оформление',
                'Профессиональное обслуживание',
                'Гибкие условия оплаты'
            ]
        }
        
        # Стандарты обслуживания
        self.service_standards = {
            'кофе-брейк': {
                'duration': '30-90 мин',
                'weight_per_person': '150-300г',
                'price_range': '1000-2000₽',
                'staff_ratio': 30  # 1 официант на 30 человек
            },
            'фуршет': {
                'duration': '2-4 часа',
                'weight_per_person': '200-500г',
                'price_range': '2000-4000₽',
                'staff_ratio': 20
            },
            'банкет': {
                'duration': '3-6 часов',
                'weight_per_person': '600-1700г',
                'price_range': '4000-8000₽',
                'staff_ratio': 10
            },
            'корпоратив': {
                'duration': '3-5 часов',
                'weight_per_person': '300-800г',
                'price_range': '2500-5000₽',
                'staff_ratio': 15
            }
        }
    
    async def process_super_request(self, message: str, user_info: Dict[str, Any]) -> str:
        """🚀 Главный метод обработки запросов"""
        try:
            logger.info(f"🧠 SuperAI обрабатывает: {message[:50]}...")
            
            # Извлекаем параметры из сообщения
            event_params = self._extract_event_params(message)
            
            # Определяем намерение пользователя
            intent = self._detect_intent(message)
            
            logger.info(f"📊 Параметры: {event_params}")
            logger.info(f"🎯 Намерение: {intent}")
            
            # Обрабатываем в зависимости от намерения
            if intent == "create_estimate":
                return await self._create_smart_estimate(event_params, user_info)
            elif intent == "menu_consultation":
                return await self._provide_menu_consultation(event_params)
            elif intent == "price_calculation":
                return await self._calculate_pricing(event_params)
            elif intent == "service_info":
                return await self._provide_service_info(message)
            elif intent == "order_status":
                return await self._check_order_status(message, user_info)
            else:
                return await self._handle_general_inquiry(message, user_info)
                
        except Exception as e:
            logger.error(f"❌ Ошибка SuperAI: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._get_error_response()
    
    def _extract_event_params(self, message: str) -> Dict[str, Any]:
        """Извлечение параметров мероприятия из текста"""
        params = {
            'guest_count': None,
            'event_type': None,
            'budget': None,
            'budget_per_person': None,
            'date': None,
            'duration': None,
            'special_requests': []
        }
        
        message_lower = message.lower()
        
        # Извлекаем количество гостей
        guest_patterns = [
            r'(\d+)\s*(?:человек|персон|гостей|чел\.?)',
            r'на\s*(\d+)\s*(?:человек|персон|гостей)',
            r'(?:человек|персон|гостей)[:.\s]*(\d+)'
        ]
        
        for pattern in guest_patterns:
            match = re.search(pattern, message_lower)
            if match:
                params['guest_count'] = int(match.group(1))
                break
        
        # Определяем тип мероприятия
        event_types = {
            'фуршет': ['фуршет', 'фуршетн', 'стоячий'],
            'банкет': ['банкет', 'банкетн', 'рассадк', 'сидячий'],
            'корпоратив': ['корпоратив', 'корпоративн', 'компани', 'офис'],
            'кофе-брейк': ['кофе', 'брейк', 'кофебрейк', 'перерыв'],
            'презентация': ['презентаци', 'presentat'],
            'день рождения': ['день рождения', 'др ', 'birthday'],
            'свадьба': ['свадьб', 'свадеб']
        }
        
        for event_type, keywords in event_types.items():
            if any(keyword in message_lower for keyword in keywords):
                params['event_type'] = event_type
                break
        
        # Извлекаем бюджет
        budget_patterns = [
            r'бюджет[:\s]*(\d+)\s*(?:тыс|к|тысяч|000)',
            r'(\d+)\s*(?:тыс|к|тысяч)\s*(?:рублей|руб|₽)?',
            r'до\s*(\d+)\s*(?:тыс|к|тысяч|000)',
            r'(\d+)\s*000\s*(?:рублей|руб|₽)'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, message_lower)
            if match:
                budget_value = int(match.group(1))
                if budget_value < 1000:  # Если меньше 1000, считаем что это тысячи
                    params['budget'] = budget_value * 1000
                else:
                    params['budget'] = budget_value
                
                # Рассчитываем бюджет на человека
                if params['guest_count'] and params['budget']:
                    params['budget_per_person'] = params['budget'] / params['guest_count']
                break
        
        # Извлекаем дату
        date_patterns = [
            r'(\d{1,2})[./](\d{1,2})[./](\d{2,4})',
            r'(\d{1,2})\s*(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)',
            r'(завтра|послезавтра|через\s*\d+\s*дн)',
            r'(понедельник|вторник|среда|четверг|пятница|суббота|воскресенье)'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message_lower)
            if match:
                params['date'] = match.group(0)
                break
        
        # Особые пожелания
        special_keywords = {
            'вегетарианское': 'вегетарианское меню',
            'постное': 'постное меню',
            'детское': 'детское меню',
            'халяль': 'халяльное меню',
            'кошерное': 'кошерное меню',
            'безглютеновое': 'безглютеновое меню',
            'диетическое': 'диетическое меню'
        }
        
        for keyword, request in special_keywords.items():
            if keyword in message_lower:
                params['special_requests'].append(request)
        
        return params
    
    def _detect_intent(self, message: str) -> str:
        """Определение намерения пользователя"""
        message_lower = message.lower()
        
        # Паттерны для определения намерений
        intents = {
            'create_estimate': [
                'смет', 'расчет', 'рассчит', 'посчит', 'сколько стоит',
                'человек', 'персон', 'гостей', 'участник'
            ],
            'menu_consultation': [
                'меню', 'блюда', 'что входит', 'состав', 'ассортимент',
                'что есть', 'варианты', 'выбор'
            ],
            'price_calculation': [
                'цен', 'стоимост', 'стоит', 'прайс', 'тариф',
                'сколько', 'бюджет', 'дорого', 'дешево'
            ],
            'service_info': [
                'услуг', 'сервис', 'обслуживан', 'официант', 'повар',
                'доставк', 'оборудован', 'посуд'
            ],
            'order_status': [
                'статус', 'заказ', 'где мой', 'когда приедет',
                'отслеживан', 'готовность'
            ]
        }
        
        # Подсчитываем совпадения для каждого намерения
        intent_scores = {}
        for intent, keywords in intents.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Возвращаем намерение с максимальным счетом
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return 'general'
    
    async def _create_smart_estimate(self, params: Dict[str, Any], user_info: Dict[str, Any]) -> str:
        """Создание интеллектуальной сметы"""
        try:
            # Проверяем минимальные параметры
            if not params['guest_count']:
                return self._request_missing_params(params)
            
            # Определяем тип мероприятия если не указан
            if not params['event_type']:
                params['event_type'] = self._guess_event_type(params)
            
            # Используем Claude для анализа если доступен
            if self.claude_service and self.claude_service.is_available():
                claude_params = await self.claude_service.analyze_request(
                    f"{params['event_type']} {params['guest_count']} человек"
                    + (f" бюджет {params['budget']}" if params['budget'] else "")
                )
                if claude_params and claude_params.get('success'):
                    params.update(claude_params.get('data', {}))
            
            # Получаем подходящие блюда
            menu_items = self.menu_service.get_items_for_event_type(
                params['event_type'],
                params['guest_count'],
                params['budget_per_person']
            )
            
            if not menu_items:
                return self._no_menu_items_response(params)
            
            # Рассчитываем смету
            estimate = self.catering_rules.calculate_estimate(
                menu_items,
                params['guest_count'],
                params['event_type'],
                params['budget']
            )
            
            # Генерируем Excel если генератор доступен
            excel_path = None
            if self.excel_generator:
                try:
                    excel_path = self.excel_generator.create_estimate(estimate, params)
                    logger.info(f"📊 Excel создан: {excel_path}")
                except Exception as e:
                    logger.error(f"❌ Ошибка создания Excel: {e}")
            
            # Формируем ответ
            response = self._format_smart_estimate_response(estimate, params, user_info)
            
            # Добавляем информацию о файле если создан
            if excel_path:
                response += f"\n\n📊 **Excel файл готов!** Файл: `{excel_path}`"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания сметы: {e}")
            return self._get_error_response()
    
    def _guess_event_type(self, params: Dict[str, Any]) -> str:
        """Угадывание типа мероприятия по параметрам"""
        guest_count = params.get('guest_count', 50)
        budget_per_person = params.get('budget_per_person', 3000)
        
        # Логика определения
        if guest_count <= 30 and budget_per_person <= 2000:
            return 'кофе-брейк'
        elif budget_per_person >= 5000:
            return 'банкет'
        elif guest_count >= 50:
            return 'корпоратив'
        else:
            return 'фуршет'
    
    def _request_missing_params(self, params: Dict[str, Any]) -> str:
        """Запрос недостающих параметров"""
        missing = []
        
        if not params['guest_count']:
            missing.append("количество гостей")
        if not params['event_type']:
            missing.append("формат мероприятия")
        
        return (
            f"🤔 Для точного расчета мне нужно уточнить:\n\n"
            f"• {', '.join(missing).capitalize()}\n\n"
            f"Пример запроса: `Корпоратив 50 человек бюджет 150000`\n\n"
            f"Или просто укажите количество гостей, а я подберу оптимальный вариант!"
        )
    
    def _no_menu_items_response(self, params: Dict[str, Any]) -> str:
        """Ответ при отсутствии подходящих блюд"""
        return (
            f"😔 К сожалению, не удалось подобрать меню для ваших параметров:\n\n"
            f"• Гостей: {params['guest_count']}\n"
            f"• Формат: {params['event_type']}\n"
            + (f"• Бюджет: {params['budget']:,}₽\n" if params['budget'] else "") +
            f"\n🤝 Рекомендации:\n"
            f"• Увеличьте бюджет до {params['guest_count'] * 2000:,}₽\n"
            f"• Или уменьшите количество гостей\n"
            f"• Рассмотрите другой формат мероприятия\n\n"
            f"Напишите новые параметры, и я сделаю расчет!"
        )
    
    def _format_smart_estimate_response(self, estimate: Dict[str, Any], params: Dict[str, Any], user_info: Dict[str, Any]) -> str:
        """Форматирование умного ответа со сметой"""
        event_type = params.get('event_type', 'мероприятие').title()
        guest_count = params['guest_count']
        
        # Персонализация
        greeting = f"Отлично, {user_info.get('first_name', 'Менеджер')}!"
        
        # Основные расчеты
        menu_cost = estimate.get('menu_cost', 0)
        service_cost = estimate.get('service_cost', 0)
        total_cost = estimate.get('total_cost', 0)
        cost_per_guest = estimate.get('cost_per_guest', 0)
        
        # Анализ соответствия бюджету
        budget_analysis = ""
        if params.get('budget'):
            if total_cost <= params['budget']:
                budget_analysis = f"✅ Укладываемся в бюджет {params['budget']:,}₽"
            else:
                over_budget = total_cost - params['budget']
                budget_analysis = f"⚠️ Превышение бюджета на {over_budget:,}₽"
        
        # Рекомендации
        recommendations = self._get_smart_recommendations(estimate, params)
        
        response = f"""
{greeting} Я подготовил для вас оптимальное предложение:

🎯 **{event_type} на {guest_count} человек**

📊 **РАСЧЕТ СТОИМОСТИ:**
• 🍽️ Меню: **{menu_cost:,.0f}₽**
• 👥 Обслуживание: **{service_cost:,.0f}₽**
━━━━━━━━━━━━━━━━━━━━
💰 **ИТОГО: {total_cost:,.0f}₽**
👤 На человека: **{cost_per_guest:,.0f}₽**

{budget_analysis}

📋 **ЧТО ВКЛЮЧЕНО:**
• {estimate.get('menu_items_count', 0)} позиций премиального меню
• Граммовка {estimate.get('weight_per_person', 0):.0f}г на гостя
• Красивая подача и оформление
• Доставка в пределах МКАД

{recommendations}

📞 Готов оформить заказ? Отправьте "Подтверждаю" или задайте уточняющие вопросы!
"""
        
        return response
    
    def _get_smart_recommendations(self, estimate: Dict[str, Any], params: Dict[str, Any]) -> str:
        """Генерация умных рекомендаций"""
        recommendations = []
        
        # Анализируем граммовку
        weight_per_guest = estimate.get('weight_per_person', 0)
        event_type = params.get('event_type', 'фуршет')
        standards = self.service_standards.get(event_type, {})
        
        if weight_per_guest < 200:
            recommendations.append("📌 Рекомендую увеличить количество блюд для сытости гостей")
        
        # Анализируем персонал
        if estimate.get('service_cost', 0) == 0:
            recommendations.append("📌 Рассмотрите вариант с обслуживанием для комфорта гостей")
        
        # Специальные предложения
        if params.get('guest_count', 0) >= 50:
            recommendations.append("🎁 При заказе от 50 человек - комплимент от шефа!")
        
        if recommendations:
            return "\n💡 **РЕКОМЕНДАЦИИ:**\n" + "\n".join(recommendations)
        else:
            return "\n✨ **Это оптимальный вариант для вашего мероприятия!**"
    
    async def _provide_menu_consultation(self, params: Dict[str, Any]) -> str:
        """Консультация по меню"""
        menu_stats = self.menu_service.get_menu_stats()
        
        response = f"""
📋 **Консультация по меню РестДеливери**

У нас {menu_stats['total_items']} позиций в {menu_stats['categories']} категориях!

🌟 **Популярные позиции для {params.get('event_type', 'мероприятий')}:**

**Канапе и брускетты:**
• Канапе с лососем и сливочным сыром
• Брускетта с томатами и моцареллой
• Канапе с ростбифом и трюфельным соусом

**Горячие закуски:**
• Мини-шашлычки из курицы
• Жульен в тарталетках
• Темпура из креветок

**Десерты:**
• Мини-чизкейки
• Макаронс ассорти
• Фруктовые канапе

💡 **Как подобрать меню:**
1. Учитывайте формат мероприятия
2. Соблюдайте баланс мясных/рыбных/овощных блюд
3. Не забудьте про десерты (15-20% от общего количества)

Хотите, я составлю персональное меню для вашего мероприятия?
"""
        
        return response
    
    async def _calculate_pricing(self, params: Dict[str, Any]) -> str:
        """Детальный расчет стоимости"""
        event_type = params.get('event_type', 'фуршет')
        guest_count = params.get('guest_count', 50)
        
        # Получаем стандарты для типа мероприятия
        standards = self.service_standards.get(event_type, self.service_standards['фуршет'])
        
        # Расчеты
        min_price = guest_count * int(standards['price_range'].split('-')[0].replace('₽', ''))
        max_price = guest_count * int(standards['price_range'].split('-')[1].replace('₽', ''))
        
        response = f"""
💰 **Детальный расчет стоимости**

📊 Параметры расчета:
• Формат: **{event_type.title()}**
• Гостей: **{guest_count}**
• Длительность: **{standards['duration']}**

💵 **Стоимость мероприятия:**
• Эконом вариант: **{min_price:,}₽**
• Оптимальный: **{(min_price + max_price) // 2:,}₽**
• Премиум: **{max_price:,}₽**

📋 **Что влияет на цену:**
• Выбор блюд (30-50% от стоимости)
• Количество персонала (20-30%)
• Аренда оборудования (10-20%)
• Логистика и упаковка (5-10%)

🎯 **Рекомендуемый вариант:**
Оптимальный пакет {(min_price + max_price) // 2:,}₽ включает:
• {12 + guest_count // 10} позиций меню
• Граммовка {standards['weight_per_person']}
• {guest_count // standards['staff_ratio']} официантов
• Красивая подача

Хотите точный расчет? Укажите ваши предпочтения!
"""
        
        return response
    
    async def _provide_service_info(self, message: str) -> str:
        """Информация об услугах"""
        return f"""
🎯 **Услуги РестДеливери**

🚚 **Доставка:**
• Бесплатно в пределах МКАД
• За МКАД - от 1500₽
• Точно ко времени

👥 **Персонал:**
• Профессиональные официанты
• Выездные повара
• Банкетные менеджеры
• Униформа и полная экипировка

🪑 **Оборудование:**
• Фуршетные столы
• Коктейльные столы
• Банкетные столы и стулья
• Текстиль и декор

🍽️ **Посуда:**
• Фарфоровая посуда
• Стеклянные бокалы
• Столовые приборы
• Одноразовая посуда (эко)

⏰ **Условия заказа:**
• Минимальный заказ: 10,000₽
• Бронирование: за 24 часа
• Изменения: за 48 часов
• Оплата: предоплата 50%

📞 Нужна конкретная услуга? Спрашивайте!
"""
    
    async def _check_order_status(self, message: str, user_info: Dict[str, Any]) -> str:
        """Проверка статуса заказа"""
        # Здесь должна быть интеграция с системой заказов
        return f"""
📦 **Статус вашего заказа**

Уважаемый {user_info.get('first_name', 'клиент')}!

Для проверки статуса заказа мне нужен номер заказа.
Номер указан в подтверждении (формат: RD-XXXXXX).

Если у вас нет номера, я могу найти заказ по:
• Дате мероприятия
• Вашему телефону
• Адресу доставки

Укажите любую информацию для поиска!
"""
    
    async def _handle_general_inquiry(self, message: str, user_info: Dict[str, Any]) -> str:
        """Обработка общих запросов"""
        # Используем Claude если доступен
        if self.claude_service and self.claude_service.is_available():
            try:
                # Добавляем контекст компании
                context_message = f"""
                Ты - ассистент компании РестДеливери, премиального сервиса доставки банкетных блюд.
                Клиент спрашивает: {message}
                
                Информация о компании:
                - Минимальный заказ: 10,000₽
                - Доставка по Москве бесплатно
                - Заказы принимаем за сутки
                - Специализация: фуршеты, банкеты, корпоративы
                
                Дай полезный и дружелюбный ответ.
                """
                
                response = await self.claude_service.get_response(context_message)
                return response
            except Exception as e:
                logger.error(f"❌ Ошибка Claude: {e}")
        
        # Базовый ответ
        return f"""
👋 Здравствуйте, {user_info.get('first_name', 'дорогой клиент')}!

Я - ваш персональный ассистент в **РестДеливери**.

🎯 **Чем могу помочь:**
• Рассчитать смету для мероприятия
• Подобрать оптимальное меню
• Проконсультировать по услугам
• Ответить на вопросы о доставке

💡 **Быстрый старт:**
Просто напишите, какое мероприятие планируете!

Например: "Корпоратив на 50 человек" или "Фуршет на день рождения"

📞 Готов помочь с организацией вашего идеального мероприятия!
"""
    
    def _get_error_response(self) -> str:
        """Стандартный ответ при ошибке"""
        return (
            "😔 Извините, произошла техническая ошибка.\n\n"
            "Попробуйте:\n"
            "• Переформулировать запрос\n"
            "• Указать основные параметры (количество гостей, формат)\n"
            "• Написать позже\n\n"
            "Или позвоните нам: +7 (495) XXX-XX-XX"
        )


def create_intelligent_assistant(claude_service, menu_service, catering_rules) -> Optional[IntelligentAssistant]:
    """Фабричная функция для создания IntelligentAssistant"""
    try:
        assistant = IntelligentAssistant(claude_service, menu_service, catering_rules)
        logger.info("✅ IntelligentAssistant создан успешно")
        return assistant
    except Exception as e:
        logger.error(f"❌ Ошибка создания IntelligentAssistant: {e}")
        return None


def create_super_ai_agent(claude_service, menu_service, catering_rules) -> Optional[SuperAIAgent]:
    """Фабричная функция для создания SuperAIAgent"""
    try:
        agent = SuperAIAgent(claude_service, menu_service, catering_rules)
        logger.info("🎉 SuperAIAgent создан успешно")
        return agent
    except Exception as e:
        logger.error(f"❌ Ошибка создания SuperAIAgent: {e}")
        return None


# Тестовая функция для проверки
def test_super_ai_agent():
    """Тестирование SuperAIAgent"""
    logger.info("🧪 Тестирование SuperAIAgent...")
    
    # Создаем мок-сервисы для теста
    class MockService:
        def is_available(self):
            return True
        
        def get_menu_stats(self):
            return {'total_items': 100, 'categories': 10}
        
        def get_items_for_event_type(self, *args):
            return [{'name': 'Тест', 'price': 100}] * 10
        
        def calculate_estimate(self, *args):
            return {
                'menu_cost': 50000,
                'service_cost': 10000,
                'total_cost': 60000,
                'cost_per_guest': 1200,
                'weight_per_person': 350,
                'menu_items_count': 10
            }
    
    mock_service = MockService()
    agent = create_super_ai_agent(mock_service, mock_service, mock_service)
    
    if agent:
        logger.info("✅ SuperAIAgent создан для теста")
        
        # Тестируем извлечение параметров
        test_messages = [
            "Корпоратив 50 человек бюджет 150к",
            "Фуршет на 30 персон",
            "Банкет 100 гостей на 5 марта"
        ]
        
        for msg in test_messages:
            params = agent._extract_event_params(msg)
            logger.info(f"Сообщение: {msg}")
            logger.info(f"Параметры: {params}")
    else:
        logger.error("❌ Не удалось создать SuperAIAgent для теста")


if __name__ == "__main__":
    # Запускаем тест при прямом вызове
    test_super_ai_agent()