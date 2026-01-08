# TrackCast

TrackCast это проект, направленный для стримеров, который считывает играющий в Яндекс Музыке и Spotify трек, который отображается на локальной странице, которую можно вывести в OBS.

## Установка

Для установки необходимо скачать исходный код проекта и выполнить команду:

```bash
git clone https://github.com/kartavkun/TrackCast.git
```

Для установки зависимостей используется [UV](https://docs.astral.sh/uv/getting-started/installation/). Для установки вы должны ввести в терминале:

[!NOTE] Для Spotify необходимо создать файл spotify_cred.py в директории src/trackcast/auth/ со следующим содержимым:

```python
CLIENT_ID = '<your client id>'
CLIENT_SECRET = '<your client secret>'
```

Для установки требуется ###

## Запуск

Для запуска и работы с программой рекомендуется использовать [UV](https://docs.astral.sh/uv/getting-started/installation/). Для запуска вы должны ввести в терминале:

```bash
cd src
uv run -m trackcast.tray_app
```

## Использование

**Скоро**

## Планы

- Реализовать систему стилей для виджета, не требуемый пересборки программы
- Сделать отдельные виджеты для ЯМ и Spotify (Потому что Spotify даёт больше информации чем ЯМ)

## Лицензия

GNU GPL v3

## Credits

**Скоро**
