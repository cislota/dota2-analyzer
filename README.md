# Dota 2 Match Analyzer

Консольная утилита для анализа последних матчей игрока Dota 2 через публичный OpenDota API.

Приложение получает матчи по `account_id`, сохраняет сырые данные, считает базовую статистику и выводит результат в понятном виде.

## Возможности

- загрузка последних матчей игрока через OpenDota API;
- сохранение сырых матчей в JSON;
- расчет общего винрейта;
- расчет побед и поражений;
- расчет средней длительности матча;
- группировка матчей по героям;
- сохранение результата анализа в JSON или CSV;
- fallback на локально сохраненные матчи, если API временно недоступен.

## Структура проекта

```text
dota2-match-analyzer/
|-- main.py
|-- api_client.py
|-- models.py
|-- analyzer.py
|-- storage.py
|-- requirements.txt
|-- README.md
|-- data/
|   |-- raw/
|   `-- processed/
`-- utils/
    |-- __init__.py
    `-- exceptions.py
```

## Установка

Требуется Python 3.10+.

Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
```

Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source venv/bin/activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

## Команды

### Загрузить матчи

```bash
python main.py fetch 123456789
```

Команда:

- получает последние 20 матчей игрока;
- сохраняет сырые данные в `data/raw/123456789_matches.json`;
- выводит краткую проверочную информацию по первым матчам.

Можно изменить количество матчей:

```bash
python main.py fetch 123456789 --limit 10
```

### Проанализировать матчи

```bash
python main.py analyze 123456789
```

Команда:

- получает последние матчи через OpenDota API;
- сохраняет raw-данные в `data/raw/`;
- считает статистику;
- выводит результат в консоль.

Если API недоступен, команда попробует загрузить ранее сохраненный файл из `data/raw/`.

### Сохранить анализ

JSON:

```bash
python main.py analyze 123456789 --save json
```

CSV:

```bash
python main.py analyze 123456789 --save csv
```

Результаты сохраняются в:

```text
data/processed/123456789_stats.json
data/processed/123456789_stats.csv
```

## Пример вывода

```text
Dota 2 Match Analyzer

Player ID: 123456789
Matches analyzed: 20

Winrate: 60.0%
Wins: 12
Losses: 8

Average match duration: 38:42

Top heroes:
1. Hero ID 78 - 5 games, 4 wins, winrate 80.0%
2. Hero ID 21 - 3 games, 2 wins, winrate 66.7%
3. Hero ID 11 - 2 games, 1 win, winrate 50.0%
```

## Как считается победа

OpenDota возвращает сторону игрока в поле `player_slot`:

- `player_slot < 128` - игрок был за Radiant;
- `player_slot >= 128` - игрок был за Dire.

Победа игрока определяется сравнением его стороны с `radiant_win`:

- Radiant + `radiant_win=True` означает победу;
- Dire + `radiant_win=False` означает победу.

## Файлы

- `main.py` - точка входа и CLI на `argparse`;
- `api_client.py` - получение матчей из OpenDota;
- `models.py` - dataclass-модели `Match`, `HeroStats`, `PlayerStats`;
- `analyzer.py` - расчет статистики;
- `storage.py` - сохранение и загрузка JSON/CSV;
- `utils/exceptions.py` - пользовательские исключения.

## Источник данных

OpenDota API:

https://api.opendota.com/api
