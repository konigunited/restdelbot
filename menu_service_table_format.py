#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menu Service - АДАПТИРОВАННАЯ версия для табличного формата txt файлов
Формат: Артикул	Наименование	Описание	Вес (г)	Цена (₽)
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class MenuService:
    """Сервис для работы с меню - ВЕРСИЯ ДЛЯ ТАБЛИЧНОГО ФОРМАТА"""
    
    def __init__(self, menu_files_dir: str = "menu_files"):
        self.menu_files_dir = Path(menu_files_dir)
        self.menu_items = []
        self.categories = {}
        self.txt_files = []
        
        # Правила подбора по типам мероприятий
        self.event_rules = {
            'кофе-брейк': {
                'граммовка': (200, 300),
                'категории': {
                    'Канапе': 0.3,
                    'Сэндвичи': 0.3,
                    'Выпечка': 0.2,
                    'Десерты': 0.2
                },
                'позиций_на_человека': 0.15,
                'мин_позиций': 4,
                'макс_позиций': 8
            },
            'фуршет': {
                'граммовка': (300, 500),
                'категории': {
                    'Канапе': 0.25,
                    'Брускетты': 0.15,
                    'Салаты': 0.2,
                    'Горячие закуски': 0.15,
                    'Холодные закуски': 0.15,
                    'Десерты': 0.1
                },
                'позиций_на_человека': 0.2,
                'мин_позиций': 8,
                'макс_позиций': 15
            },
            'банкет': {
                'граммовка': (700, 1200),
                'категории': {
                    'Салаты': 0.2,
                    'Холодные закуски': 0.15,
                    'Горячие закуски': 0.2,
                    'Горячие блюда': 0.25,
                    'Гарниры': 0.1,
                    'Десерты': 0.1
                },
                'позиций_на_человека': 0.25,
                'мин_позиций': 10,
                'макс_позиций': 20
            },
            'корпоратив': {
                'граммовка': (400, 700),
                'категории': {
                    'Канапе': 0.2,
                    'Брускетты': 0.15,
                    'Салаты': 0.15,
                    'Горячие закуски': 0.2,
                    'Холодные закуски': 0.15,
                    'Десерты': 0.15
                },
                'позиций_на_человека': 0.22,
                'мин_позиций': 10,
                'макс_позиций': 18
            }
        }
        
        self.load_menu_from_txt_files()
    
    def load_menu_from_txt_files(self):
        """Загрузка меню из txt файлов табличного формата"""
        try:
            logger.info(f"🔍 Поиск txt файлов в папке: {self.menu_files_dir}")
            logger.info(f"📁 Абсолютный путь: {self.menu_files_dir.absolute()}")
            
            if not self.menu_files_dir.exists():
                logger.warning(f"⚠️ Папка {self.menu_files_dir} не найдена")
                self._create_menu_files_directory()
                return
            
            # Ищем все txt файлы
            txt_files = list(self.menu_files_dir.glob("*.txt"))
            
            logger.info(f"📂 Содержимое папки {self.menu_files_dir}:")
            for item in self.menu_files_dir.iterdir():
                logger.info(f"  - {item.name} ({'файл' if item.is_file() else 'папка'})")
            
            if not txt_files:
                logger.warning(f"⚠️ Txt файлы не найдены в {self.menu_files_dir}")
                self._create_sample_txt_files()
                txt_files = list(self.menu_files_dir.glob("*.txt"))
            
            self.txt_files = txt_files
            logger.info(f"📁 Найдено txt файлов: {len(txt_files)}")
            for txt_file in txt_files:
                logger.info(f"  - {txt_file.name}")
            
            # Загружаем данные из каждого файла
            total_items = 0
            for txt_file in txt_files:
                logger.info(f"📄 Обрабатываем файл: {txt_file.name}")
                items_count = self._load_menu_from_txt_file(txt_file)
                total_items += items_count
                logger.info(f"📄 {txt_file.name}: загружено {items_count} позиций")
            
            # Группируем по категориям
            self._categorize_items()
            
            # ДОБАВЛЯЕМ ОТЛАДОЧНУЮ ИНФОРМАЦИЮ О КАТЕГОРИЯХ
            logger.info(f"📂 Созданные категории:")
            for category, items in self.categories.items():
                logger.info(f"  - {category}: {len(items)} позиций")
            
            logger.info(f"✅ Всего загружено {total_items} позиций из {len(txt_files)} файлов")
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки txt файлов: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self._create_default_menu()
    
    def _load_menu_from_txt_file(self, txt_file: Path) -> int:
        """Загрузка меню из одного txt файла табличного формата"""
        try:
            logger.info(f"📖 Читаем файл: {txt_file}")
            with open(txt_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                logger.warning(f"⚠️ Файл {txt_file.name} пустой")
                return 0
            
            logger.info(f"📄 В файле {txt_file.name} строк: {len(lines)}")
            
            # Определяем категорию по имени файла
            category = self._determine_category_from_filename(txt_file.name)
            logger.info(f"📂 Категория для {txt_file.name}: {category}")
            
            # Парсим содержимое (пропускаем заголовок)
            items = self._parse_table_content(lines, category, txt_file.name)
            
            logger.info(f"✅ Из файла {txt_file.name} извлечено {len(items)} позиций")
            for item in items[:3]:  # Показываем первые 3 для отладки
                logger.info(f"   - {item['article']}: {item['name']} ({item['price']}₽)")
            
            # Добавляем к общему списку
            self.menu_items.extend(items)
            
            return len(items)
            
        except Exception as e:
            logger.error(f"❌ Ошибка чтения файла {txt_file}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return 0
    
    def _determine_category_from_filename(self, filename: str) -> str:
        """Определение категории по имени файла"""
        filename_lower = filename.lower()
        
        category_mapping = {
            'канапе': 'Канапе',
            'брускетт': 'Брускетты',
            'салат': 'Салаты',
            'банкет': 'Банкетные блюда',
            'горячие': 'Горячие закуски',
            'холодные': 'Холодные закуски',
            'десерт': 'Десерты',
            'сэндвич': 'Сэндвичи',
            'выпечка': 'Выпечка',
            'напитки': 'Напитки',
            'гарнир': 'Гарниры',
            'сет': 'Готовые сеты',
            'меню': 'Основное меню'
        }
        
        for keyword, category in category_mapping.items():
            if keyword in filename_lower:
                return category
        
        # Если не определили, используем имя файла как категорию
        return filename.replace('.txt', '').replace('_', ' ').title()
    
    def _parse_table_content(self, lines: List[str], category: str, filename: str) -> List[Dict[str, Any]]:
        """Парсинг табличного содержимого"""
        items = []
        
        logger.info(f"🔍 Парсинг файла {filename}, строк: {len(lines)}")
        
        # Проверяем заголовок (первая строка)
        if lines and lines[0].strip():
            header = lines[0].strip()
            logger.info(f"📋 Заголовок файла {filename}: {header}")
            
            # Проверяем что это табличный формат
            if '\t' in header or 'Артикул' in header:
                logger.info(f"✅ Обнаружен табличный формат в {filename}")
                # Пропускаем заголовок
                data_lines = lines[1:]
            else:
                logger.warning(f"⚠️ Заголовок не найден в {filename}, обрабатываем все строки")
                # Если заголовка нет, обрабатываем все строки
                data_lines = lines
        else:
            data_lines = lines
        
        logger.info(f"📄 Строк данных для обработки: {len(data_lines)}")
        
        # Обрабатываем строки данных
        processed_count = 0
        for line_num, line in enumerate(data_lines, 2):  # Начинаем с 2, так как 1 - заголовок
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            logger.debug(f"🔍 Обрабатываем строку {line_num}: {line[:100]}...")
            
            try:
                item = self._parse_table_line(line, category, line_num, filename)
                if item:
                    items.append(item)
                    processed_count += 1
                    logger.debug(f"✅ Строка {line_num} обработана: {item['name']}")
                else:
                    logger.warning(f"⚠️ Строка {line_num} не обработана")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка парсинга строки {line_num} в {filename}: {e}")
                logger.warning(f"Строка: {line}")
        
        logger.info(f"✅ Из {filename} успешно обработано {processed_count} из {len(data_lines)} строк")
        
        return items
    
    def _parse_table_line(self, line: str, category: str, line_num: int, filename: str) -> Optional[Dict[str, Any]]:
        """Парсинг одной строки табличного формата"""
        
        # Разделяем по табуляции
        parts = line.split('\t')
        
        logger.debug(f"🔍 Строка {line_num}: найдено {len(parts)} колонок")
        logger.debug(f"    Колонки: {[p[:30] + '...' if len(p) > 30 else p for p in parts]}")
        
        if len(parts) >= 5:
            # Полный формат: Артикул	Наименование	Описание	Вес (г)	Цена (₽)
            try:
                article = parts[0].strip()
                name = parts[1].strip()
                description = parts[2].strip()
                weight_str = parts[3].strip()
                price_str = parts[4].strip()
                
                logger.debug(f"    Артикул: {article}")
                logger.debug(f"    Название: {name}")
                logger.debug(f"    Вес: {weight_str}")
                logger.debug(f"    Цена: {price_str}")
                
                # Извлекаем числовые значения
                weight = self._extract_number(weight_str)
                price = self._extract_number(price_str)
                
                logger.debug(f"    Извлечено - Вес: {weight}г, Цена: {price}₽")
                
                if not name:
                    logger.warning(f"⚠️ Пустое название в строке {line_num}")
                    return None
                
                # Создаем ID на основе артикула
                item_id = self._create_id_from_article(article, line_num)
                
                logger.debug(f"    Создан ID: {item_id}")
                
                item = {
                    'id': item_id,
                    'article': article,
                    'name': name,
                    'description': description,
                    'category': category,
                    'price': max(1, price),
                    'weight': max(1, weight),
                    'unit': 'шт',
                    'source_file': filename
                }
                
                logger.debug(f"    ✅ Создан элемент: {item['name']} (ID: {item['id']})")
                return item
                
            except Exception as e:
                logger.error(f"❌ Ошибка обработки полного формата в строке {line_num}: {e}")
                logger.error(f"    Строка: {line}")
                return None
        
        elif len(parts) >= 3:
            # Сокращенный формат: может быть без описания
            try:
                article = parts[0].strip()
                name = parts[1].strip()
                weight_str = parts[2].strip() if len(parts) > 2 else "100"
                price_str = parts[3].strip() if len(parts) > 3 else "500"
                
                weight = self._extract_number(weight_str)
                price = self._extract_number(price_str)
                
                item_id = self._create_id_from_article(article, line_num)
                
                logger.debug(f"    ✅ Сокращенный формат: {name} (ID: {item_id})")
                
                return {
                    'id': item_id,
                    'article': article,
                    'name': name,
                    'description': '',
                    'category': category,
                    'price': max(1, price),
                    'weight': max(1, weight),
                    'unit': 'шт',
                    'source_file': filename
                }
                
            except Exception as e:
                logger.error(f"❌ Ошибка обработки сокращенного формата в строке {line_num}: {e}")
                return None
        
        else:
            logger.warning(f"⚠️ Недостаточно данных в строке {line_num}: {len(parts)} колонок (нужно минимум 3)")
            logger.warning(f"    Содержимое: {parts}")
            return None
    
    def _create_id_from_article(self, article: str, line_num: int) -> int:
        """Создание ID на основе артикула"""
        if article:
            # Извлекаем числовую часть из артикула
            numbers = re.findall(r'\d+', article)
            if numbers:
                # Используем первое число из артикула
                base_id = int(numbers[0])
                # Добавляем смещение чтобы избежать конфликтов
                return base_id + (hash(article) % 1000)
            else:
                # Если нет чисел в артикуле, генерируем на основе хеша
                return abs(hash(article)) % 10000 + 1000
        else:
            # Если артикул пустой, используем номер строки
            return line_num + 10000
    
    def _extract_number(self, text: str) -> int:
        """Извлечение числа из текста"""
        if not text:
            return 0
        
        # Убираем все кроме цифр
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return 0
    
    def _create_menu_files_directory(self):
        """Создание папки menu_files"""
        try:
            self.menu_files_dir.mkdir(exist_ok=True)
            logger.info(f"📁 Создана папка: {self.menu_files_dir}")
            self._create_sample_txt_files()
        except Exception as e:
            logger.error(f"❌ Ошибка создания папки: {e}")
    
    def _create_sample_txt_files(self):
        """Создание примеров txt файлов в табличном формате"""
        sample_files = {
            'банкетное_меню.txt': """Артикул	Наименование	Описание	Вес (г)	Цена (₽)
B001	Говяжий бок на подушке из картофельно-тыквенного пюре	Нежная говядина на воздушном пюре из картофеля и тыквы	250	1150
B002	Запеченная скумбрия с баклажанами и кунжутным соусом	Ароматная рыба с овощами под изысканным азиатским соусом	270	1100
B003	Медальоны из говядины с сезонными грибами	Сочные медальоны премиальной говядины с лесными грибами	250	1350
B004	Радужная форель с пюре васаби, биск, тартар из огурцов	Деликатесная форель с японскими акцентами и свежим тартаром	260	1600
B005	Телячьи щечки с картофельно-сельдереевым кремом и грибным соусом	Томленые щечки молодой телятины в ароматном грибном соусе	250	1200""",
            
            'канапе_меню.txt': """Артикул	Наименование	Описание	Вес (г)	Цена (₽)
K001	Канапе с лососем и сливочным сыром	Изысканное канапе с копченым лососем на ржаном хлебе	30	180
K002	Канапе с ростбифом и трюфельным соусом	Премиальный ростбиф с ароматным трюфельным соусом	35	200
K003	Канапе с сыром и виноградом	Нежный сыр бри с сочным виноградом на тосте	25	150
K004	Канапе с креветкой и авокадо	Тигровая креветка с кремовым авокадо и лаймом	35	220
K005	Канапе овощное	Свежие овощи с творожным муссом на цельнозерновом хлебе	30	120""",
            
            'салаты_меню.txt': """Артикул	Наименование	Описание	Вес (г)	Цена (₽)
S001	Салат Цезарь с курицей	Классический салат с куриной грудкой гриль и пармезаном	200	450
S002	Салат Греческий	Традиционный греческий салат с сыром фета и маслинами	180	380
S003	Салат с креветками	Микс салатов с тигровыми креветками и авокадо	190	520
S004	Салат Оливье	Традиционный русский салат с отварными овощами	200	320
S005	Салат мимоза	Слоеный салат с рыбными консервами и яйцами	180	280""",
            
            'горячие_закуски.txt': """Артикул	Наименование	Описание	Вес (г)	Цена (₽)
H001	Мини-шашлычок из курицы	Нежные кусочки куриного филе на шпажках	50	180
H002	Мини-шашлычок из свинины	Сочная свинина маринованная в специях	50	200
H003	Жульен в тарталетке	Классический жульен с грибами в хрустящей тарталетке	40	150
H004	Темпура из креветок	Креветки в легком кляре темпура с соусом	60	280
H005	Куриные крылышки BBQ	Ароматные крылышки в соусе барбекю	80	160""",
            
            'десерты_меню.txt': """Артикул	Наименование	Описание	Вес (г)	Цена (₽)
D001	Мини-чизкейк	Нежный чизкейк с ягодным топпингом	80	180
D002	Макаронс	Французские миндальные пирожные ассорти	20	120
D003	Профитроли	Заварные пирожные с кремом и шоколадом	60	150
D004	Фруктовое канапе	Свежие фрукты на шпажках с медовым соусом	50	100
D005	Тирамису порционный	Классический итальянский десерт в порционной подаче	100	220"""
        }
        
        try:
            for filename, content in sample_files.items():
                file_path = self.menu_files_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"📄 Создан файл: {filename}")
        except Exception as e:
            logger.error(f"❌ Ошибка создания примеров: {e}")
    
    def _categorize_items(self):
        """Группировка блюд по категориям"""
        self.categories = {}
        for item in self.menu_items:
            category = item.get('category', 'Другое')
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(item)
    
    def _create_default_menu(self):
        """Создание меню по умолчанию если txt файлы недоступны"""
        self.menu_items = [
            {"id": 1001, "article": "B001", "name": "Говяжий бок на подушке из картофельно-тыквенного пюре", "category": "Банкетные блюда", "price": 1150, "weight": 250, "description": "Нежная говядина на воздушном пюре", "unit": "шт"},
            {"id": 1002, "article": "K001", "name": "Канапе с лососем и сливочным сыром", "category": "Канапе", "price": 180, "weight": 30, "description": "Изысканное канапе с копченым лососем", "unit": "шт"},
            {"id": 1003, "article": "S001", "name": "Салат Цезарь с курицей", "category": "Салаты", "price": 450, "weight": 200, "description": "Классический салат с куриной грудкой", "unit": "порция"},
            {"id": 1004, "article": "H001", "name": "Мини-шашлычок из курицы", "category": "Горячие закуски", "price": 180, "weight": 50, "description": "Нежные кусочки куриного филе", "unit": "шт"},
            {"id": 1005, "article": "D001", "name": "Мини-чизкейк", "category": "Десерты", "price": 180, "weight": 80, "description": "Нежный чизкейк с ягодным топпингом", "unit": "шт"}
        ]
        
        self._categorize_items()
        logger.info(f"✅ Создано меню по умолчанию: {len(self.menu_items)} позиций")
    
    def get_items_for_event_type(self, event_type: str, guest_count: int, budget_per_person: Optional[float] = None) -> List[Dict[str, Any]]:
        """Подбор блюд для типа мероприятия с исправленной обработкой ID"""
        logger.info(f"🔍 Подбор меню: {event_type}, {guest_count} гостей, бюджет/чел: {budget_per_person}")
        
        # ОТЛАДОЧНАЯ ИНФОРМАЦИЯ
        logger.info(f"📂 Доступные категории в меню: {list(self.categories.keys())}")
        logger.info(f"📊 Всего позиций в меню: {len(self.menu_items)}")
        
        event_type = event_type.lower()
        
        # Упрощаем тип мероприятия
        if 'банкет' in event_type:
            event_type = 'банкет'
        elif 'фуршет' in event_type:
            event_type = 'фуршет'
        elif 'кофе' in event_type or 'брейк' in event_type:
            event_type = 'кофе-брейк'
        elif 'корпоратив' in event_type:
            event_type = 'корпоратив'
        
        if event_type not in self.event_rules:
            logger.warning(f"⚠️ Неизвестный тип мероприятия: {event_type}, используем фуршет")
            event_type = 'фуршет'
        
        rules = self.event_rules[event_type]
        selected_items = []
        
        # Определяем целевую граммовку
        min_weight, max_weight = rules['граммовка']
        if budget_per_person:
            if budget_per_person < 2000:
                target_weight = min_weight
            elif budget_per_person > 5000:
                target_weight = max_weight
            else:
                ratio = (budget_per_person - 2000) / 3000
                target_weight = min_weight + (max_weight - min_weight) * ratio
        else:
            target_weight = (min_weight + max_weight) / 2
        
        logger.info(f"📊 Целевая граммовка: {target_weight}г/человека")
        
        # Определяем количество позиций
        positions_count = max(
            rules['мин_позиций'],
            min(
                int(guest_count * rules['позиций_на_человека']),
                rules['макс_позиций']
            )
        )
        
        logger.info(f"📋 Целевое количество позиций: {positions_count}")
        
        # ИСПРАВЛЕННАЯ ЛОГИКА: работаем с реальными категориями
        available_categories = list(self.categories.keys())
        logger.info(f"🔍 Реальные категории: {available_categories}")
        
        if not available_categories:
            logger.error("❌ Нет доступных категорий в меню!")
            return []
        
        # Подбираем блюда из доступных категорий
        items_per_category = max(1, positions_count // len(available_categories))
        remainder = positions_count % len(available_categories)
        
        logger.info(f"📋 Позиций на категорию: {items_per_category}, остаток: {remainder}")
        
        for i, category in enumerate(available_categories):
            # Количество позиций для этой категории
            category_positions = items_per_category
            if i < remainder:  # Распределяем остаток
                category_positions += 1
            
            logger.info(f"📂 Обрабатываем категорию: {category} ({category_positions} позиций)")
            
            # Фильтруем по бюджету если указан
            available_items = self.categories[category]
            if budget_per_person:
                max_item_price = budget_per_person * 2  # Простое ограничение
                available_items = [
                    item for item in available_items 
                    if item.get('price', 0) <= max_item_price
                ]
                logger.info(f"   После фильтрации по бюджету: {len(available_items)} позиций")
            
            if not available_items:
                logger.warning(f"⚠️ Нет доступных блюд в категории {category}")
                continue
            
            # Сортируем по цене (сначала дешевые)
            available_items.sort(key=lambda x: x.get('price', 0))
            
            # Выбираем позиции
            for item in available_items[:category_positions]:
                # Проверяем ID - теперь должен быть всегда
                if 'id' not in item or not item['id']:
                    logger.error(f"❌ Отсутствует ID у блюда: {item.get('name', 'Unknown')}")
                    # Генерируем ID как резерв
                    item['id'] = len(selected_items) + 1000 + hash(item.get('name', '')) % 1000
                
                # Добавляем количество
                item_with_quantity = item.copy()
                item_with_quantity['quantity'] = max(1, guest_count // 10)
                item_with_quantity['total_weight'] = item_with_quantity['quantity'] * item.get('weight', 0)
                selected_items.append(item_with_quantity)
                
                logger.info(f"✅ Добавлено: {item['name']} (ID: {item['id']}) x{item_with_quantity['quantity']}")
        
        logger.info(f"✅ Подобрано {len(selected_items)} позиций")
        
        # Проверяем если ничего не подобрано
        if not selected_items:
            logger.warning("⚠️ Не удалось подобрать блюда, добавляем из всего меню")
            # Берем просто первые позиции из всего меню
            for item in self.menu_items[:min(positions_count, len(self.menu_items))]:
                if 'id' not in item or not item['id']:
                    item['id'] = len(selected_items) + 1000 + hash(item.get('name', '')) % 1000
                
                item_with_quantity = item.copy()
                item_with_quantity['quantity'] = max(1, guest_count // 10)
                item_with_quantity['total_weight'] = item_with_quantity['quantity'] * item.get('weight', 0)
                selected_items.append(item_with_quantity)
                
                logger.info(f"🔄 Добавлено из общего меню: {item['name']} (ID: {item['id']})")
        
        return selected_items
    
    def get_menu_stats(self) -> Dict[str, Any]:
        """Получение статистики меню"""
        return {
            'total_items': len(self.menu_items),
            'categories': len(self.categories),
            'categories_detail': {
                cat: len(items) for cat, items in self.categories.items()
            },
            'txt_files_count': len(self.txt_files),
            'files_list': [f.name for f in self.txt_files],
            'new_items': 0,
            'popular_items': 10
        }
    
    def get_available_categories(self) -> List[str]:
        """Получение списка доступных категорий"""
        return list(self.categories.keys())
    
    def search_items(self, query: str) -> List[Dict[str, Any]]:
        """Поиск блюд по названию"""
        query_lower = query.lower()
        results = []
        
        for item in self.menu_items:
            if (query_lower in item.get('name', '').lower() or 
                query_lower in item.get('description', '').lower() or
                query_lower in item.get('article', '').lower()):
                results.append(item)
        
        return results
    
    def get_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Получение блюда по ID"""
        for item in self.menu_items:
            if item.get('id') == item_id:
                return item
        return None
    
    def get_item_by_article(self, article: str) -> Optional[Dict[str, Any]]:
        """Получение блюда по артикулу"""
        for item in self.menu_items:
            if item.get('article', '').upper() == article.upper():
                return item
        return None
    
    def reload_menu(self):
        """Перезагрузка меню из txt файлов"""
        self.menu_items = []
        self.categories = {}
        self.load_menu_from_txt_files()
        logger.info("🔄 Меню перезагружено из txt файлов")
    
    def get_debug_info(self) -> str:
        """Получение отладочной информации о состоянии меню"""
        debug_info = []
        
        debug_info.append("🔍 ОТЛАДОЧНАЯ ИНФОРМАЦИЯ MenuService")
        debug_info.append("=" * 50)
        
        # Информация о папке
        debug_info.append(f"📁 Папка меню: {self.menu_files_dir}")
        debug_info.append(f"📁 Абсолютный путь: {self.menu_files_dir.absolute()}")
        debug_info.append(f"📁 Папка существует: {self.menu_files_dir.exists()}")
        
        if self.menu_files_dir.exists():
            # Содержимое папки
            debug_info.append("\n📂 Содержимое папки:")
            for item in self.menu_files_dir.iterdir():
                file_type = "📄 файл" if item.is_file() else "📁 папка"
                debug_info.append(f"  {file_type}: {item.name}")
        
        # Информация о загруженных файлах
        debug_info.append(f"\n📄 TXT файлов найдено: {len(self.txt_files)}")
        for txt_file in self.txt_files:
            debug_info.append(f"  - {txt_file.name}")
        
        # Информация о меню
        debug_info.append(f"\n🍽️ Всего позиций в меню: {len(self.menu_items)}")
        debug_info.append(f"📂 Категорий: {len(self.categories)}")
        
        # Детали по категориям
        if self.categories:
            debug_info.append("\n📂 Категории и количество позиций:")
            for category, items in self.categories.items():
                debug_info.append(f"  - {category}: {len(items)} позиций")
        else:
            debug_info.append("\n❌ Категории НЕ СОЗДАНЫ!")
        
        # Примеры блюд
        if self.menu_items:
            debug_info.append("\n🍽️ Первые 5 позиций:")
            for i, item in enumerate(self.menu_items[:5], 1):
                debug_info.append(f"  {i}. ID:{item.get('id', 'N/A')} | {item.get('article', 'N/A')} | {item.get('name', 'N/A')} | {item.get('category', 'N/A')}")
        else:
            debug_info.append("\n❌ ПОЗИЦИИ НЕ ЗАГРУЖЕНЫ!")
        
        debug_info.append("\n" + "=" * 50)
        
        return "\n".join(debug_info)
    
    def force_reload_with_debug(self):
        """Принудительная перезагрузка с отладкой"""
        logger.info("🔄 ПРИНУДИТЕЛЬНАЯ ПЕРЕЗАГРУЗКА С ОТЛАДКОЙ")
        
        # Очищаем текущие данные
        self.menu_items = []
        self.categories = {}
        self.txt_files = []
        
        # Перезагружаем с подробным логированием
        self.load_menu_from_txt_files()
        
        # Выводим итоговую информацию
        logger.info("📊 ИТОГОВАЯ СТАТИСТИКА:")
        logger.info(f"  - Файлов: {len(self.txt_files)}")
        logger.info(f"  - Позиций: {len(self.menu_items)}")
        logger.info(f"  - Категорий: {len(self.categories)}")
        
        return self.get_debug_info()
    def _add_beverages_to_coffee_break(self, selected_items, guest_count):
        """Add mandatory beverages for coffee break"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Checking beverages for coffee break...")
        
        # Check if beverages already exist
        has_coffee = any('кофе' in item.get('name', '').lower() for item in selected_items)
        has_tea = any('чай' in item.get('name', '').lower() for item in selected_items)
        
        if has_coffee and has_tea:
            return selected_items
        
        # Find beverages category
        beverages = []
        for category_name, items in self.categories.items():
            if any(keyword in category_name.lower() for keyword in ['напитки', 'beverages', 'кофе', 'чай']):
                beverages = items
                logger.info(f"Found beverages category: {category_name}")
                break
        
        # Add coffee if missing
        if beverages and not has_coffee:
            for item in beverages:
                if 'кофе' in item.get('name', '').lower():
                    coffee_item = item.copy()
                    coffee_item['quantity'] = guest_count
                    coffee_item['total_weight'] = guest_count * item.get('weight', 200)
                    selected_items.append(coffee_item)
                    logger.info(f"Added coffee: {item['name']}")
                    break
        
        # Add tea if missing
        if beverages and not has_tea:
            for item in beverages:
                if 'чай' in item.get('name', '').lower():
                    tea_item = item.copy()
                    tea_item['quantity'] = guest_count // 2
                    tea_item['total_weight'] = (guest_count // 2) * item.get('weight', 200)
                    selected_items.append(tea_item)
                    logger.info(f"Added tea: {item['name']}")
                    break
        
        return selected_items
