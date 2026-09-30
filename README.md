# Bayan MIDI Emulator

Графический MIDI-эмулятор баяна для Windows.

## Установка и запуск

Нужен Python 3.10 или новее. В PowerShell, открытом в папке проекта,
выполните:

```powershell
py -m pip install .
py -m bayan_emulator
```

Вторая команда запускает приложение и не зависит от того, добавлена ли папка
Python Scripts в `PATH`.

После установки также создаётся команда:

```powershell
bayan-midi-emulator
```

Если Windows сообщает, что эта команда не найдена, используйте надёжный
вариант `py -m bayan_emulator` выше. Установка не создаёт ярлык в меню «Пуск».

## Возможности

- Simulates button presses and releases
- Generates NOTE_ON and NOTE_OFF events
- Supports polyphony and chord buttons
- Графический интерфейс и вывод MIDI
- Configuration via JSON files

## MIDI-выход

Для проверки MIDI-выхода:

```powershell
py -m pip install -e .
py .\tools\midi_smoke_test.py
```

В Windows приложению нужен уже существующий MIDI-выход:

- физическое MIDI-устройство; или
- виртуальный MIDI-порт.

Само приложение виртуальный MIDI-порт в Windows не создаёт.

## Конфигурация

Дополнительные раскладки хранятся в каталоге `configs/`.
Файл `bayan_test.json` предназначен только для тестов и не содержит полную
раскладку инструмента.
