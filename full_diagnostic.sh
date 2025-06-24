#!/bin/bash
# 🔍 EventBot: ПОЛНАЯ диагностика всего проекта
# Находим ВСЁ лишнее, оставляем только рабочие функции

echo "🔍 ПОЛНАЯ ДИАГНОСТИКА ПРОЕКТА EventBot"
echo "🎯 ЦЕЛЬ: Найти и удалить ВСЁ лишнее, оставить только рабочие функции"
echo ""

# Общий размер проекта
echo "📊 ОБЩИЙ РАЗМЕР ПРОЕКТА:"
du -sh . 2>/dev/null
echo ""

# Размеры всех папок
echo "📁 РАЗМЕРЫ ПАПОК (по убыванию):"
du -sh */ 2>/dev/null | sort -hr
echo ""

# Детальный анализ каждой папки
echo "🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ПАПОК:"
echo ""

# Анализ services/
echo "📁 SERVICES/ - Сервисы бота"
echo "   📊 Размер: $(du -sh services/ 2>/dev/null | cut -f1)"
echo "   🎯 Назначение: Основные сервисы EventBot"
echo "   ✅ Должно быть: 5 файлов ~500KB"
echo "   📋 Содержимое:"
ls -la services/ 2>/dev/null | head -20
echo "   🗑️ МУСОР в services/:"
echo "      - logs/ папка ($(du -sh services/logs/ 2>/dev/null | cut -f1))"
echo "      - __pycache__/ ($(du -sh services/__pycache__/ 2>/dev/null | cut -f1))"
echo "      - backup файлы: $(ls services/*backup* services/*old* services/*bak* services/*temp* 2>/dev/null | wc -l) штук"
echo "      - файлы с русскими именами: $(ls services/*копия* 2>/dev/null | wc -l) штук"
echo ""

# Анализ logs/
echo "📁 LOGS/ - Системные логи"
echo "   📊 Размер: $(du -sh logs/ 2>/dev/null | cut -f1)"
echo "   🎯 Назначение: Логи работы бота"
echo "   ✅ Должно быть: Текущие логи <10MB"
echo "   📋 Содержимое:"
ls -la logs/ 2>/dev/null | head -10
echo "   🗑️ МУСОР в logs/:"
find logs/ -name "*.log" -mtime +7 2>/dev/null | wc -l | xargs echo "      - Старые логи (>7 дней):"
find logs/ -name "*.log" -size +10M 2>/dev/null | wc -l | xargs echo "      - Большие логи (>10MB):"
echo ""

# Анализ data/
echo "📁 DATA/ - Данные и кэш"
echo "   📊 Размер: $(du -sh data/ 2>/dev/null | cut -f1)"
echo "   🎯 Назначение: НЕИЗВЕСТНО! Возможно временные данные"
echo "   ❓ Нужна проверка содержимого"
echo "   📋 Содержимое:"
ls -la data/ 2>/dev/null
echo "   📁 Подпапки:"
find data/ -type d 2>/dev/null
echo "   📄 Файлы:"
find data/ -type f -exec ls -lh {} \; 2>/dev/null | head -10
echo ""

# Анализ output/
echo "📁 OUTPUT/ - Excel сметы"
echo "   📊 Размер: $(du -sh output/ 2>/dev/null | cut -f1)"
echo "   🎯 Назначение: Готовые Excel файлы смет"
echo "   ✅ Должно быть: Только актуальные сметы"
echo "   📋 Количество файлов: $(ls output/*.xlsx 2>/dev/null | wc -l)"
echo "   🗑️ МУСОР в output/:"
find output/ -name "*.xlsx" -mtime +3 2>/dev/null | wc -l | xargs echo "      - Старые сметы (>3 дней):"
echo ""

# Анализ menu_files/
echo "📁 MENU_FILES/ - Файлы меню (КРИТИЧНО!)"
echo "   📊 Размер: $(du -sh menu_files/ 2>/dev/null | cut -f1)"
echo "   🎯 Назначение: Актуальное меню Rest Delivery"
echo "   ✅ Должно быть: 6 TXT файлов"
echo "   📋 Содержимое:"
ls -la menu_files/ 2>/dev/null
echo "   ⚠️  НЕ ТРОГАТЬ! Критичные файлы!"
echo ""

# Анализ backup папок
backup_dirs=$(find . -name "backup*" -type d 2>/dev/null)
if [ -n "$backup_dirs" ]; then
echo "📁 BACKUP ПАПКИ - МУСОР!"
echo "$backup_dirs" | while read dir; do
    echo "   🗑️ $dir: $(du -sh "$dir" 2>/dev/null | cut -f1)"
done
echo ""
fi

# Общий анализ Python файлов
echo "🐍 АНАЛИЗ PYTHON ФАЙЛОВ:"
echo "   📊 Всего .py файлов: $(find . -name "*.py" | wc -l)"
echo "   🎯 Нужно файлов: ~8-10"
echo ""
echo "   ✅ РАБОЧИЕ ФАЙЛЫ (должны остаться):"
echo "      - eventbot_fixed.py (главный файл)"
echo "      - menu_service_table_format.py (загрузка меню)"
echo "      - services/*.py (5 сервисов)"
echo ""
echo "   🗑️ МУСОР ФАЙЛЫ:"
echo "      - Backup файлы: $(find . -name "*backup*.py" | wc -l)"
echo "      - Fix файлы: $(find . -name "fix_*.py" | wc -l)"
echo "      - Test файлы: $(find . -name "test*.py" | wc -l)"
echo "      - Integrate файлы: $(find . -name "integrate*.py" | wc -l)"
echo "      - Patch файлы: $(find . -name "patch*.py" | wc -l)"
echo "      - Apply файлы: $(find . -name "apply*.py" | wc -l)"
echo "      - Old файлы: $(find . -name "*old*.py" | wc -l)"
echo "      - Файлы с русскими именами: $(find . -name "*копия*.py" | wc -l)"
echo ""

# Анализ других файлов
echo "📄 АНАЛИЗ ДРУГИХ ФАЙЛОВ:"
echo "   📊 .env backup файлов: $(ls .env.backup* 2>/dev/null | wc -l)"
echo "   📊 .sh скриптов: $(ls *.sh 2>/dev/null | wc -l)"
echo "   📊 .txt отчетов: $(ls upgrade_report*.txt diagnostic*.txt 2>/dev/null | wc -l)"
echo "   📊 .json файлов: $(find . -name "*.json" | wc -l)"
echo ""

# Python кэши
echo "🗑️ PYTHON КЭШИ:"
cache_size=$(find . -name "__pycache__" -exec du -sh {} \; 2>/dev/null | cut -f1)
cache_count=$(find . -name "__pycache__" | wc -l)
echo "   📊 __pycache__ папок: $cache_count"
echo "   📊 Размер кэшей: $cache_size"
echo "   📊 .pyc файлов: $(find . -name "*.pyc" | wc -l)"
echo ""

# Большие файлы
echo "📏 БОЛЬШИЕ ФАЙЛЫ (>1MB):"
find . -type f -size +1M -exec ls -lh {} \; 2>/dev/null | head -10
echo ""

# Старые файлы
echo "📅 СТАРЫЕ ФАЙЛЫ (изменены >7 дней назад):"
find . -type f -mtime +7 -exec ls -lh {} \; 2>/dev/null | head -10
echo ""

echo "🎯 ИТОГОВАЯ ОЦЕНКА:"
total_size=$(du -sh . 2>/dev/null | cut -f1)
echo "   📊 Текущий размер: $total_size"
echo "   🎯 Целевой размер: ~3-5MB"
echo "   🗑️ Мусора примерно: $(echo "$total_size" | sed 's/M//' | awk '{print $1-3}')MB"
echo ""

echo "🚀 РЕКОМЕНДАЦИИ ПО ОЧИСТКЕ:"
echo "   1️⃣ КРИТИЧНО: Удалить services/logs/ (5.2MB)"
echo "   2️⃣ КРИТИЧНО: Удалить все backup папки и файлы"
echo "   3️⃣ КРИТИЧНО: Удалить все fix_*, test_*, integrate_* файлы"
echo "   4️⃣ Очистить Python кэши"
echo "   5️⃣ Очистить data/ если там мусор"
echo "   6️⃣ Архивировать старые логи и Excel файлы"
echo ""

echo "💡 ФИНАЛЬНЫЙ ПРОЕКТ ДОЛЖЕН СОДЕРЖАТЬ:"
echo "   📄 eventbot_fixed.py"
echo "   📄 menu_service_table_format.py"
echo "   📄 .env"
echo "   📄 requirements.txt"
echo "   📁 services/ (5 файлов, ~500KB)"
echo "   📁 menu_files/ (6 TXT файлов)"
echo "   📁 output/ (только свежие Excel)"
echo "   📁 logs/ (только актуальные логи)"
echo "   📁 feedback_data/ (новая папка для обратной связи)"
echo ""
echo "   🎯 ИТОГО: ~3-5MB чистого, рабочего кода!"

echo ""
echo "⚠️  СЛЕДУЮЩИЙ ШАГ: Создать скрипт радикальной очистки на основе этой диагностики"