#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EventBot AI v2.1 - ИСПРАВЛЕННАЯ ВЕРСИЯ с menu_files и исправленными ID
Telegram бот для автоматизации банкетных смет
"""

import os
import sys
import asyncio
import logging
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import re

# Настройка путей - ИСПРАВЛЕНО для menu_files
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'services'))
PROJECT_DIR = Path(__file__).parent.absolute()
os.chdir(PROJECT_DIR)

# Путь к папке menu_files
MENU_FILES_DIR = PROJECT_DIR / "menu_files"

# Настройка логирования
def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler('logs/eventbot.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger(__name__)

# Проверка зависимостей
def check_dependencies():
    missing_deps = []
    
    try:
        from telegram import Update
        from telegram.ext import Application
    except ImportError:
        missing_deps.append("python-telegram-bot")
    
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing_deps.append("python-dotenv")
    
    if missing_deps:
        logger.error(f"❌ Отсутствуют зависимости: {', '.join(missing_deps)}")
        logger.error("Установите их командой: pip install " + " ".join(missing_deps))
        sys.exit(1)

check_dependencies()

from dotenv import load_dotenv
load_dotenv()

def check_env_variables():
    """Проверка наличия необходимых переменных окружения"""
    required_vars = ['TELEGRAM_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        logger.error("Создайте файл .env и добавьте необходимые переменные")
        sys.exit(1)

check_env_variables()

# Импорт сервисов с исправленной логикой загрузки меню
try:
    # Создаем кастомный MenuService для табличного формата txt файлов
    try:
        from menu_service_table_format import MenuService  # Табличный формат в корне
    except ImportError:
        from services.menu_service_table_format import MenuService  # Табличный формат в services
    
    from services.claude_api_service import EnhancedClaudeAPIService, create_enhanced_claude_service
    from services.excel_estimate_generator import ExcelEstimateGenerator
    from services.catering_rules_service import CateringRulesService
    from services.client_database import ClientDatabase
except ImportError as e:
    logger.error(f"❌ Ошибка импорта сервисов: {e}")
    logger.error("Убедитесь, что все файлы находятся в правильных папках")
    sys.exit(1)

# Импорт SuperAIAgent
SUPER_AGENT_AVAILABLE = False
super_ai_agent = None
intelligent_assistant = None

try:
    from services.intelligent_manager_assistant import (
        SuperAIAgent, 
        create_super_ai_agent,
        create_intelligent_assistant
    )
    SUPER_AGENT_AVAILABLE = True
    logger.info("✅ SuperAIAgent успешно импортирован!")
except ImportError:
    try:
        from intelligent_manager_assistant import (
            SuperAIAgent, 
            create_super_ai_agent,
            create_intelligent_assistant
        )
        SUPER_AGENT_AVAILABLE = True
        logger.info("✅ SuperAIAgent импортирован из корневой папки!")
    except ImportError as e:
        logger.warning(f"⚠️ SuperAIAgent недоступен: {e}")

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

class EventBotAI:
    """
    EventBot AI v2.1 - ИСПРАВЛЕННАЯ ВЕРСИЯ с menu_files
    """
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.manager_ids = self._parse_manager_ids()
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        if not self.token:
            logger.error("❌ TELEGRAM_TOKEN не настроен!")
            sys.exit(1)
        
        # Инициализация сервисов
        self._initialize_services()
        self._log_startup_stats()
        
    def _parse_manager_ids(self) -> list:
        """Парсинг ID менеджеров из переменной окружения"""
        manager_ids_str = os.getenv('MANAGER_IDS', '')
        if not manager_ids_str:
            logger.warning("⚠️ MANAGER_IDS не настроен - доступ для всех")
            return []
        
        try:
            return [int(id.strip()) for id in manager_ids_str.split(',') if id.strip()]
        except ValueError:
            logger.error("❌ Некорректный формат MANAGER_IDS")
            return []
    
    def _initialize_services(self):
        """Инициализация всех сервисов с menu_files"""
        try:
            logger.info("🔧 Инициализация сервисов EventBot...")
            
            # ИСПРАВЛЕНО: MenuService с menu_files
            logger.info(f"📁 Инициализация MenuService с папкой: {MENU_FILES_DIR}")
            self.menu_service = MenuService(str(MENU_FILES_DIR))
            
            # Claude API
            claude_api_key = os.getenv("CLAUDE_API_KEY")
            if claude_api_key:
                self.claude_service = create_enhanced_claude_service(claude_api_key, "data")
                self.claude_service.load_menu_data()
                logger.info("✅ Claude API инициализирован")
            else:
                logger.warning("⚠️ CLAUDE_API_KEY не найден - Claude недоступен")
                self.claude_service = None
            
            self.excel_generator = ExcelEstimateGenerator()
            self.catering_rules = CateringRulesService()
            self.client_db = ClientDatabase()
            
            # ИИ-помощники
            logger.info("🤖 Инициализация ИИ-помощников...")
            
            self.intelligent_assistant = None
            self.super_ai_agent = None
            
            if SUPER_AGENT_AVAILABLE and self.claude_service:
                try:
                    self.intelligent_assistant = create_intelligent_assistant(
                        self.claude_service, 
                        self.menu_service, 
                        self.catering_rules
                    )
                    if self.intelligent_assistant:
                        logger.info("✅ Intelligent Assistant создан")
                    
                    self.super_ai_agent = create_super_ai_agent(
                        self.claude_service, 
                        self.menu_service, 
                        self.catering_rules
                    )
                    
                    if self.super_ai_agent:
                        self.super_ai_agent.excel_generator = self.excel_generator
                        logger.info("🎉 СУПЕР ИИ-АГЕНТ АКТИВИРОВАН!")
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка создания ИИ-агентов: {e}")
                    self.intelligent_assistant = None
                    self.super_ai_agent = None
            else:
                if not SUPER_AGENT_AVAILABLE:
                    logger.warning("⚠️ SuperAIAgent недоступен")
                if not self.claude_service:
                    logger.warning("⚠️ Claude API недоступен")
            
            logger.info("✅ Все сервисы инициализированы")
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка инициализации: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def _log_startup_stats(self):
        """Логирование статистики при запуске"""
        try:
            menu_stats = self.menu_service.get_menu_stats()
            
            logger.info("=" * 60)
            logger.info("🤖 EventBot AI v2.1 - ТАБЛИЧНЫЙ ФОРМАТ TXT")
            logger.info("=" * 60)
            logger.info(f"📁 Папка меню: {MENU_FILES_DIR}")
            logger.info(f"📄 TXT файлов: {menu_stats.get('txt_files_count', 0)}")
            logger.info(f"📊 Позиций меню: {menu_stats['total_items']}")
            logger.info(f"📂 Категорий: {menu_stats['categories']}")
            logger.info(f"📋 Формат: Артикул→Название→Описание→Вес→Цена")
            logger.info(f"👥 Менеджеров: {len(self.manager_ids) if self.manager_ids else 'Все'}")
            logger.info(f"🤖 Claude AI: {'✅ Активен' if self.claude_service and self.claude_service.is_available() else '❌ Недоступен'}")
            logger.info(f"🧠 SuperAI: {'✅ Активен' if self.super_ai_agent else '❌ Недоступен'}")
            logger.info(f"📊 Excel: ✅ Готов")
            logger.info(f"🧮 Калькулятор: ✅ Исправленные расчеты")
            logger.info(f"🚀 Режим: {'🔧 Debug' if self.debug_mode else '⚡ Production'}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка статистики: {e}")
    
    def _check_access(self, user_id: int) -> bool:
        """Проверка доступа пользователя"""
        if not self.manager_ids:
            return True
        return user_id in self.manager_ids
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        first_name = update.effective_user.first_name or "Пользователь"
        
        logger.info(f"👤 Команда /start от {username} ({first_name}, ID: {user_id})")
        
        if not self._check_access(user_id):
            await update.message.reply_text(
                "❌ **Доступ запрещен**\n\n"
                "Этот бот предназначен только для менеджеров РестДеливери.\n"
                "Для получения доступа обратитесь к администратору.",
                parse_mode='Markdown'
            )
            return
        
        menu_stats = self.menu_service.get_menu_stats()
        claude_status = "🟢 Активен" if self.claude_service and self.claude_service.is_available() else "🔴 Недоступен"
        super_ai_status = "🟢 Активен" if self.super_ai_agent else "🔴 Недоступен"
        
        welcome_message = f"""
🤖 **EventBot AI v2.1 - ТАБЛИЧНЫЙ ФОРМАТ ГОТОВ!**

Привет, {first_name}! 👋

✨ *Интеллектуальная система создания банкетных смет*

📊 **Статус системы:**
• 📁 Папка меню: **{MENU_FILES_DIR.name}**
• 📄 TXT файлов: **{menu_stats.get('txt_files_count', 0)}**
• 📊 Позиций меню: **{menu_stats['total_items']}**
• 📂 Категорий: **{menu_stats['categories']}**  
• 📋 Формат: **Артикул→Название→Описание→Вес→Цена**
• 🤖 Claude AI: **{claude_status}**
• 🧠 SuperAI: **{super_ai_status}**
• 📊 Excel: **🟢 Готов**

🎯 **Как создать смету:**
Просто отправьте описание мероприятия, например:
• `Корпоратив 50 человек бюджет 150к`
• `Банкет 30 человек` 
• `Фуршет 100 человек бюджет 200к`
• `Кофе-брейк 25 человек`

💡 **Особенности v2.1:**
• ✅ Табличный формат TXT (TSV)
• ✅ Автоматическое создание ID из артикулов
• ✅ Поддержка описаний блюд
• ✅ Исправлены все ошибки с ID

📞 **РестДеливери** - Премиальное банкетное обслуживание
        """
        
        keyboard = [
            [InlineKeyboardButton("📋 Каталог меню", callback_data="menu"),
             InlineKeyboardButton("💰 Калькулятор", callback_data="calculator")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats"), 
             InlineKeyboardButton("❓ Справка", callback_data="help")],
            [InlineKeyboardButton("🔄 Перезагрузить меню", callback_data="reload_menu"),
             InlineKeyboardButton("🔍 Диагностика", callback_data="debug_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопок"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not self._check_access(user_id):
            await query.edit_message_text("❌ Доступ запрещен.")
            return
        
        if query.data == "menu":
            await self.show_menu_catalog(query)
        elif query.data == "stats":
            await self.show_statistics(query)
        elif query.data == "help":
            await self.show_help(query)
        elif query.data == "calculator":
            await self.show_calculator(query)
        elif query.data == "reload_menu":
            await self.reload_menu_callback(query)
        elif query.data == "debug_menu":
            await self.debug_menu_callback(query)
        elif query.data == "force_reload":
            await self.force_reload_callback(query)
        elif query.data == "back_to_start":
            # Создаем фиктивный объект для вызова start_command
            fake_update = type('obj', (object,), {
                'effective_user': query.from_user,
                'message': type('obj', (object,), {
                    'reply_text': query.edit_message_text
                })()
            })()
            await self.start_command(fake_update, None)
    
    async def reload_menu_callback(self, query):
        """Перезагрузка меню из txt файлов"""
        try:
            await query.edit_message_text("🔄 Перезагружаю меню из txt файлов...")
            
            # Перезагружаем меню
            self.menu_service.reload_menu()
            
            # Получаем новую статистику
            menu_stats = self.menu_service.get_menu_stats()
            
            response = f"""
✅ **Меню успешно перезагружено!**

📊 **Новая статистика:**
• 📁 Папка: {MENU_FILES_DIR}
• 📄 TXT файлов: {menu_stats.get('txt_files_count', 0)}
• 📋 Позиций: {menu_stats['total_items']}
• 📂 Категорий: {menu_stats['categories']}

📂 **Категории:**
"""
            
            for category, count in menu_stats.get('categories_detail', {}).items():
                response += f"• {category}: {count} позиций\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            logger.info("✅ Меню перезагружено через callback")
            
        except Exception as e:
            logger.error(f"❌ Ошибка перезагрузки меню: {e}")
            await query.edit_message_text(
                "❌ Ошибка перезагрузки меню.\n"
                "Проверьте логи для подробностей."
            )
    
    async def debug_menu_callback(self, query):
        """Диагностика меню для отладки"""
        try:
            await query.edit_message_text("🔍 Диагностика меню...")
            
            # Получаем отладочную информацию
            debug_info = self.menu_service.get_debug_info()
            
            # Разбиваем на части если слишком длинно
            if len(debug_info) > 4000:
                parts = [debug_info[i:i+4000] for i in range(0, len(debug_info), 4000)]
                for i, part in enumerate(parts):
                    if i == 0:
                        await query.edit_message_text(f"```\n{part}\n```", parse_mode='Markdown')
                    else:
                        await query.message.reply_text(f"```\n{part}\n```", parse_mode='Markdown')
            else:
                await query.edit_message_text(f"```\n{debug_info}\n```", parse_mode='Markdown')
            
            # Добавляем кнопки
            keyboard = [
                [InlineKeyboardButton("🔄 Перезагрузить с отладкой", callback_data="force_reload")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                "🔧 Используйте кнопки для дальнейших действий:",
                reply_markup=reply_markup
            )
            
            logger.info("✅ Диагностика меню выполнена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка диагностики меню: {e}")
            await query.edit_message_text(
                "❌ Ошибка диагностики меню.\n"
                "Проверьте логи для подробностей."
            )
    
    async def force_reload_callback(self, query):
        """Принудительная перезагрузка с отладкой"""
        try:
            await query.edit_message_text("🔄 Принудительная перезагрузка с отладкой...")
            
            # Выполняем перезагрузку с отладкой
            debug_info = self.menu_service.force_reload_with_debug()
            
            # Получаем новую статистику
            menu_stats = self.menu_service.get_menu_stats()
            
            response = f"""
✅ **Принудительная перезагрузка завершена!**

📊 **Результат:**
• 📄 TXT файлов: {menu_stats.get('txt_files_count', 0)}
• 📋 Позиций: {menu_stats['total_items']}
• 📂 Категорий: {menu_stats['categories']}

📂 **Загруженные категории:**
"""
            
            for category, count in menu_stats.get('categories_detail', {}).items():
                response += f"• {category}: {count} позиций\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            logger.info("✅ Принудительная перезагрузка завершена")
            
        except Exception as e:
            logger.error(f"❌ Ошибка принудительной перезагрузки: {e}")
            await query.edit_message_text(
                "❌ Ошибка принудительной перезагрузки.\n"
                "Проверьте логи для подробностей."
            )
        """Перезагрузка меню из txt файлов"""
        try:
            await query.edit_message_text("🔄 Перезагружаю меню из txt файлов...")
            
            # Перезагружаем меню
            self.menu_service.reload_menu()
            
            # Получаем новую статистику
            menu_stats = self.menu_service.get_menu_stats()
            
            response = f"""
✅ **Меню успешно перезагружено!**

📊 **Новая статистика:**
• 📁 Папка: {MENU_FILES_DIR}
• 📄 TXT файлов: {menu_stats.get('txt_files_count', 0)}
• 📋 Позиций: {menu_stats['total_items']}
• 📂 Категорий: {menu_stats['categories']}

📂 **Категории:**
"""
            
            for category, count in menu_stats.get('categories_detail', {}).items():
                response += f"• {category}: {count} позиций\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            logger.info("✅ Меню перезагружено через callback")
            
        except Exception as e:
            logger.error(f"❌ Ошибка перезагрузки меню: {e}")
            await query.edit_message_text(
                "❌ Ошибка перезагрузки меню.\n"
                "Проверьте логи для подробностей."
            )
    
    async def show_menu_catalog(self, query):
        """Показ каталога меню"""
        try:
            categories = self.menu_service.get_available_categories()
            menu_stats = self.menu_service.get_menu_stats()
            
            catalog_text = f"""
📋 **Каталог меню РестДеливери**

📊 **Загружено из TXT файлов (табличный формат):**
• 📁 Папка: **{MENU_FILES_DIR.name}**
• 📄 TXT файлов: **{menu_stats.get('txt_files_count', 0)}**
• 🍽️ Всего позиций: **{menu_stats['total_items']}**
• 📂 Категорий: **{len(categories)}**
• 📋 Формат: **Артикул→Название→Описание→Вес→Цена**

🗂️ **Доступные категории:**
"""
            
            category_details = menu_stats.get('categories_detail', {})
            for i, (category, count) in enumerate(category_details.items(), 1):
                catalog_text += f"{i}. **{category}**: {count} позиций\n"
            
            catalog_text += f"""

💡 **Как использовать:**
Отправьте описание мероприятия, и я автоматически подберу оптимальное меню из каталога.

🔍 **Поиск по меню:**
Напишите "Найти [название блюда]" или "Найти [артикул]" для поиска.

🔄 **Обновление меню:**
Меню загружается из TXT файлов в табличном формате:
• Колонка 1: Артикул (например B001)
• Колонка 2: Наименование блюда  
• Колонка 3: Описание
• Колонка 4: Вес в граммах
• Колонка 5: Цена в рублях

Используйте кнопку "Перезагрузить меню" для обновления.
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Перезагрузить", callback_data="reload_menu")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                catalog_text, 
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка каталога: {e}")
            await query.edit_message_text("❌ Ошибка загрузки каталога меню")
    
    async def show_statistics(self, query):
        """Показ статистики"""
        try:
            menu_stats = self.menu_service.get_menu_stats()
            
            client_stats = {}
            try:
                client_stats = self.client_db.get_statistics()
            except:
                client_stats = {'total_clients': 0, 'total_orders': 0}
            
            stats_text = f"""
📊 **Статистика EventBot AI v2.1**

📁 **Система меню (TXT файлы):**
• 📂 Папка: **{MENU_FILES_DIR}**
• 📄 TXT файлов: **{menu_stats.get('txt_files_count', 0)}**
• 🍽️ Позиций в меню: **{menu_stats['total_items']}**
• 📂 Категорий: **{menu_stats['categories']}**

🤖 **Системные сервисы:**
• 🧠 Claude AI: **{"✅ Работает" if self.claude_service and self.claude_service.is_available() else "❌ Недоступен"}**
• 🎯 SuperAI: **{"✅ Работает" if self.super_ai_agent else "❌ Недоступен"}**
• 📊 Excel: **✅ Готов**
• 💾 База данных: **✅ Активна**

📈 **Статистика работы:**
• 👥 Клиентов в базе: **{client_stats.get('total_clients', 0)}**
• 📋 Обработано заказов: **{client_stats.get('total_orders', 0)}**

👥 **Доступ и безопасность:**
• 🔐 Менеджеров: **{len(self.manager_ids) if self.manager_ids else 'Все'}**
• 🚀 Режим: **{'🔧 Debug' if self.debug_mode else '⚡ Production'}**

⏰ **Время работы:** {datetime.now().strftime('%H:%M:%S')}
📅 **Дата:** {datetime.now().strftime('%d.%m.%Y')}

🎯 **Версия:** 2.1 Professional (menu_files)
🏢 **Компания:** РестДеливери
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Перезагрузить меню", callback_data="reload_menu")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                stats_text, 
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка статистики: {e}")
            await query.edit_message_text("❌ Ошибка получения статистики")
    
    async def show_calculator(self, query):
        """Калькулятор"""
        calculator_text = """
🧮 **Калькулятор банкетного меню v2.1**

📏 **Стандарты граммовки на 1 гостя:**

☕ **Кофе-брейк** (30-90 мин):
• Легкий: 150-200г
• Стандарт: 200-250г
• Плотный: 250-300г

🍹 **Фуршет** (2-3 часа):
• Эконом: 200-300г
• Стандарт: 300-400г
• Премиум: 400-500г

🍽️ **Банкет** (3-5 часов):
• Легкий: 600-800г
• Стандарт: 800-1200г
• Премиум: 1200-1700г

💰 **Ориентировочная стоимость на гостя:**
• Кофе-брейк: 1000-2000₽
• Фуршет: 2000-4000₽
• Банкет: 4000-8000₽

🔧 **Особенности v2.1:**
• Меню загружается из TXT файлов
• Автоматическое присвоение ID
• Исправлены ошибки с блюдами

📝 Отправьте параметры мероприятия для точного расчета!
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            calculator_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def show_help(self, query):
        """Справка"""
        help_text = f"""
❓ **Справка EventBot AI v2.1**

🆕 **Что нового в v2.1:**
• 📁 Меню загружается из папки **{MENU_FILES_DIR.name}**
• 📄 Поддержка табличного формата TXT (TSV)
• 🏷️ Автоматическое создание ID из артикулов  
• 📝 Поддержка описаний блюд
• 🔧 Исправлены все ошибки с ID

📌 **Быстрый старт:**
Просто отправьте описание вашего мероприятия!

🎯 **Примеры запросов:**
• `Корпоратив 50 человек`
• `Банкет 30 человек бюджет 100к`  
• `Фуршет 100 человек бюджет 250к`
• `Кофе-брейк 25 человек`

📄 **Табличный формат TXT файлов:**
```
Артикул	Наименование	Описание	Вес (г)	Цена (₽)
B001	Говяжий бок на пюре	Нежная говядина	250	1150
K001	Канапе с лососем	Изысканное канапе	30	180
```
Разделитель: табуляция (TAB)

💡 **Полезные советы:**
1. Указывайте точное количество гостей
2. Уточняйте формат мероприятия
3. Обозначайте бюджет (если есть)
4. Для обновления меню используйте кнопку "Перезагрузить"

📱 **Команды бота:**
• `/start` - Главное меню
• `/help` - Эта справка
• `Найти [блюдо]` - Поиск в меню
• `Найти [артикул]` - Поиск по артикулу

🏢 **РестДеливери** - Ваш надежный партнер!
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            help_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def process_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Главный обработчик сообщений"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        first_name = update.effective_user.first_name or "Менеджер"
        
        if not self._check_access(user_id):
            await update.message.reply_text(
                "❌ Доступ запрещен.\n"
                "Обратитесь к администратору для получения доступа."
            )
            return
        
        request_text = update.message.text
        logger.info(f"📝 Сообщение от {username} ({first_name}): {request_text[:100]}...")
        
        # Обработка команд поиска
        if request_text.lower().startswith("найти "):
            await self.search_menu(update, request_text[6:])
            return
        
        # Индикатор обработки
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, 
            action="typing"
        )
        
        try:
            user_info = {
                'id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': update.effective_user.last_name or '',
                'chat_id': update.effective_chat.id
            }
            
            # Используем SuperAIAgent если доступен
            if self.super_ai_agent:
                logger.info("🧠 Используем SuperAIAgent для обработки")
                
                try:
                    response = await self.super_ai_agent.process_super_request(
                        request_text, 
                        user_info
                    )
                    
                    # Проверяем Excel файл в ответе
                    excel_file_path = None
                    excel_pattern = r'📊 \*\*Excel файл готов!\*\* Файл: `([^`]+)`'
                    match = re.search(excel_pattern, response)
                    
                    if match:
                        excel_file_path = match.group(1)
                        response = re.sub(
                            r'\n\n📊 \*\*Excel файл готов!\*\*.*', 
                            '', 
                            response
                        )
                    
                    await update.message.reply_text(
                        response, 
                        parse_mode='Markdown'
                    )
                    logger.info("✅ SuperAI ответ отправлен")
                    
                    if excel_file_path and Path(excel_file_path).exists():
                        await self.send_excel_file(update, excel_file_path)
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка SuperAI: {e}")
                    await self.process_estimate_request_legacy(update, context)
                
                return
            
            # Fallback к базовому помощнику
            elif self.intelligent_assistant:
                logger.info("🔄 Используем Intelligent Assistant")
                
                try:
                    response = await self.intelligent_assistant.get_smart_response(
                        request_text
                    )
                    await update.message.reply_text(
                        response, 
                        parse_mode='Markdown'
                    )
                    logger.info("✅ Basic ответ отправлен")
                except Exception as e:
                    logger.error(f"❌ Ошибка Intelligent Assistant: {e}")
                    await self.process_estimate_request_legacy(update, context)
                
                return
            
            # Fallback к базовой обработке
            else:
                logger.info("📋 Используем базовый обработчик")
                await self.process_estimate_request_legacy(update, context)
                
        except Exception as e:
            logger.error(f"❌ Критическая ошибка обработки: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            await update.message.reply_text(
                "😔 Произошла ошибка при обработке запроса.\n\n"
                "Попробуйте:\n"
                "• Переформулировать запрос\n"
                "• Указать точные параметры\n"
                "• Обратиться к администратору\n\n"
                "Пример: `Фуршет 50 человек бюджет 150000`",
                parse_mode='Markdown'
            )
    
    async def search_menu(self, update: Update, search_query: str):
        """Поиск по меню"""
        try:
            results = self.menu_service.search_items(search_query)
            
            if results:
                response = f"🔍 **Результаты поиска: '{search_query}'**\n\n"
                for i, item in enumerate(results[:10], 1):
                    response += f"{i}. **{item['name']}**\n"
                    if item.get('article'):
                        response += f"   Артикул: {item['article']}\n"
                    response += f"   ID: {item.get('id', 'N/A')}\n"
                    response += f"   Категория: {item['category']}\n"
                    response += f"   Цена: {item['price']}₽\n"
                    if item.get('description'):
                        response += f"   Описание: {item['description']}\n"
                    response += "\n"
                
                if len(results) > 10:
                    response += f"\n_...и еще {len(results) - 10} позиций_"
            else:
                response = f"❌ По запросу '{search_query}' ничего не найдено"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")
            await update.message.reply_text("❌ Ошибка поиска по меню")
    
    async def send_excel_file(self, update: Update, file_path: str):
        """Отправка Excel файла"""
        try:
            logger.info(f"📊 Отправляем Excel файл: {file_path}")
            
            with open(file_path, 'rb') as excel_file:
                filename = Path(file_path).name
                
                caption = (
                    "📊 **Детальная смета в Excel**\n\n"
                    "✅ Полное меню с граммовкой\n"
                    "✅ Расчет персонала и услуг\n"
                    "✅ Итоговая стоимость\n\n"
                    "📞 По вопросам: support@restdelivery.ru"
                )
                
                await update.message.reply_document(
                    document=excel_file,
                    filename=filename,
                    caption=caption,
                    parse_mode='Markdown'
                )
                
            logger.info("✅ Excel файл успешно отправлен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки Excel: {e}")
            await update.message.reply_text(
                f"⚠️ Excel файл создан, но произошла ошибка при отправке.\n"
                f"Файл сохранен: `{file_path}`",
                parse_mode='Markdown'
            )
    
    async def process_estimate_request_legacy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Legacy обработка запроса"""
        await update.message.reply_text(
            "🔄 **Обрабатываю запрос в базовом режиме...**\n\n"
            "⚠️ SuperAI недоступен, используется упрощенная обработка.\n"
            "Для полного функционала настройте Claude API.",
            parse_mode='Markdown'
        )
    
    def setup_handlers(self, application: Application):
        """Настройка обработчиков"""
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("menu", self.menu_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_message)
        )
        
        logger.info("✅ Обработчики команд настроены")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        fake_query = type('obj', (object,), {
            'edit_message_text': update.message.reply_text
        })()
        await self.show_help(fake_query)
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /menu"""
        fake_query = type('obj', (object,), {
            'edit_message_text': update.message.reply_text
        })()
        await self.show_menu_catalog(fake_query)
    
    def run(self):
        """Запуск бота"""
        try:
            application = (
                Application.builder()
                .token(self.token)
                .connect_timeout(30.0)
                .read_timeout(30.0)
                .build()
            )
            
            self.setup_handlers(application)
            
            logger.info("🚀 EventBot AI v2.1 запускается...")
            logger.info(f"📁 Меню из: {MENU_FILES_DIR}")
            logger.info(f"🧠 SuperAI: {'✅ Активен' if self.super_ai_agent else '❌ Недоступен'}")
            logger.info("📱 Бот готов к приему сообщений")
            logger.info("🔗 Нажмите Ctrl+C для остановки")
            
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                timeout=30,
                pool_timeout=30
            )
            
        except Exception as e:
            logger.error(f"💥 Критическая ошибка запуска: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

def signal_handler(signum, frame):
    """Обработчик сигналов завершения"""
    logger.info("🛑 Получен сигнал завершения работы...")
    logger.info("👋 EventBot остановлен")
    sys.exit(0)

def main():
    """Главная функция"""
    try:
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Создаем необходимые директории
        directories = ['logs', 'data', 'output', 'backup', 'output/estimates', str(MENU_FILES_DIR)]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        logger.info("📁 Директории проекта проверены")
        logger.info(f"📁 Папка menu_files: {MENU_FILES_DIR}")
        
        # Проверяем наличие txt файлов
        if MENU_FILES_DIR.exists():
            txt_files = list(MENU_FILES_DIR.glob("*.txt"))
            logger.info(f"📄 Найдено txt файлов: {len(txt_files)}")
            for txt_file in txt_files:
                logger.info(f"  - {txt_file.name}")
        else:
            logger.warning(f"⚠️ Папка {MENU_FILES_DIR} не существует, будет создана")
        
        # Запускаем бота
        logger.info("🚀 Инициализация EventBot...")
        bot = EventBotAI()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("👋 EventBot остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()