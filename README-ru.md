
<div align="center">
  <h1>flarepick</h1>
</div>

**flarepick** — инструмент для удобной организации фотографий в красивые галереи.

<img src="https://img.shields.io/badge/Python-3.14-blue">
<img src="https://img.shields.io/badge/PyQt6-GUI-green">

## ✨ Возможности

- 🗂️ **Коллекции** — организуйте фотографии в собственные коллекции.
- 🏷️ **EXIF-метаданные** — просматривайте настройки камеры, ISO, выдержку и диафрагму.
- 🚩 **Отбор и отклонение** — быстро отмечайте фотографии как выбранные или отклонённые.
- 🖥️ **Десктопный интерфейс** — управляйте фотографиями через приложение на PyQt6.

## ⚙️ Технические характеристики

<p align="left">
  <img src="https://img.shields.io/badge/Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white">
  <img src="https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white">
  <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black">
</p>

### Установка

Если вы хотите запустить *flarepick* непосредственно из исходного кода без сборки исполняемого файла, выполните следующие действия:

1. Клонируйте репозиторий.
2. Установите зависимости:
```bash
pip3 install -r requirements.txt
```

3. Запустите приложение:
```bash
python3 main.py
```

### Хранение данных

Фотографии остаются в исходных папках и не копируются и не изменяются приложением *flarepick*.

База данных SQLite хранит только коллекции и ссылки на отмеченные фотографии (выбранные или отклонённые).

### Библиотеки

- PyQt6 — графический интерфейс.
- sqlite3 — база данных.
