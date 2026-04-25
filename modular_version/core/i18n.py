TRANSLATIONS = {'ru': {'done': 'Готово',
        'csv_saved_msg': 'Экспортировано строк: {n}\nФайл: {path}',
        'scan_mode_recursive': 'Сканирование (с подпапками)',
        'scan_mode_norec': 'Сканирование (только текущая папка)',
        'stat_new': 'нов',
        'stat_updated': 'обн',
        'stat_skipped': 'проп',
        'stat_errors': 'ош',
        'stat_sha1': 'SHA1',
        'app_title': 'Менеджер файловых баз данных',
        'app_subtitle': 'Индексация, поиск и управление файлами с SQLite',
        'theme': 'Тема:',
        'language': 'Язык:',
        'info_text': '• Системные/скрытые папки автоматически исключаются\n'
                     '• Двойной щелчок в списке — показать файл в папке\n'
                     '• Неоднозначно: двойной щелчок для выбора',
        'scan_options': 'Параметры сканирования',
        'incremental': 'Инкрементальное обновление',
        'calc_sha1': 'Вычислять SHA1 (медленно)',
        'include_subfolders': 'Включая подпапки',
        'btn_build': 'Создать новую базу из папок',
        'btn_build_incremental': 'Обновить существующую базу из папок',
        'btn_set': 'Создать/обновить набор (буфер/txt/xlsx)',
        'btn_view': '👁️ Просмотр базы',
        'btn_exit': 'Выйти',
        'btn_stop': 'Остановить операцию',
        'btn_background': 'Свернуть в трей',
        'confirm_stop_title': 'Подтверждение остановки',
        'confirm_stop_msg': 'Рекомендуется дождаться завершения.\n\nПосле принудительной остановки или аварийного закрытия может потребоваться повторная индексация.\n\nОстановить операцию?',
        'scan_close_running_title': 'Окно операции',
        'scan_close_running_msg': 'Операция ещё выполняется.\n\nРекомендуется дождаться завершения. После принудительной остановки или аварийного закрытия может потребоваться повторная индексация.\n\nЧто сделать?',
        'status_ready': 'Готово.',
        'status_stopping': 'Остановка… Рекомендуется дождаться завершения. После принудительной остановки или аварийного закрытия может потребоваться повторная индексация.',
        'status_scan': 'Сканирование…',
        'status_counting_title': 'Подсчёт файлов…',
        'status_counting_files': 'Подсчёт файлов… найдено: {counted}',
        'status_sync': 'Синхронизация набора…',
        'set_name_title': 'Имя набора',
        'set_name_prompt': 'Введите имя набора (например: Договор_123):',
        'set_name_empty': 'Введите имя набора.',
        'source_title': 'Источник',
        'source_text': 'Выберите источник списка путей:',
        'mode_title': 'Режим',
        'mode_text': 'Перезаписать набор целиком?\nДа = заменить\nНет = добавить к существующему',
        'empty_warning': 'Пусто',
        'empty_text': 'Пути не найдены (пустой буфер/файл).',
        'scan_complete': 'Сканирование завершено',
        'scan_complete_msg': 'Обработано файлов: ',
        'set_created': 'Набор сохранён',
        'set_created_msg': ' элементов, найдено: ',
        'choose_scan_folder_title': 'Выберите папку для сканирования',
        'choose_scan_folders_title': 'Выберите папки для сканирования',
        'add_more_folders_title': 'Добавить ещё папку?',
        'add_more_folders_text': 'Текущая папка добавлена. Хотите добавить ещё одну папку в эту же '
                                 'базу?',
        'no_scan_folders_selected': 'Не выбраны папки для сканирования.',
        'multi_folder_prompt': 'Выберите несколько папок для индексации в одном окне. Добавляйте '
                               'нужные папки в список, удаляйте лишние и запускайте сканирование.',
        'selected_folders_label': 'Выбранные папки',
        'selected_folders_count': 'Выбрано папок: {count}',
        'btn_add_folder': 'Добавить папку',
        'btn_remove_selected_folder': 'Удалить выбранную',
        'btn_clear_folders': 'Очистить список',
        'btn_start_scan': 'Запустить индексацию',
        'folder_already_added': 'Эта папка уже добавлена в список.',
        'scan_roots_label': 'Корни сканирования:',
        'choose_db_save_title': 'Куда сохранить базу данных (.db)?',
        'choose_db_open_title': 'Откройте базу данных (.db)',
        'incremental_no_db_selected_title': 'Инкрементальное обновление',
        'incremental_no_db_selected_text': 'Для инкрементального обновления нужна существующая '
                                           'база, созданная этой программой.\n'
                                           '\n'
                                           'Если у вас ещё нет базы, нажмите «Да», чтобы создать '
                                           'новую базу без инкрементального обновления.\n'
                                           'Если хотите вернуться без изменений, нажмите «Нет».',
        'incremental_invalid_db_title': 'Выбранная база не подходит',
        'incremental_invalid_db_text': 'Эта база не подходит для инкрементального обновления.\n'
                                       '\n'
                                       'Причина: {reason}\n'
                                       '\n'
                                       'Нажмите «Да», чтобы выбрать другую существующую базу.\n'
                                       'Нажмите «Нет», чтобы создать новую базу без '
                                       'инкрементального обновления.',
        'incremental_db_reason_missing': 'файл базы не найден',
        'incremental_db_reason_structure': 'в файле нет структуры этой программы (нужны таблицы '
                                           'files и meta)',
        'incremental_db_reason_sqlite': 'файл не удалось открыть как корректную SQLite-базу',
        'incremental_db_reason_unknown': 'не удалось проверить структуру базы',
        'choose_set_source_title': 'Источник списка путей',
        'choose_set_source_paste': 'Вставить из буфера',
        'choose_set_source_file': 'Выбрать файл',
        'choose_set_source_cancel': 'Отмена',
        'status_found': 'Найден',
        'status_missing': 'Не найден',
        'status_ambiguous': 'Неоднозначно',
        'theme_changed': 'Тема изменена',
        'theme_changed_msg': 'Применена тема: ',
        'lang_changed': 'Язык изменен',
        'lang_changed_msg': 'Выбран язык: ',
        'viewer_title': 'Просмотр базы данных — ',
        'set_all': '(Все)',
        'set_label': 'Набор:',
        'status_label': 'Статус:',
        'search_label': 'Поиск:',
        'search_btn': 'Найти',
        'tt_search_btn_filters': 'Поиск выполняется по текущей выборке с учётом всех фильтров. Если заданы расширение, размер или дата, результаты будут только среди файлов, которые им соответствуют.',
        'reset_btn': 'Сброс',
        'only_existing': 'Только существующие на диске',
        'show_in_folder': 'Показать в папке',
        'resolve_ambiguous': 'Разрешить неоднозначные',
        'export_csv': 'Экспорт в CSV',
        'close': 'Закрыть',
        'first': '⏮ В начало',
        'previous': '← Назад',
        'next': 'Вперёд →',
        'last': 'В конец ⏭',
        'of': 'из',
        'searching': 'Поиск...',
        'header_name': 'Имя',
        'header_relpath': 'Относительный путь / исходный',
        'header_size': 'Размер',
        'header_mtime': 'Изменён',
        'header_present': 'Есть',
        'header_status': 'Статус',
        'header_fullpath': 'Полный путь / сопоставленный',
        'resolve_title': 'Разрешить неоднозначность',
        'original_path': 'Исходный путь:',
        'candidates': 'Кандидаты по имени файла: ',
        'select_save': 'Выбрать и сохранить',
        'cancel': 'Отмена',
        'no_candidates': 'Нет кандидатов',
        'no_candidates_msg': 'Кандидаты не найдены. Возможно, база нуждается в обновлении.',
        'no_selection': 'Ничего не выбрано',
        'no_selection_msg': 'Пожалуйста, выберите один вариант.',
        'error': 'Ошибка',
        'warning': 'Предупреждение',
        'info': 'Информация',
        'help': 'Помощь',
        'help_title': 'Помощь',
        'help_update_db_text': 'Если вы удаляли/перемещали файлы на диске, база могла устареть.\n'
                               '\n'
                               '• Нажмите «Создать базу из папки» и отметьте «Инкрементальное '
                               'обновление»\n'
                               '• Или пересоздайте базу заново\n'
                               '\n'
                               'После обновления поиск и «Показать в папке» будут работать '
                               'корректно.',
        'empty_path': 'Пустой путь',
        'empty_path_msg': 'Не выбран путь к файлу.',
        'file_not_found': 'Файл не найден',
        'file_not_found_msg': 'Файл не найден. Обновите, пожалуйста, базу.\n\nОткрыта папка:\n\n',
        'not_found': 'Не найдено',
        'not_found_msg': 'Файл и папка не найдены:\n\n',
        'copy': 'Копировать',
        'stop': 'Стоп',
        'save_report_title': 'Сохранить отчёт',
        'save_report_btn': 'Сохранить отчёт…',
        'filetype_text': 'Текстовый файл',
        'filetype_all': 'Все файлы',
        'report_saved_title': 'Отчёт сохранён',
        'report_saved_msg': 'Отчёт сохранён в файл:\n{path}',
        'report_save_failed': 'Не удалось сохранить отчёт:\n{err}',
        'warning_title': 'Предупреждение',
        'tt_incremental': 'Обновляет сведения о файлах в базе. Для поиска по содержимому новые и '
                          'изменённые документы нужно индексировать отдельно.',
        'tt_sha1': 'SHA1 — контрольная сумма файла. Помогает определить изменения и найти точные '
                   'дубликаты. Сильно замедляет сканирование.',
        'help_sha1_title': 'SHA1',
        'help_sha1_text': 'SHA1 — это «отпечаток» содержимого файла (контрольная сумма).\n'
                          '\n'
                          'Зачем нужно:\n'
                          '• контроль изменений — разный SHA1 означает, что файл изменился\n'
                          '• поиск точных дубликатов по содержимому\n'
                          '\n'
                          'Минус: SHA1 считается чтением файла целиком, поэтому сканирование может '
                          'стать заметно медленнее.',
        'tt_recursive': 'Сканировать также подпапки выбранной папки.',
        'tt_only_existing': 'Показывает только файлы, которые сейчас существуют на диске. Если '
                            'удаляли файлы вручную — обновите базу (инкремент).',
        'tt_help_btn': 'Открыть справку',
        'dialog_hint_open_file': 'Сейчас откроется системное окно Windows для выбора файла.',
        'dialog_hint_save_file': 'Сейчас откроется системное окно Windows для выбора места '
                                 'сохранения.',
        'dialog_hint_select_folder': 'Сейчас откроется системное окно Windows для выбора папки.',
        'warn_increment_off': 'Вы отключили инкрементальное обновление. Следующее сканирование '
                              'пересоздаст базу заново (старые записи будут удалены). Продолжить?',
        'warn_only_existing_on': 'Фильтр «Только существующие на диске» опирается на данные базы. '
                                 'Если вы удаляли файлы вручную, рекомендуется обновить базу '
                                 '(инкремент). Включить фильтр?',
        'warn_sha1_on': 'Вычисление SHA1 может значительно замедлить сканирование, особенно для '
                        'больших файлов и HDD/сетевых папок. Включить SHA1?',
        'help_incremental_title': 'Инкрементальное обновление',
        'help_incremental_text': 'Обновляет сведения о файлах в базе. Для поиска по содержимому новые '
                                 'и изменённые документы нужно индексировать отдельно.',
        'help_only_existing_title': 'Только существующие на диске',
        'help_only_existing_text': 'Этот фильтр показывает только файлы, которые в базе отмечены '
                                   'как существующие на диске.\n'
                                   '\n'
                                   'Если вы удалили файл вручную, база отразит это после '
                                   'инкрементального обновления.',
        'help_status_title': 'Фильтр «Статус»',
        'help_status_text': 'Показывает записи по статусу (актуально для наборов/Set):\n'
                            '\n'
                            '• (Все) — без фильтра\n'
                            '• Найден — путь сопоставлен и файл найден\n'
                            '• Не найден — файла нет на диске (помечено при обновлении)\n'
                            '• Неоднозначно — найдено несколько вариантов, нужен выбор\n'
                            '\n'
                            'Если выбран (Все) наборов, статусы не используются.',
        'ok': 'Понятно',
        'yes': 'Да',
        'no': 'Нет',
        'error_title': 'Ошибка',
        'help_btn_build_title': 'Создание / обновление базы',
        'help_btn_build_text': 'Сканирует выбранные папки и создаёт или обновляет SQLite-базу '
                               'файлов.\n'
                               '\n'
                               'Порядок работы:\n'
                               '1) выберите одну или несколько папок для сканирования\n'
                               '2) если включён инкремент — выберите существующую .db для '
                               'обновления\n'
                               '3) если инкремент выключен — укажите новую .db или подтвердите '
                               'пересоздание существующей\n'
                               '\n'
                               'Что делает кнопка:\n'
                               '• добавляет новые файлы\n'
                               '• обновляет изменённые файлы\n'
                               '• при инкременте помечает удалённые файлы как отсутствующие на '
                               'диске\n'
                               '• при выключенном инкременте пересобирает таблицу файлов с нуля\n'
                               '\n'
                               'Опции выше влияют на скорость и полноту сканирования.',
        'help_btn_set_title': 'Создание / обновление набора',
        'help_btn_set_text': 'Загружает список путей из буфера, TXT или Excel и сопоставляет его с '
                             'выбранной базой.\n'
                             '\n'
                             'Результат сохраняется как именованный набор со статусами: Найден / '
                             'Не найден / Неоднозначно.',
        'help_btn_view_title': 'Просмотр базы',
        'help_btn_view_text': 'Открывает просмотрщик базы: поиск, фильтры, экспорт CSV, показ '
                              'файла в папке и ручное разрешение неоднозначных строк набора.',
        'xlsx_disabled_warn': '⚠ Импорт XLSX отключён (установите openpyxl: pip install openpyxl). '
                              'TXT/буфер работают.',
        'csv_filetype': 'CSV',
        'sqlite_db_filetype': 'База SQLite',
        'text_files_filetype': 'Текстовые файлы',
        'text_excel_filetype': 'Текст/Excel',
        'excel_files_filetype': 'Файлы Excel',
        'err_read_paths': 'Не удалось прочитать список путей:\n{err}',
        'err_open_db': 'Не удалось открыть базу данных:\n{err}',
        'err_read_paths_generic': 'Не удалось прочитать список путей.',
        'err_open_db_generic': 'Не удалось открыть базу данных.',
        'report_save_failed_generic': 'Не удалось сохранить отчёт.',
        'show_in_folder_failed_generic': 'Не удалось показать файл в папке.',
        'search_failed_generic': 'Не удалось выполнить поиск.',
        'scan_failed_generic': 'Операция сканирования завершилась с ошибкой.',
        'set_sync_failed_generic': 'Не удалось создать или обновить набор.',
        'resolve_need_specific_set': 'Разрешение неоднозначности работает только для выбранного '
                                     'набора (не «(Все)»).',
        'resolve_row_not_ambiguous': 'Выбранная строка не имеет статуса «Неоднозначно».',
        'resolve_no_service_data': 'Не удалось определить служебные данные выбранной строки.',
        'set_summary_full': 'Набор: {name}\n'
                            'Всего элементов: {total}\n'
                            'Найдено: {found}\n'
                            'Не найдено: {missing}\n'
                            'Неоднозначных: {ambiguous}\n'
                            '\n'
                            'Что дальше:\n'
                            '1) Откройте «Просмотр базы».\n'
                            '2) Выберите набор «{name}».\n'
                            '3) Для строк со статусом «Неоднозначно» сделайте двойной щелчок и '
                            'выберите правильный файл.',
        'set_status_updated': 'Набор «{name}» обновлён: {total} элементов (найдено {found})',
        'set_toast_updated': 'Набор «{name}»: {total} эл., найдено {found}, неоднозначных '
                             '{ambiguous}',
        'confirm_title': 'Подтверждение',
        'scan_report_summary': 'Итоги:\n'
                               'Всего обработано: {total}\n'
                               'Новых: {new}\n'
                               'Обновлено: {updated}\n'
                               'Без изменений: {unchanged}\n'
                               'Пропущено: {skipped}\n'
                               'Ошибок: {errors}\n'
                               'SHA1 вычислено: {sha1}\n'
                               'Помечено как отсутствующие: {missing}',
        'scan_report_folders': 'Файлы по папкам:',
        'scan_stopped_title': 'Сканирование остановлено',
        'scan_stopped_msg': 'Операция остановлена пользователем. Уже обработано файлов: {total}. '
                            'Ошибок: {errors}.',
        'status_scan_stopped': 'Сканирование остановлено пользователем.',
        'exit_scan_running_title': 'Выход из программы',
        'exit_scan_running_msg': 'Сканирование ещё выполняется.\n\nРекомендуется дождаться завершения. После принудительной остановки или аварийного закрытия может потребоваться повторная индексация.\n\nОстановить операцию и выйти?',
        'export_csv_running': 'Идёт экспорт CSV…',
        'export_csv_done': 'CSV экспортирован: {n} строк',
        'search_mode_fs': 'Файлы и папки',
        'search_mode_content': 'Содержимое документов',
        'header_mark': 'Выбор',
        'header_source': 'Источник',
        'header_snippet': 'Фрагмент',
        'item_kind_all': 'Все объекты',
        'item_kind_files': 'Только файлы',
        'item_kind_folders': 'Только папки',
        'filter_ext': 'Расш.',
        'filter_size_from': 'Размер от',
        'filter_to': 'до',
        'filter_date_from': 'Дата от',
        'filter_clear': 'Сбросить фильтры',
        'btn_equalize_columns': 'Выровнять ширину',
        'tt_equalize_columns': 'Сделать все колонки одинаковой ширины.',
        'filter_ext_all': 'Все расширения',
        'tt_ext_filter_files_only': 'Фильтр по расширению доступен только в режиме «Только файлы» '
                                    'в выпадающем списке слева.',
        'tt_size_filter_example': 'Например: 500 KB, 10 MB, 1.5 GB. Нажмите Enter',
        'calendar_btn': '...',
        'calendar_title': 'Выбор даты',
        'calendar_today': 'Сегодня',
        'calendar_prev_month': '←',
        'calendar_next_month': '→',
        'calendar_month_names': 'Январь|Февраль|Март|Апрель|Май|Июнь|Июль|Август|Сентябрь|Октябрь|Ноябрь|Декабрь',
        'calendar_weekday_names': 'Пн|Вт|Ср|Чт|Пт|Сб|Вс',
        'btn_mark_page': 'Отметить все на странице',
        'btn_mark_all_pages': 'Отметить все на всех страницах',
        'marked_count': 'Отмечено: {count}',
        'nothing_found_title': 'Ничего не найдено',
        'content_search_no_results_message': 'По содержимому ничего не найдено. Если индексация ещё не завершена, результаты могут появиться позже.',
        'tt_search_mode_content_help': 'Поиск по содержимому работает по PDF, DOCX и XLSX. Результаты появляются только для уже проиндексированных файлов. Для части PDF поиск зависит от встроенного текста или OCR.',
        'open_help': 'Открыть справку',
        'help_content_search_title': 'Справка по поиску по содержимому',
        'help_content_search_text': 'Поиск по содержимому работает по PDF, DOCX и XLSX.\n\nЧто важно:\n• результаты появляются только для уже проиндексированных файлов;\n• для части PDF поиск зависит от встроенного текста или OCR;\n• можно вводить обычные слова, фразы и адреса — знаки препинания обрабатываются автоматически.',
        'search_failed_content_invalid': 'Поиск по содержимому не смог обработать этот запрос. Введите слово, фразу или адрес обычным текстом.',
        'search_failed_content': 'Не удалось выполнить поиск по содержимому. Попробуйте запрос без лишних знаков препинания или проверьте, завершена ли индексация.',
        'btn_mark_all': 'Отметить всё',
        'btn_unmark_all': 'Снять всё',
        'btn_collect_checked': 'Собрать отмеченные',
        'collect_files_title': 'Сбор файлов',
        'collect_files_choose_dir': 'Куда собрать выбранные файлы',
        'collect_files_none_selected': 'Ничего не выбрано',
        'collect_files_result': 'Скопировано: {copied}\nПропущено: {skipped}',
        'item_type_folder': 'Папка',
        'item_type_file': 'Файл',
        'index_docs_title': 'Индексация документов',
        'index_docs_prepare': 'Подготовка…',
        'index_mode_changed': 'Изменённые',
        'index_mode_all': 'Все',
        'index_mode_errors': 'Ошибки',
        'btn_index_content': 'Индексировать содержимое документов',
        'help_index_content_title': 'Индексировать содержимое документов',
        'help_index_content_text': 'Создаёт или обновляет индекс текста документов. Уже '
                                   'проиндексированные и неизменённые файлы пропускаются.',
        'old_db_title': 'Старая база данных',
        'old_db_message': 'Эта база создана старой версией программы и не поддерживает новые '
                          'функции.\n'
                          '\n'
                          'Отсутствуют таблицы: {tables}\n'
                          '\n'
                          'Создайте новую базу в текущей версии утилиты.',
        'help_index_content_body': 'Создает или обновляет поисковый индекс по тексту внутри '
                                   'документов.\n'
                                   '\n'
                                   'Поддерживаются Word, Excel и PDF. Для PDF при плохом '
                                   'встроенном тексте может использоваться OCR, если рядом '
                                   'доступен content_runtime.\n'
                                   '\n'
                                   'Обычный запуск работает инкрементально: обновляет новые и '
                                   'измененные документы, не трогая остальные.',
        'index_docs_summary': 'Готово. Обработано: {processed}\nУспешно: {ok}\nОшибок: {errors}',
        'index_docs_nothing_to_do': 'Новых или изменённых документов для индексации не найдено.',
        'save': 'Сохранить',
        'open': 'Открыть',
        'select': 'Выбрать',
        'path_dialog_title': 'Выбор пути',
        'path_dialog_location': 'Папка:',
        'path_dialog_go': 'Перейти',
        'path_dialog_up': 'Вверх',
        'path_dialog_name': 'Имя',
        'path_dialog_type': 'Тип',
        'path_dialog_filename': 'Имя файла:',
        'path_dialog_current_folder': 'Текущая папка:',
        'path_dialog_folder': 'Папка',
        'path_dialog_file': 'Файл',
        'path_dialog_invalid_folder': 'Указанная папка недоступна.',
        'path_dialog_no_file_name': 'Введите имя файла.',
        'path_dialog_file_missing': 'Выбранный файл не найден.',
        'tray_restore': 'Восстановить',
        'tray_hide_icon': 'Скрыть значок в трее',
        'size_unit_b': 'Б',
        'size_unit_kb': 'КБ',
        'size_unit_mb': 'МБ',
        'size_unit_gb': 'ГБ',
        'size_unit_tb': 'ТБ',
        'size_unit_pb': 'ПБ',
        'datetime_format': '%Y-%m-%d %H:%M',
        'content_source_docx': 'Word',
        'content_source_xlsx': 'Excel',
        'content_source_pdf_embedded': 'PDF (встроенный текст)',
        'content_source_pdf_ocr': 'PDF (OCR)',
        'content_source_pdf_mixed': 'PDF (смешанный)',
        'content_source_unknown': 'Документ',
        'show_in_folder_failed': 'Не удалось показать файл в папке.',
        'unsupported_set_source_filetype': 'Поддерживаются только .txt и .xlsx/.xlsm/.xltx/.xltm',
        'quick_start_title': 'С чего начать',
        'quick_start_text': '1. Откройте существующую базу или создайте новую.\n'
                            '2. Для индексации выберите одну или несколько папок.\n'
                            '3. Для поиска по содержимому нужна полная индексация содержимого.\n'
                            '4. Фильтр по расширению работает только в режиме «Только файлы».\n'
                            '5. Папка content_runtime должна находиться рядом с программой. Она нужна для OCR PDF-файлов и полной индексации их содержимого.',
        'btn_hide': 'Скрыть',
        'btn_show': 'Показать'},
 'en': {'done': 'Done',
        'csv_saved_msg': 'Exported rows: {n}\nFile: {path}',
        'scan_mode_recursive': 'Scanning (with subfolders)',
        'scan_mode_norec': 'Scanning (current folder only)',
        'stat_new': 'new',
        'stat_updated': 'upd',
        'stat_skipped': 'skip',
        'stat_errors': 'err',
        'stat_sha1': 'sha1',
        'app_title': 'File Database Manager',
        'app_subtitle': 'Index, search, and manage files with SQLite',
        'theme': 'Theme:',
        'language': 'Language:',
        'info_text': '• System/hidden folders are automatically excluded\n'
                     '• Double-click in viewer to show file in folder\n'
                     '• AMBIGUOUS: double-click to resolve manually',
        'scan_options': 'Scan Options',
        'incremental': 'Incremental update',
        'calc_sha1': 'Calculate SHA1 (slow)',
        'include_subfolders': 'Include subfolders',
        'btn_build': 'Create new database from folders',
        'btn_build_incremental': 'Update existing database from folders',
        'btn_set': 'Create/update set (clipboard/txt/xlsx)',
        'btn_view': '👁️ View database',
        'btn_exit': 'Exit',
        'btn_stop': 'Stop operation',
        'btn_background': 'Minimize to tray',
        'confirm_stop_title': 'Confirm stop',
        'confirm_stop_msg': 'It is recommended to wait until completion.\n\nAfter a forced stop or unexpected shutdown, reindexing may be required.\n\nStop the operation?',
        'scan_close_running_title': 'Operation window',
        'scan_close_running_msg': 'The operation is still running.\n\nIt is recommended to wait until completion. After a forced stop or unexpected shutdown, reindexing may be required.\n\nWhat would you like to do?',
        'status_ready': 'Ready.',
        'status_stopping': 'Stopping… It is recommended to wait until completion. After a forced stop or unexpected shutdown, reindexing may be required.',
        'status_scan': 'Scanning…',
        'status_counting_title': 'Counting files…',
        'status_counting_files': 'Counting files… found: {counted}',
        'status_sync': 'Syncing set…',
        'set_name_title': 'Set name',
        'set_name_prompt': 'Enter set name (e.g., Contract_123):',
        'set_name_empty': 'Enter a set name.',
        'source_title': 'Source',
        'source_text': 'Choose where to take the path list from:',
        'mode_title': 'Mode',
        'mode_text': 'Replace set completely?\nYes = replace\nNo = append to existing',
        'empty_warning': 'Empty',
        'empty_text': 'No paths found (empty clipboard/file).',
        'scan_complete': 'Scan Complete',
        'scan_complete_msg': 'Processed files: ',
        'set_created': 'Set Created',
        'set_created_msg': ' items, found: ',
        'choose_scan_folder_title': 'Select folder to scan',
        'choose_scan_folders_title': 'Select folders to scan',
        'add_more_folders_title': 'Add another folder?',
        'add_more_folders_text': 'The current folder has been added. Do you want to add another '
                                 'folder to the same database?',
        'no_scan_folders_selected': 'No folders were selected for scanning.',
        'multi_folder_prompt': 'Choose several folders for indexing in one window. Add the folders '
                               'you need to the list, remove extras, then start scanning.',
        'selected_folders_label': 'Selected folders',
        'selected_folders_count': 'Folders selected: {count}',
        'btn_add_folder': 'Add folder',
        'btn_remove_selected_folder': 'Remove selected',
        'btn_clear_folders': 'Clear list',
        'btn_start_scan': 'Start indexing',
        'folder_already_added': 'This folder is already in the list.',
        'scan_roots_label': 'Scan roots:',
        'choose_db_save_title': 'Save database file (.db)',
        'choose_db_open_title': 'Open database file (.db)',
        'incremental_no_db_selected_title': 'Incremental update',
        'incremental_no_db_selected_text': 'Incremental update needs an existing database created '
                                           'by this program.\n'
                                           '\n'
                                           'If you do not have one yet, click Yes to create a new '
                                           'database without incremental update.\n'
                                           'If you want to go back without changes, click No.',
        'incremental_invalid_db_title': 'Selected database is not suitable',
        'incremental_invalid_db_text': 'This database cannot be used for incremental update.\n'
                                       '\n'
                                       'Reason: {reason}\n'
                                       '\n'
                                       'Click Yes to choose another existing database.\n'
                                       'Click No to create a new database without incremental '
                                       'update.',
        'incremental_db_reason_missing': 'database file was not found',
        'incremental_db_reason_structure': "the file does not contain this program's database "
                                           'structure (tables files and meta are required)',
        'incremental_db_reason_sqlite': 'the file could not be opened as a valid SQLite database',
        'incremental_db_reason_unknown': 'the database structure could not be verified',
        'choose_set_source_title': 'Path list source',
        'choose_set_source_paste': 'Paste from clipboard',
        'choose_set_source_file': 'Choose file',
        'choose_set_source_cancel': 'Cancel',
        'status_found': 'Found',
        'status_missing': 'Missing',
        'status_ambiguous': 'Ambiguous',
        'theme_changed': 'Theme Changed',
        'theme_changed_msg': 'Applied theme: ',
        'lang_changed': 'Language Changed',
        'lang_changed_msg': 'Selected language: ',
        'viewer_title': 'Database Viewer — ',
        'set_all': '(All)',
        'set_label': 'Set:',
        'status_label': 'Status:',
        'search_label': 'Search:',
        'search_btn': 'Search',
        'tt_search_btn_filters': 'Search runs on the current filtered selection with all active filters applied. If a specific extension is selected, results will only include files of that type.',
        'copy': 'Copy',
        'stop': 'Stop',
        'reset_btn': 'Reset',
        'only_existing': 'Only existing on disk',
        'show_in_folder': 'Show in folder',
        'resolve_ambiguous': 'Resolve ambiguous',
        'export_csv': 'Export to CSV',
        'close': 'Close',
        'first': '⏮ First',
        'previous': '← Prev',
        'next': 'Next →',
        'last': 'Last ⏭',
        'of': 'of',
        'searching': 'Searching…',
        'header_name': 'Name',
        'header_relpath': 'Relative path / raw',
        'header_size': 'Size',
        'header_mtime': 'Modified',
        'header_present': 'Exists',
        'header_status': 'Status',
        'header_fullpath': 'Full path / resolved',
        'resolve_title': 'Resolve AMBIGUOUS',
        'original_path': 'Original path:',
        'candidates': 'Candidates by filename: ',
        'select_save': 'Select and save',
        'cancel': 'Cancel',
        'no_candidates': 'No candidates',
        'no_candidates_msg': 'No candidates found. Database might need update.',
        'no_selection': 'No selection',
        'no_selection_msg': 'Please select one candidate.',
        'error': 'Error',
        'warning': 'Warning',
        'info': 'Information',
        'empty_path': 'Empty path',
        'empty_path_msg': 'No path selected.',
        'file_not_found': 'File not found',
        'file_not_found_msg': 'File not found. Please update the database.\n\nOpened folder:\n\n',
        'show_in_folder_failed': 'Failed to show file in folder.',
        'not_found': 'Not found',
        'not_found_msg': 'File and folder not found:\n\n',
        'save_report_title': 'Save report',
        'save_report_btn': 'Save report…',
        'filetype_text': 'Text file',
        'filetype_all': 'All files',
        'report_saved_title': 'Report saved',
        'report_saved_msg': 'Report saved to:\n{path}',
        'report_save_failed': 'Failed to save report:\n{err}',
        'tt_incremental': 'Updates file records in the database. New and changed documents must be '
                          'indexed separately for content search.',
        'tt_only_existing': 'Shows only files that currently exist on disk. If you deleted files '
                            'manually, update the database (incremental).',
        'tt_sha1': 'SHA1 is a file checksum. Detects changes and exact duplicates. Significantly '
                   'slows scanning.',
        'tt_recursive': 'Scan subfolders of the selected folder as well.',
        'tt_help_btn': 'Open help',
        'dialog_hint_open_file': 'A Windows system dialog will open to choose a file.',
        'dialog_hint_save_file': 'A Windows system dialog will open to choose where to save the '
                                 'file.',
        'dialog_hint_select_folder': 'A Windows system dialog will open to choose a folder.',
        'warning_title': 'Warning',
        'warn_increment_off': 'You disabled incremental update. The next scan will rebuild the '
                              'database from scratch (old records will be removed). Continue?',
        'warn_only_existing_on': 'The “Only existing on disk” filter relies on database data. If '
                                 'you deleted files manually, it is recommended to update the '
                                 'database (incremental). Enable the filter?',
        'warn_sha1_on': 'Computing SHA1 can significantly slow scanning, especially for large '
                        'files and HDD/network drives. Enable SHA1?',
        'help_incremental_title': 'Incremental update',
        'help_incremental_text': 'Updates file records in the database. New and changed documents '
                                 'must be indexed separately for content search.',
        'help_only_existing_title': 'Only existing on disk',
        'help_only_existing_text': 'This filter shows only files marked in the database as present '
                                   'on disk.\n'
                                   '\n'
                                   'If you delete a file manually, the database will reflect it '
                                   'after an incremental update.',
        'help_status_title': 'Status filter',
        'help_status_text': 'Filters rows by status (relevant for Sets):\n'
                            '\n'
                            '• (All) — no filter\n'
                            '• Found — path matched and the file was found\n'
                            '• Missing — file not present on disk (marked during update)\n'
                            '• Ambiguous — multiple candidates, needs manual resolve\n'
                            '\n'
                            'If (All) sets is selected, statuses are not used.',
        'help_sha1_title': 'SHA1',
        'help_sha1_text': 'SHA1 is a content checksum (fingerprint).\n'
                          '\n'
                          'Uses:\n'
                          '• change tracking — different SHA1 means the file changed\n'
                          '• exact duplicate detection by content\n'
                          '\n'
                          'Downside: SHA1 requires reading the whole file, so scanning may become '
                          'much slower.',
        'help_title': 'Help',
        'help_update_db_text': 'If you deleted or moved files on disk, the database may be out of '
                               'date.\n'
                               '\n'
                               '• Click “Create/update database from folder” and enable '
                               '“Incremental update”\n'
                               '• Or rebuild the database from scratch\n'
                               '\n'
                               'After updating, search and “Show in folder” will work correctly.',
        'ok': 'Got it',
        'yes': 'Yes',
        'no': 'No',
        'error_title': 'Error',
        'help_btn_build_title': 'Build / update database',
        'help_btn_build_text': 'Scans the selected folders and creates or updates the SQLite file '
                               'database.\n'
                               '\n'
                               'Workflow:\n'
                               '1) choose one or more folders to scan\n'
                               '2) if incremental mode is enabled, open an existing .db to update\n'
                               '3) if incremental mode is off, choose where to save a new .db or '
                               'recreate an existing one\n'
                               '\n'
                               'What this button does:\n'
                               '• adds new files\n'
                               '• updates changed files\n'
                               '• in incremental mode, marks removed files as missing on disk\n'
                               '• with incremental mode off, rebuilds the files table from '
                               'scratch\n'
                               '\n'
                               'The options above affect scan speed and completeness.',
        'help_btn_set_title': 'Create / update set',
        'help_btn_set_text': 'Loads a path list from clipboard, TXT, or Excel and matches it '
                             'against the selected database.\n'
                             '\n'
                             'The result is saved as a named set with statuses: Found / Missing / '
                             'Ambiguous.',
        'help_btn_view_title': 'View database',
        'help_btn_view_text': 'Opens the database viewer: search, filters, CSV export, show file in folder, and manual resolution of ambiguous set rows.',
        'csv_filetype': 'CSV',
        'sqlite_db_filetype': 'SQLite Database',
        'text_files_filetype': 'Text files',
        'text_excel_filetype': 'Text/Excel',
        'excel_files_filetype': 'Excel files',
        'err_read_paths': 'Failed to read path list:\n{err}',
        'err_open_db': 'Failed to open database:\n{err}',
        'err_read_paths_generic': 'Failed to read path list.',
        'err_open_db_generic': 'Failed to open database.',
        'report_save_failed_generic': 'Failed to save report.',
        'show_in_folder_failed_generic': 'Failed to show file in folder.',
        'search_failed_generic': 'Search failed.',
        'scan_failed_generic': 'Scanning operation failed.',
        'set_sync_failed_generic': 'Failed to create or update set.',
        'resolve_need_specific_set': 'Resolving ambiguity works only for a selected set (not '
                                     '“(All)”).',
        'resolve_row_not_ambiguous': 'The selected row does not have AMBIGUOUS status.',
        'resolve_no_service_data': 'Could not determine service row data (set_item_id/raw_path).',
        'set_summary_full': 'Set: {name}\n'
                            'Total items: {total}\n'
                            'Found: {found}\n'
                            'Missing: {missing}\n'
                            'Ambiguous: {ambiguous}\n'
                            '\n'
                            'Next steps:\n'
                            '1) Open “View database”.\n'
                            '2) Select set “{name}”.\n'
                            '3) Double-click AMBIGUOUS rows and choose the correct file.',
        'set_status_updated': 'Set “{name}” updated: {total} items (found {found})',
        'set_toast_updated': 'Set “{name}”: {total} items, found {found}, ambiguous {ambiguous}',
        'confirm_title': 'Confirm',
        'scan_report_summary': 'Summary:\n'
                               'Processed total: {total}\n'
                               'New: {new}\n'
                               'Updated: {updated}\n'
                               'Unchanged: {unchanged}\n'
                               'Skipped: {skipped}\n'
                               'Errors: {errors}\n'
                               'SHA1 computed: {sha1}\n'
                               'Marked missing: {missing}',
        'scan_report_folders': 'Files by folder:',
        'scan_stopped_title': 'Scan stopped',
        'scan_stopped_msg': 'The operation was stopped by the user. Files already processed: '
                            '{total}. Errors: {errors}.',
        'status_scan_stopped': 'Scan stopped by user.',
        'export_csv_running': 'Exporting CSV…',
        'export_csv_done': 'CSV exported: {n} rows',
        'exit_scan_running_title': 'Exit Program',
        'exit_scan_running_msg': 'A scan is still running. Stop the operation and exit?',
        'search_mode_fs': 'Files and folders',
        'search_mode_content': 'Document content',
        'header_mark': 'Pick',
        'header_source': 'Source',
        'header_snippet': 'Snippet',
        'item_kind_all': 'All items',
        'item_kind_files': 'Files only',
        'item_kind_folders': 'Folders only',
        'filter_ext': 'Ext',
        'filter_size_from': 'Size from',
        'filter_to': 'to',
        'filter_date_from': 'Date from',
        'filter_clear': 'Clear filters',
        'btn_equalize_columns': 'Equalize widths',
        'tt_equalize_columns': 'Make all columns the same width.',
        'filter_ext_all': 'All extensions',
        'tt_ext_filter_files_only': 'Extension filter is available only in the Files only mode.',
        'tt_size_filter_example': 'For example: 500 KB, 10 MB, 1.5 GB. Press Enter',
        'calendar_btn': '...',
        'calendar_title': 'Choose date',
        'calendar_today': 'Today',
        'calendar_prev_month': '←',
        'calendar_next_month': '→',
        'calendar_month_names': 'January|February|March|April|May|June|July|August|September|October|November|December',
        'calendar_weekday_names': 'Mon|Tue|Wed|Thu|Fri|Sat|Sun',
        'btn_mark_page': 'Mark all on page',
        'btn_mark_all_pages': 'Mark all on all pages',
        'marked_count': 'Marked: {count}',
        'nothing_found_title': 'Nothing found',
        'content_search_no_results_message': 'No matches were found in document content. If indexing is still running, results may appear later.',
        'tt_search_mode_content_help': 'Content search works with PDF, DOCX, and XLSX files. Results appear only for files that have already been indexed. For some PDFs, search depends on embedded text or OCR.',
        'open_help': 'Open help',
        'help_content_search_title': 'Content search help',
        'help_content_search_text': 'Content search works with PDF, DOCX, and XLSX files.\n\nImportant:\n• results appear only for files that have already been indexed;\n• for some PDFs, search depends on embedded text or OCR;\n• you can enter normal words, phrases, and addresses — punctuation is handled automatically.',
        'search_failed_content_invalid': 'Content search could not process this query. Enter a word, phrase, or address as normal text.',
        'search_failed_content': 'Could not complete content search. Try a query with fewer punctuation marks, or check whether indexing has finished.',
        'btn_mark_all': 'Mark all',
        'btn_unmark_all': 'Unmark all',
        'btn_collect_checked': 'Collect checked',
        'collect_files_title': 'Collect files',
        'collect_files_choose_dir': 'Choose destination folder',
        'collect_files_none_selected': 'Nothing selected',
        'collect_files_result': 'Copied: {copied}\nSkipped: {skipped}',
        'item_type_folder': 'Folder',
        'item_type_file': 'File',
        'index_docs_title': 'Indexing documents',
        'index_docs_prepare': 'Preparing…',
        'index_mode_changed': 'Changed',
        'index_mode_all': 'All',
        'index_mode_errors': 'Errors',
        'btn_index_content': 'Index document content',
        'help_index_content_title': 'Index document content',
        'help_index_content_text': 'Creates or updates the text index for documents. Already indexed '
                                   'and unchanged files are skipped.',
        'old_db_title': 'Old database',
        'old_db_message': 'This database was created by an older version of the application and '
                          'does not support the new features.\n'
                          '\n'
                          'Missing tables: {tables}\n'
                          '\n'
                          'Create a new database with the current version of the utility.',
        'help_index_content_body': 'Creates or updates a search index for text inside documents.\n'
                                   '\n'
                                   'Supports Word, Excel and PDF. For PDF, OCR may be used when '
                                   'embedded text is poor and content_runtime is available.\n'
                                   '\n'
                                   'A normal run is incremental: it updates new and changed '
                                   'documents without reprocessing everything.',
        'index_docs_summary': 'Done. Processed: {processed}\nOK: {ok}\nErrors: {errors}',
        'index_docs_nothing_to_do': 'No new or changed documents were found for indexing.',
        'save': 'Save',
        'open': 'Open',
        'select': 'Select',
        'path_dialog_title': 'Choose path',
        'path_dialog_location': 'Folder:',
        'path_dialog_go': 'Go',
        'path_dialog_up': 'Up',
        'path_dialog_name': 'Name',
        'path_dialog_type': 'Type',
        'path_dialog_filename': 'File name:',
        'path_dialog_current_folder': 'Current folder:',
        'path_dialog_folder': 'Folder',
        'path_dialog_file': 'File',
        'path_dialog_invalid_folder': 'The selected folder is not available.',
        'path_dialog_no_file_name': 'Enter a file name.',
        'path_dialog_file_missing': 'The selected file was not found.',
        'tray_restore': 'Restore',
        'tray_hide_icon': 'Hide tray icon',
        'size_unit_b': 'B',
        'size_unit_kb': 'KB',
        'size_unit_mb': 'MB',
        'size_unit_gb': 'GB',
        'size_unit_tb': 'TB',
        'size_unit_pb': 'PB',
        'datetime_format': '%Y-%m-%d %H:%M',
        'content_source_docx': 'Word',
        'content_source_xlsx': 'Excel',
        'content_source_pdf_embedded': 'PDF (embedded text)',
        'content_source_pdf_ocr': 'PDF (OCR)',
        'content_source_pdf_mixed': 'PDF (mixed)',
        'content_source_unknown': 'Document',
        'help': 'Help',
        'unsupported_set_source_filetype': 'Only .txt and .xlsx/.xlsm/.xltx/.xltm are supported',
        'quick_start_title': 'Getting started',
        'quick_start_text': '1. Open an existing database or create a new one.\n'
                            '2. For indexing, choose one or several folders.\n'
                            '3. Full content indexing is required for content search.\n'
                            '4. The extension filter works only in the “Files only” mode.\n'
                            '5. The content_runtime folder must be located next to the program. It is needed for OCR of PDF files and full indexing of their contents.',
        'btn_hide': 'Hide',
        'btn_show': 'Show'},
 'de': {'done': 'Fertig',
        'csv_saved_msg': 'Exportierte Zeilen: {n}\nDatei: {path}',
        'scan_mode_recursive': 'Scan (mit Unterordnern)',
        'scan_mode_norec': 'Scan (nur aktueller Ordner)',
        'stat_new': 'neu',
        'stat_updated': 'akt',
        'stat_skipped': 'überspr',
        'stat_errors': 'Fehl',
        'stat_sha1': 'SHA1',
        'app_title': 'Datei-Datenbank-Manager',
        'app_subtitle': 'Dateien mit SQLite indexieren, suchen und verwalten',
        'theme': 'Design:',
        'language': 'Sprache:',
        'info_text': '• System-/versteckte Ordner werden automatisch ausgeschlossen\n'
                     '• Doppelklick in der Liste — Datei im Ordner anzeigen\n'
                     '• Mehrdeutig: Doppelklick zum Auswählen',
        'scan_options': 'Scan-Optionen',
        'incremental': 'Inkrementelles Update',
        'calc_sha1': 'SHA1 berechnen (langsam)',
        'include_subfolders': 'Unterordner einbeziehen',
        'btn_build': 'Neue Datenbank aus Ordnern erstellen',
        'btn_build_incremental': 'Vorhandene Datenbank aus Ordnern aktualisieren',
        'btn_set': 'Set erstellen/aktualisieren (Zwischenablage/TXT/XLSX)',
        'btn_view': '👁️ Datenbank anzeigen',
        'btn_exit': 'Beenden',
        'btn_stop': 'Vorgang stoppen',
        'btn_background': 'In den Tray',
        'confirm_stop_title': 'Stopp bestätigen',
        'confirm_stop_msg': 'Möchten Sie den Vorgang wirklich stoppen?',
        'scan_close_running_title': 'Vorgangsfenster',
        'scan_close_running_msg': 'Der Vorgang läuft noch. Was möchten Sie tun?',
        'status_ready': 'Bereit.',
        'status_stopping': 'Wird gestoppt… (warten Sie auf das Ende des aktuellen Pakets)',
        'status_scan': 'Scanne…',
        'status_counting_title': 'Dateien zählen…',
        'status_counting_files': 'Dateien werden gezählt… gefunden: {counted}',
        'status_sync': 'Set wird synchronisiert…',
        'set_name_title': 'Satzname',
        'set_name_prompt': 'Geben Sie einen Satznamen ein (z. B. Vertrag_123):',
        'set_name_empty': 'Bitte geben Sie einen Satznamen ein.',
        'source_title': 'Quelle',
        'source_text': 'Wählen Sie die Quelle der Pfadliste:',
        'mode_title': 'Modus',
        'mode_text': 'Vorhandenen Satz vollständig überschreiben?\n'
                     'Ja = ersetzen\n'
                     'Nein = zum bestehenden Satz hinzufügen',
        'empty_warning': 'Leer',
        'empty_text': 'Keine Pfade gefunden (Zwischenablage/Datei ist leer).',
        'scan_complete': 'Scannen abgeschlossen',
        'scan_complete_msg': 'Verarbeitete Dateien: ',
        'set_created': 'Satz gespeichert',
        'set_created_msg': ' Elemente, gefunden: ',
        'choose_scan_folder_title': 'Ordner zum Scannen wählen',
        'choose_scan_folders_title': 'Ordner zum Scannen wählen',
        'add_more_folders_title': 'Weiteren Ordner hinzufügen?',
        'add_more_folders_text': 'Der aktuelle Ordner wurde hinzugefügt. Möchten Sie einen '
                                 'weiteren Ordner in dieselbe Datenbank aufnehmen?',
        'no_scan_folders_selected': 'Es wurden keine Ordner zum Scannen ausgewählt.',
        'multi_folder_prompt': 'Wählen Sie mehrere Ordner für die Indexierung in einem Fenster '
                               'aus. Fügen Sie die benötigten Ordner der Liste hinzu, entfernen '
                               'Sie überflüssige und starten Sie dann den Scan.',
        'selected_folders_label': 'Ausgewählte Ordner',
        'selected_folders_count': 'Ausgewählte Ordner: {count}',
        'btn_add_folder': 'Ordner hinzufügen',
        'btn_remove_selected_folder': 'Auswahl entfernen',
        'btn_clear_folders': 'Liste leeren',
        'btn_start_scan': 'Indexierung starten',
        'folder_already_added': 'Dieser Ordner ist bereits in der Liste.',
        'scan_roots_label': 'Scan-Wurzeln:',
        'choose_db_save_title': 'Datenbankdatei speichern (.db)',
        'choose_db_open_title': 'Datenbankdatei öffnen (.db)',
        'incremental_no_db_selected_title': 'Inkrementelles Update',
        'incremental_no_db_selected_text': 'Für ein inkrementelles Update wird eine vorhandene, '
                                           'mit diesem Programm erstellte Datenbank benötigt.\n'
                                           '\n'
                                           'Wenn Sie noch keine Datenbank haben, klicken Sie auf '
                                           '„Ja“, um ohne inkrementelles Update eine neue '
                                           'Datenbank zu erstellen.\n'
                                           'Wenn Sie ohne Änderungen zurückkehren möchten, klicken '
                                           'Sie auf „Nein“.',
        'incremental_invalid_db_title': 'Ausgewählte Datenbank ist nicht geeignet',
        'incremental_invalid_db_text': 'Diese Datenbank kann nicht für ein inkrementelles Update '
                                       'verwendet werden.\n'
                                       '\n'
                                       'Grund: {reason}\n'
                                       '\n'
                                       'Klicken Sie auf „Ja“, um eine andere vorhandene Datenbank '
                                       'auszuwählen.\n'
                                       'Klicken Sie auf „Nein“, um ohne inkrementelles Update eine '
                                       'neue Datenbank zu erstellen.',
        'incremental_db_reason_missing': 'die Datenbankdatei wurde nicht gefunden',
        'incremental_db_reason_structure': 'die Datei enthält nicht die Datenbankstruktur dieses '
                                           'Programms (Tabellen files und meta sind erforderlich)',
        'incremental_db_reason_sqlite': 'die Datei konnte nicht als gültige SQLite-Datenbank '
                                        'geöffnet werden',
        'incremental_db_reason_unknown': 'die Datenbankstruktur konnte nicht geprüft werden',
        'choose_set_source_title': 'Quelle der Pfadliste',
        'choose_set_source_paste': 'Aus Zwischenablage einfügen',
        'choose_set_source_file': 'Datei auswählen',
        'choose_set_source_cancel': 'Abbrechen',
        'status_found': 'Gefunden',
        'status_missing': 'Nicht gefunden',
        'status_ambiguous': 'Mehrdeutig',
        'theme_changed': 'Thema geändert',
        'theme_changed_msg': 'Angewendetes Thema: ',
        'lang_changed': 'Sprache geändert',
        'lang_changed_msg': 'Ausgewählte Sprache: ',
        'viewer_title': 'Datenbankansicht — ',
        'set_all': '(Alle)',
        'set_label': 'Satz:',
        'status_label': 'Status:',
        'search_label': 'Suche:',
        'search_btn': 'Suchen',
        'tt_search_btn_filters': 'Die Suche wird auf der aktuell gefilterten Auswahl unter Berücksichtigung aller aktiven Filter ausgeführt. Wenn eine bestimmte Erweiterung gewählt ist, enthalten die Ergebnisse nur Dateien dieses Typs.',
        'copy': 'Kopieren',
        'stop': 'Stopp',
        'reset_btn': 'Zurücksetzen',
        'only_existing': 'Nur aktuell vorhandene Dateien',
        'show_in_folder': 'Im Ordner anzeigen',
        'resolve_ambiguous': 'Mehrdeutige Einträge auflösen',
        'export_csv': 'Als CSV exportieren',
        'close': 'Schließen',
        'first': '⏮ Zum Anfang',
        'previous': '← Zurück',
        'next': 'Weiter →',
        'last': '⏭ Zum Ende',
        'of': 'von',
        'searching': 'Suche…',
        'header_name': 'Name',
        'header_relpath': 'Relativer Pfad / Quelle',
        'header_size': 'Größe',
        'header_mtime': 'Geändert',
        'header_present': 'Vorhanden',
        'header_status': 'Status',
        'header_fullpath': 'Vollständiger Pfad / zugeordneter Pfad',
        'resolve_title': 'Mehrdeutigkeit auflösen',
        'original_path': 'Ursprünglicher Pfad:',
        'candidates': 'Kandidaten nach Dateinamen: ',
        'select_save': 'Auswählen und speichern',
        'cancel': 'Abbrechen',
        'no_candidates': 'Keine Kandidaten',
        'no_candidates_msg': 'Keine Kandidaten gefunden. Die Datenbank muss möglicherweise '
                             'aktualisiert werden.',
        'no_selection': 'Nichts ausgewählt',
        'no_selection_msg': 'Bitte wählen Sie einen Eintrag aus.',
        'error': 'Fehler',
        'warning': 'Warnung',
        'info': 'Info',
        'empty_path': 'Leerer Pfad',
        'empty_path_msg': 'Es wurde kein Dateipfad ausgewählt.',
        'file_not_found': 'Datei nicht gefunden',
        'file_not_found_msg': 'Datei nicht gefunden. Bitte aktualisieren Sie die Datenbank.\n'
                              '\n'
                              'Geöffneter Ordner:\n'
                              '\n',
        'show_in_folder_failed': 'Datei konnte im Ordner nicht angezeigt werden:\n{err}',
        'not_found': 'Nicht gefunden',
        'not_found_msg': 'Datei und Ordner nicht gefunden:\n\n',
        'save_report_title': 'Bericht speichern',
        'save_report_btn': 'Bericht speichern…',
        'filetype_text': 'Textdatei',
        'filetype_all': 'Alle Dateien',
        'report_saved_title': 'Bericht gespeichert',
        'report_saved_msg': 'Bericht gespeichert unter:\n{path}',
        'report_save_failed': 'Bericht konnte nicht gespeichert werden:\n{err}',
        'tt_incremental': 'Gilt nur für die Schaltfläche „Datenbank aus Ordnern '
                          'erstellen/aktualisieren“. Wenn aktiviert, wird eine vorhandene .db '
                          'aktualisiert: neue Dateien werden hinzugefügt und fehlende als „nicht '
                          'auf dem Datenträger“ markiert. Einträge werden nicht gelöscht.',
        'tt_only_existing': 'Zeigt nur Dateien an, die aktuell auf dem Datenträger vorhanden sind. '
                            'Wenn Sie Dateien manuell gelöscht haben – aktualisieren Sie die '
                            'Datenbank (inkrementell).',
        'tt_sha1': 'SHA1 ist die Prüfsumme einer Datei. Hilft, Änderungen zu erkennen und exakte '
                   'Duplikate zu finden. Verlangsamt den Scan deutlich.',
        'tt_recursive': 'Auch Unterordner des gewählten Ordners scannen.',
        'tt_help_btn': 'Hilfe öffnen',
        'dialog_hint_open_file': 'Jetzt wird das Windows-Systemfenster zur Dateiauswahl geöffnet.',
        'dialog_hint_save_file': 'Jetzt wird das Windows-Systemfenster zur Auswahl des '
                                 'Speicherorts geöffnet.',
        'dialog_hint_select_folder': 'Jetzt wird das Windows-Systemfenster zur Ordnerauswahl '
                                     'geöffnet.',
        'warning_title': 'Warnung',
        'warn_increment_off': 'Sie haben die inkrementelle Aktualisierung deaktiviert. Der nächste '
                              'Scan erstellt die Datenbank neu (alte Einträge werden entfernt). '
                              'Fortfahren?',
        'warn_only_existing_on': 'Der Filter „Nur auf Datenträger vorhandene“ nutzt Daten aus der '
                                 'Datenbank. Wenn Sie Dateien manuell gelöscht haben, wird '
                                 'empfohlen, die Datenbank zu aktualisieren (inkrementell). Filter '
                                 'aktivieren?',
        'warn_sha1_on': 'Die Berechnung von SHA1 kann den Scan deutlich verlangsamen, besonders '
                        'bei großen Dateien und HDD/Netzwerkordnern. SHA1 aktivieren?',
        'help_incremental_title': 'Inkrementelles Update',
        'help_incremental_text': 'Diese Option gilt nur für die Schaltfläche „Datenbank aus '
                                 'Ordnern erstellen/aktualisieren“.\n'
                                 '\n'
                                 'So funktioniert es:\n'
                                 '• bei aktiviertem inkrementellem Modus wählen Sie eine '
                                 'vorhandene .db zum Aktualisieren\n'
                                 '• neue Dateien werden zur Datenbank hinzugefügt\n'
                                 '• vom Datenträger entfernte Dateien bleiben in der Datenbank, '
                                 'werden aber als „nicht auf dem Datenträger“ markiert\n'
                                 '• geänderte Dateien werden aktualisiert\n'
                                 '\n'
                                 'Wenn der inkrementelle Modus ausgeschaltet ist, geben Sie eine '
                                 'neue .db an oder erstellen eine vorhandene Datenbank vollständig '
                                 'neu. Dabei wird die Dateitabelle von Grund auf neu aufgebaut.\n'
                                 '\n'
                                 'Diese Option gilt nicht für die Schaltflächen „Set '
                                 'erstellen/aktualisieren“ und „Datenbank anzeigen“.',
        'help_only_existing_title': 'Nur auf Datenträger vorhandene',
        'help_only_existing_text': 'Dieser Filter zeigt nur Dateien an, die in der Datenbank als '
                                   'auf dem Datenträger vorhanden markiert sind.\n'
                                   '\n'
                                   'Wenn Sie eine Datei manuell gelöscht haben, wird die Datenbank '
                                   'dies nach einer inkrementellen Aktualisierung widerspiegeln.',
        'help_status_title': 'Filter „Status“',
        'help_status_text': 'Zeigt Einträge nach Status (relevant für Sätze/Set):\n'
                            '\n'
                            '• (Alle) — kein Filter\n'
                            '• Gefunden — Pfad wurde zugeordnet und Datei gefunden\n'
                            '• Nicht gefunden — Datei fehlt auf dem Datenträger\n'
                            '• Mehrdeutig — mehrere Varianten gefunden, Auswahl nötig\n'
                            '\n'
                            'Wenn (Alle) Sätze gewählt ist, werden Status nicht verwendet.',
        'help_sha1_title': 'SHA1-Berechnung',
        'help_sha1_text': 'SHA1 ist ein „Fingerabdruck“ des Dateiinhalts (Prüfsumme).\n'
                          '\n'
                          'Wofür es nützlich ist:\n'
                          '• Kontrolle von Änderungen – unterschiedliche SHA1 bedeuten, dass sich '
                          'die Datei geändert hat\n'
                          '• Suche nach exakten Duplikaten anhand des Inhalts\n'
                          '\n'
                          'Nachteil: SHA1 wird durch vollständiges Lesen der Datei berechnet, '
                          'daher kann der Scan deutlich langsamer werden.',
        'help_title': 'Hilfe',
        'help_update_db_text': 'Wenn Sie Dateien auf dem Datenträger gelöscht oder verschoben '
                               'haben, kann die Datenbank veraltet sein.\n'
                               '\n'
                               '• Klicken Sie auf „Datenbank aus Ordnern erstellen“ und aktivieren '
                               'Sie „Inkrementelle Aktualisierung“\n'
                               '• Oder erstellen Sie die Datenbank neu\n'
                               '\n'
                               'Nach der Aktualisierung funktionieren Suche und „Im Ordner '
                               'anzeigen“ korrekt.',
        'ok': 'Verstanden',
        'yes': 'Ja',
        'no': 'Nein',
        'error_title': 'Fehler',
        'help_btn_build_title': 'Datenbank erstellen / aktualisieren',
        'help_btn_build_text': 'Scannt die ausgewählten Ordner und erstellt oder aktualisiert die '
                               'SQLite-Dateidatenbank.\n'
                               '\n'
                               'Ablauf:\n'
                               '1) einen oder mehrere Ordner zum Scannen wählen\n'
                               '2) wenn der inkrementelle Modus aktiv ist, eine vorhandene .db zum '
                               'Aktualisieren öffnen\n'
                               '3) wenn der inkrementelle Modus aus ist, Speicherort für eine neue '
                               '.db wählen oder eine vorhandene Datenbank neu erstellen\n'
                               '\n'
                               'Diese Schaltfläche:\n'
                               '• fügt neue Dateien hinzu\n'
                               '• aktualisiert geänderte Dateien\n'
                               '• markiert im inkrementellen Modus entfernte Dateien als auf dem '
                               'Datenträger fehlend\n'
                               '• baut bei ausgeschaltetem inkrementellem Modus die Dateitabelle '
                               'von Grund auf neu auf\n'
                               '\n'
                               'Die Optionen oben beeinflussen Geschwindigkeit und Vollständigkeit '
                               'des Scans.',
        'help_btn_set_title': 'Satz erstellen / aktualisieren',
        'help_btn_set_text': 'Lädt eine Liste von Pfaden aus Zwischenablage, TXT oder Excel und '
                             'gleicht sie mit der gewählten Datenbank ab.\n'
                             '\n'
                             'Das Ergebnis wird als benannter Satz mit den Status Gefunden / Nicht '
                             'gefunden / Mehrdeutig gespeichert.',
        'help_btn_view_title': 'Datenbank anzeigen',
        'help_btn_view_text': 'Öffnet die Datenbankansicht: Suche, Filter, CSV-Export, Anzeige der Datei im Ordner und manuelle Auflösung mehrdeutiger Set-Zeilen.',
        'text_files_filetype': 'Textdateien',
        'text_excel_filetype': 'Text- und Excel-Dateien',
        'excel_files_filetype': 'Excel-Dateien',
        'err_read_paths': 'Die Pfadliste konnte nicht gelesen werden:\n{err}',
        'err_open_db': 'Die Datenbank konnte nicht geöffnet werden:\n{err}',
        'err_read_paths_generic': 'Die Pfadliste konnte nicht gelesen werden.',
        'err_open_db_generic': 'Die Datenbank konnte nicht geöffnet werden.',
        'report_save_failed_generic': 'Bericht konnte nicht gespeichert werden.',
        'show_in_folder_failed_generic': 'Datei konnte im Ordner nicht angezeigt werden.',
        'search_failed_generic': 'Die Suche konnte nicht ausgeführt werden.',
        'scan_failed_generic': 'Der Scanvorgang wurde mit einem Fehler beendet.',
        'set_sync_failed_generic': 'Der Satz konnte nicht erstellt oder aktualisiert werden.',
        'resolve_need_specific_set': 'Die Auflösung von Mehrdeutigkeiten funktioniert nur für '
                                     'einen ausgewählten Satz (nicht „(Alle)“).',
        'resolve_row_not_ambiguous': 'Die ausgewählte Zeile hat nicht den Status „Mehrdeutig“.',
        'resolve_no_service_data': 'Die Dienstdaten der ausgewählten Zeile konnten nicht ermittelt '
                                   'werden.',
        'set_summary_full': 'Satz: {name}\n'
                            'Insgesamt Elemente: {total}\n'
                            'Gefunden: {found}\n'
                            'Nicht gefunden: {missing}\n'
                            'Mehrdeutig: {ambiguous}\n'
                            '\n'
                            'Nächste Schritte:\n'
                            '1) Öffnen Sie „Datenbank anzeigen“.\n'
                            '2) Wählen Sie den Satz „{name}“.\n'
                            '3) Doppelklicken Sie bei Zeilen mit Status „Mehrdeutig“ und wählen '
                            'Sie die richtige Datei aus.',
        'set_status_updated': 'Satz „{name}“ aktualisiert: {total} Elemente (gefunden {found})',
        'set_toast_updated': 'Satz „{name}“: {total} Eintr., gefunden {found}, mehrdeutig '
                             '{ambiguous}',
        'confirm_title': 'Bestätigung',
        'scan_report_summary': 'Zusammenfassung',
        'scan_report_folders': 'Ordner',
        'scan_stopped_title': 'Vorgang gestoppt',
        'scan_stopped_msg': 'Der Vorgang wurde vom Benutzer gestoppt.',
        'status_scan_stopped': 'Scan gestoppt.',
        'export_csv_running': 'CSV wird exportiert…',
        'export_csv_done': 'CSV-Export abgeschlossen',
        'exit_scan_running_title': 'Vorgangsfenster',
        'exit_scan_running_msg': 'Ein Vorgang läuft noch. Was soll geschehen?',
        'search_mode_fs': 'Dateien und Ordner',
        'search_mode_content': 'Dokumentinhalt',
        'header_mark': 'Auswahl',
        'header_source': 'Quelle',
        'header_snippet': 'Ausschnitt',
        'item_kind_all': 'Alle Objekte',
        'item_kind_files': 'Nur Dateien',
        'item_kind_folders': 'Nur Ordner',
        'filter_ext': 'Erw.',
        'filter_size_from': 'Größe von',
        'filter_to': 'bis',
        'filter_date_from': 'Datum von',
        'filter_clear': 'Filter zurücksetzen',
        'btn_equalize_columns': 'Breiten ausgleichen',
        'tt_equalize_columns': 'Alle Spalten auf die gleiche Breite setzen.',
        'filter_ext_all': 'Alle Erweiterungen',
        'tt_ext_filter_files_only': 'Der Erweiterungsfilter ist nur im Modus „Nur Dateien“ '
                                    'verfügbar.',
        'tt_size_filter_example': 'Zum Beispiel: 500 KB, 10 MB, 1.5 GB. Enter drücken',
        'calendar_btn': '...',
        'calendar_title': 'Datum wählen',
        'calendar_today': 'Heute',
        'calendar_prev_month': '←',
        'calendar_next_month': '→',
        'calendar_month_names': 'Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember',
        'calendar_weekday_names': 'Mo|Di|Mi|Do|Fr|Sa|So',
        'btn_mark_page': 'Alles auf Seite markieren',
        'btn_mark_all_pages': 'Alles auf allen Seiten markieren',
        'nothing_found_title': 'Nichts gefunden',
        'content_search_no_results_message': 'Im Dokumentinhalt wurde nichts gefunden. Wenn die Indizierung noch läuft, können die Ergebnisse später erscheinen.',
        'tt_search_mode_content_help': 'Die Inhaltssuche funktioniert mit PDF-, DOCX- und XLSX-Dateien. Ergebnisse erscheinen nur für bereits indizierte Dateien. Bei manchen PDFs hängt die Suche von eingebettetem Text oder OCR ab.',
        'search_failed_content': 'Die Inhaltssuche konnte nicht ausgeführt werden. Versuchen Sie eine Anfrage mit weniger Satzzeichen oder prüfen Sie, ob die Indizierung abgeschlossen ist.',
        'btn_mark_all': 'Alle markieren',
        'btn_unmark_all': 'Markierung aufheben',
        'btn_collect_checked': 'Markierte sammeln',
        'collect_files_title': 'Dateien sammeln',
        'collect_files_choose_dir': 'Zielordner wählen',
        'collect_files_none_selected': 'Nichts ausgewählt',
        'collect_files_result': 'Kopiert: {copied}\nÜbersprungen: {skipped}',
        'item_type_folder': 'Ordner',
        'item_type_file': 'Datei',
        'index_docs_title': 'Dokumente indexieren',
        'index_docs_prepare': 'Vorbereitung…',
        'index_mode_changed': 'Geändert',
        'index_mode_all': 'Alle',
        'index_mode_errors': 'Fehler',
        'btn_index_content': 'Dokumentinhalte indexieren',
        'help_index_content_title': 'Dokumentinhalte indexieren',
        'help_index_content_text': 'Erstellt einen Suchindex aus dem Text innerhalb von '
                                   'Dokumenten. Word, Excel und PDF werden unterstützt. Bei PDF '
                                   'mit schlechtem eingebettetem Text kann OCR verwendet werden, '
                                   'wenn content_runtime in der Nähe verfügbar ist. Je mehr '
                                   'Dokumente vorhanden sind, desto länger dauert der Vorgang.',
        'old_db_title': 'Alte Datenbank',
        'old_db_message': 'Diese Datenbank wurde mit einer älteren Version der Anwendung erstellt '
                          'und unterstützt die neuen Funktionen nicht.\n'
                          '\n'
                          'Fehlende Tabellen: {tables}\n'
                          '\n'
                          'Erstellen Sie mit der aktuellen Version des Programms eine neue '
                          'Datenbank.',
        'help_index_content_body': 'Erstellt oder aktualisiert einen Suchindex für Text innerhalb '
                                   'von Dokumenten.\n'
                                   '\n'
                                   'Word, Excel und PDF werden unterstützt. Bei PDF kann OCR '
                                   'verwendet werden, wenn der eingebettete Text schlecht ist und '
                                   'content_runtime verfügbar ist.\n'
                                   '\n'
                                   'Ein normaler Lauf arbeitet inkrementell: neue und geänderte '
                                   'Dokumente werden aktualisiert, ohne alles neu zu verarbeiten.',
        'index_docs_summary': 'Fertig. Verarbeitet: {processed}\n'
                              'Erfolgreich: {ok}\n'
                              'Fehler: {errors}',
        'index_docs_nothing_to_do': 'Keine neuen oder geänderten Dokumente zum Indizieren '
                                    'gefunden.',
        'save': 'Speichern',
        'open': 'Öffnen',
        'select': 'Auswählen',
        'path_dialog_title': 'Pfad auswählen',
        'path_dialog_location': 'Ordner:',
        'path_dialog_go': 'Gehe zu',
        'path_dialog_up': 'Nach oben',
        'path_dialog_name': 'Name',
        'path_dialog_type': 'Typ',
        'path_dialog_filename': 'Dateiname:',
        'path_dialog_current_folder': 'Aktueller Ordner:',
        'path_dialog_folder': 'Ordner',
        'path_dialog_file': 'Datei',
        'path_dialog_invalid_folder': 'Der angegebene Ordner ist nicht verfügbar.',
        'path_dialog_no_file_name': 'Bitte einen Dateinamen eingeben.',
        'path_dialog_file_missing': 'Die ausgewählte Datei wurde nicht gefunden.',
        'tray_restore': 'Wiederherstellen',
        'tray_hide_icon': 'Tray-Symbol ausblenden',
        'size_unit_b': 'B',
        'size_unit_kb': 'KB',
        'size_unit_mb': 'MB',
        'size_unit_gb': 'GB',
        'size_unit_tb': 'TB',
        'size_unit_pb': 'PB',
        'datetime_format': '%d.%m.%Y %H:%M',
        'content_source_docx': 'Word',
        'content_source_xlsx': 'Excel',
        'content_source_pdf_embedded': 'PDF (eingebetteter Text)',
        'content_source_pdf_ocr': 'PDF (OCR)',
        'content_source_pdf_mixed': 'PDF (gemischt)',
        'content_source_unknown': 'Unbekannt',
        'help': 'Hilfe',
        'unsupported_set_source_filetype': 'Es werden nur .txt und .xlsx/.xlsm/.xltx/.xltm '
                                           'unterstützt',
        'quick_start_title': 'Erste Schritte',
        'quick_start_text': '1. Öffnen Sie eine vorhandene Datenbank oder erstellen Sie eine '
                            'neue.\n'
                            '2. Wählen Sie für die Indizierung einen oder mehrere Ordner aus.\n'
                            '3. Für die Inhaltssuche ist eine vollständige Inhaltsindizierung '
                            'erforderlich.\n'
                            '4. Der Erweiterungsfilter funktioniert nur im Modus „Nur Dateien“.\n'
                            '5. Der Ordner content_runtime muss sich neben dem Programm befinden. Er wird für OCR von PDF-Dateien und die vollständige Indizierung ihres Inhalts benötigt.',
        'btn_hide': 'Ausblenden',
        'btn_show': 'Anzeigen'},
 'fr': {'done': 'Terminé',
        'csv_saved_msg': 'Lignes exportées : {n}\nFichier : {path}',
        'scan_mode_recursive': 'Analyse (avec sous-dossiers)',
        'scan_mode_norec': 'Analyse (dossier courant uniquement)',
        'stat_new': 'nv',
        'stat_updated': 'maj',
        'stat_skipped': 'ign',
        'stat_errors': 'err',
        'stat_sha1': 'SHA1',
        'app_title': 'Gestionnaire de base de fichiers',
        'app_subtitle': 'Indexer, rechercher et gérer des fichiers avec SQLite',
        'theme': 'Thème :',
        'language': 'Langue :',
        'info_text': '• Les dossiers système/masqués sont exclus automatiquement\n'
                     '• Double-clic dans la liste — afficher le fichier dans le dossier\n'
                     '• Ambigu : double-cliquez pour choisir',
        'scan_options': 'Options d’analyse',
        'incremental': 'Mise à jour incrémentielle',
        'calc_sha1': 'Calculer SHA1 (lent)',
        'include_subfolders': 'Inclure les sous-dossiers',
        'btn_build': 'Créer une nouvelle base depuis des dossiers',
        'btn_build_incremental': 'Mettre à jour une base existante depuis des dossiers',
        'btn_set': 'Créer/mettre à jour un ensemble (presse-papiers/txt/xlsx)',
        'btn_view': '👁️ Afficher la base',
        'btn_exit': 'Quitter',
        'btn_stop': 'Arrêter l’opération',
        'btn_background': 'Réduire dans la zone de notification',
        'confirm_stop_title': 'Confirmer l’arrêt',
        'confirm_stop_msg': 'Voulez-vous vraiment arrêter l’opération ?',
        'scan_close_running_title': 'Fenêtre d’opération',
        'scan_close_running_msg': 'L’opération est toujours en cours. Que voulez-vous faire ?',
        'status_ready': 'Prêt.',
        'status_stopping': 'Arrêt… (attendez la fin du lot actuel)',
        'status_scan': 'Analyse en cours…',
        'status_counting_title': 'Comptage des fichiers…',
        'status_counting_files': 'Comptage des fichiers… trouvés : {counted}',
        'status_sync': 'Synchronisation de l’ensemble…',
        'set_name_title': 'Nom de l’ensemble',
        'set_name_prompt': 'Saisissez un nom d’ensemble (par ex. Contrat_123) :',
        'set_name_empty': 'Veuillez saisir un nom d’ensemble.',
        'source_title': 'Source',
        'source_text': 'Choisissez la source de la liste des chemins :',
        'mode_title': 'Mode',
        'mode_text': 'Écraser entièrement l’ensemble existant ?\n'
                     'Oui = remplacer\n'
                     'Non = ajouter à l’ensemble existant',
        'empty_warning': 'Vide',
        'empty_text': 'Aucun chemin trouvé (presse-papiers/fichier vide).',
        'scan_complete': 'Analyse terminée',
        'scan_complete_msg': 'Fichiers traités : ',
        'set_created': 'Ensemble enregistré',
        'set_created_msg': ' éléments, trouvés : ',
        'choose_scan_folder_title': 'Sélectionner un dossier à analyser',
        'choose_scan_folders_title': 'Sélectionner des dossiers à analyser',
        'add_more_folders_title': 'Ajouter un autre dossier ?',
        'add_more_folders_text': 'Le dossier actuel a été ajouté. Voulez-vous ajouter un autre '
                                 'dossier à cette même base ?',
        'no_scan_folders_selected': 'Aucun dossier n’a été sélectionné pour l’analyse.',
        'multi_folder_prompt': 'Sélectionnez plusieurs dossiers à indexer dans une seule fenêtre. '
                               'Ajoutez les dossiers voulus à la liste, retirez ceux en trop, puis '
                               'lancez l’analyse.',
        'selected_folders_label': 'Dossiers sélectionnés',
        'selected_folders_count': 'Dossiers sélectionnés : {count}',
        'btn_add_folder': 'Ajouter un dossier',
        'btn_remove_selected_folder': 'Supprimer la sélection',
        'btn_clear_folders': 'Vider la liste',
        'btn_start_scan': 'Lancer l’indexation',
        'folder_already_added': 'Ce dossier est déjà dans la liste.',
        'scan_roots_label': 'Racines analysées :',
        'choose_db_save_title': 'Enregistrer la base (.db)',
        'choose_db_open_title': 'Ouvrir la base (.db)',
        'incremental_no_db_selected_title': 'Mise à jour incrémentielle',
        'incremental_no_db_selected_text': 'La mise à jour incrémentielle nécessite une base '
                                           'existante créée par ce programme.\n'
                                           '\n'
                                           "Si vous n'en avez pas encore, cliquez sur « Oui » pour "
                                           'créer une nouvelle base sans mise à jour '
                                           'incrémentielle.\n'
                                           'Si vous souhaitez revenir sans changement, cliquez sur '
                                           '« Non ».',
        'incremental_invalid_db_title': 'La base sélectionnée ne convient pas',
        'incremental_invalid_db_text': 'Cette base ne peut pas être utilisée pour une mise à jour '
                                       'incrémentielle.\n'
                                       '\n'
                                       'Raison : {reason}\n'
                                       '\n'
                                       'Cliquez sur « Oui » pour choisir une autre base '
                                       'existante.\n'
                                       'Cliquez sur « Non » pour créer une nouvelle base sans mise '
                                       'à jour incrémentielle.',
        'incremental_db_reason_missing': 'le fichier de base est introuvable',
        'incremental_db_reason_structure': 'le fichier ne contient pas la structure de base de ce '
                                           'programme (les tables files et meta sont requises)',
        'incremental_db_reason_sqlite': "le fichier n'a pas pu être ouvert comme base SQLite "
                                        'valide',
        'incremental_db_reason_unknown': "la structure de la base n'a pas pu être vérifiée",
        'choose_set_source_title': 'Source de la liste des chemins',
        'choose_set_source_paste': 'Coller depuis le presse-papiers',
        'choose_set_source_file': 'Choisir un fichier',
        'choose_set_source_cancel': 'Annuler',
        'status_found': 'Trouvé',
        'status_missing': 'Introuvable',
        'status_ambiguous': 'Ambigu',
        'theme_changed': 'Thème modifié',
        'theme_changed_msg': 'Thème appliqué : ',
        'lang_changed': 'Langue modifiée',
        'lang_changed_msg': 'Langue sélectionnée : ',
        'viewer_title': 'Vue de la base — ',
        'set_all': '(Tous)',
        'set_label': 'Ensemble :',
        'status_label': 'Statut :',
        'search_label': 'Recherche :',
        'search_btn': 'Rechercher',
        'tt_search_btn_filters': 'La recherche s’effectue sur la sélection filtrée actuelle. Par exemple, si PDF est choisi, les résultats ne seront recherchés que parmi les PDF.',
        'copy': 'Copier',
        'stop': 'Arrêter',
        'reset_btn': 'Réinitialiser',
        'only_existing': 'Uniquement les fichiers existants',
        'show_in_folder': 'Afficher dans le dossier',
        'resolve_ambiguous': 'Résoudre les éléments ambigus',
        'export_csv': 'Exporter en CSV',
        'close': 'Fermer',
        'first': '⏮ Début',
        'previous': '← Précédent',
        'next': 'Suivant →',
        'last': 'Fin ⏭',
        'of': 'sur',
        'searching': 'Recherche…',
        'header_name': 'Nom',
        'header_relpath': 'Chemin relatif / source',
        'header_size': 'Taille',
        'header_mtime': 'Modifié',
        'header_present': 'Présent',
        'header_status': 'Statut',
        'header_fullpath': 'Chemin complet / chemin associé',
        'resolve_title': 'Résoudre l’ambiguïté',
        'original_path': 'Chemin d’origine :',
        'candidates': 'Candidats par nom de fichier : ',
        'select_save': 'Sélectionner et enregistrer',
        'cancel': 'Annuler',
        'no_candidates': 'Aucun candidat',
        'no_candidates_msg': 'Aucun candidat trouvé. La base doit peut-être être mise à jour.',
        'no_selection': 'Aucune sélection',
        'no_selection_msg': 'Veuillez sélectionner un élément.',
        'error': 'Erreur',
        'warning': 'Avertissement',
        'info': 'Info',
        'empty_path': 'Chemin vide',
        'empty_path_msg': 'Aucun chemin de fichier sélectionné.',
        'file_not_found': 'Fichier introuvable',
        'file_not_found_msg': 'Fichier introuvable. Veuillez mettre à jour la base.\n'
                              '\n'
                              'Dossier ouvert :\n'
                              '\n',
        'show_in_folder_failed': 'Impossible d’afficher le fichier dans le dossier :\n{err}',
        'not_found': 'Introuvable',
        'not_found_msg': 'Fichier et dossier introuvables :\n\n',
        'save_report_title': 'Enregistrer le rapport',
        'save_report_btn': 'Enregistrer le rapport…',
        'filetype_text': 'Fichier texte',
        'filetype_all': 'Tous les fichiers',
        'report_saved_title': 'Rapport enregistré',
        'report_saved_msg': 'Rapport enregistré dans le fichier :\n{path}',
        'report_save_failed': 'Impossible d’enregistrer le rapport :\n{err}',
        'tt_incremental': 'S’applique uniquement au bouton « Créer/mettre à jour la base depuis '
                          'des dossiers ». Lorsqu’elle est activée, l’option met à jour une .db '
                          'existante : ajoute les nouveaux fichiers et marque les fichiers absents '
                          'comme « non présents sur le disque ». Les enregistrements ne sont pas '
                          'supprimés.',
        'tt_only_existing': 'Affiche uniquement les fichiers qui existent actuellement sur le '
                            'disque. Si vous avez supprimé des fichiers manuellement, mettez à '
                            'jour la base (mode incrémentiel).',
        'tt_sha1': 'SHA1 est la somme de contrôle d’un fichier. Aide à détecter les changements et '
                   'à trouver des doublons exacts. Ralentit nettement l’analyse.',
        'tt_recursive': 'Analyser également les sous-dossiers du dossier sélectionné.',
        'tt_help_btn': 'Ouvrir l’aide',
        'dialog_hint_open_file': 'La fenêtre système Windows de sélection de fichier va maintenant '
                                 's’ouvrir.',
        'dialog_hint_save_file': 'La fenêtre système Windows de choix de l’emplacement '
                                 'd’enregistrement va maintenant s’ouvrir.',
        'dialog_hint_select_folder': 'La fenêtre système Windows de sélection de dossier va '
                                     'maintenant s’ouvrir.',
        'warning_title': 'Avertissement',
        'warn_increment_off': 'Vous avez désactivé la mise à jour incrémentielle. La prochaine '
                              'analyse recréera la base à zéro (les anciens enregistrements seront '
                              'supprimés). Continuer ?',
        'warn_only_existing_on': 'Le filtre « Uniquement les fichiers existants » s’appuie sur les '
                                 'données de la base. Si vous avez supprimé des fichiers '
                                 'manuellement, il est recommandé de mettre la base à jour '
                                 '(incrémentielle). Activer ce filtre ?',
        'warn_sha1_on': 'Le calcul de SHA1 peut ralentir sensiblement l’analyse, surtout pour les '
                        'gros fichiers et les disques réseau/HDD. Activer SHA1 ?',
        'help_incremental_title': 'Mise à jour incrémentielle',
        'help_incremental_text': 'Cette option s’applique uniquement au bouton « Créer/mettre à '
                                 'jour la base depuis des dossiers ».\n'
                                 '\n'
                                 'Fonctionnement :\n'
                                 '• si le mode incrémentiel est activé, le programme vous demande '
                                 'd’ouvrir une .db existante à mettre à jour\n'
                                 '• les nouveaux fichiers sont ajoutés à la base\n'
                                 '• les fichiers supprimés du disque restent dans la base mais '
                                 'sont marqués comme « non présents sur le disque »\n'
                                 '• les fichiers modifiés sont mis à jour\n'
                                 '\n'
                                 'Si le mode incrémentiel est désactivé, le programme vous demande '
                                 'où enregistrer une nouvelle .db ou vous permet de recréer une '
                                 'base existante depuis zéro. Dans ce mode, la table des fichiers '
                                 'est reconstruite entièrement.\n'
                                 '\n'
                                 'Cette option ne s’applique pas aux boutons « Créer/mettre à jour '
                                 'un ensemble » ni « Afficher la base ».',
        'help_only_existing_title': 'Uniquement les fichiers existants',
        'help_only_existing_text': 'Ce filtre n’affiche que les fichiers marqués comme présents '
                                   'sur le disque dans la base.\n'
                                   '\n'
                                   'Si vous avez supprimé un fichier manuellement, la base le '
                                   'reflétera après une mise à jour incrémentielle.',
        'help_status_title': 'Filtre « Statut »',
        'help_status_text': 'Affiche les entrées par statut (utile pour les ensembles) :\n'
                            '\n'
                            '• (Tous) — sans filtre\n'
                            '• Trouvé — chemin associé et fichier trouvé\n'
                            '• Introuvable — fichier absent du disque\n'
                            '• Ambigu — plusieurs variantes trouvées, choix nécessaire\n'
                            '\n'
                            'Si (Tous) les ensembles est sélectionné, les statuts ne sont pas '
                            'utilisés.',
        'help_sha1_title': 'Calcul SHA1',
        'help_sha1_text': 'SHA1 est une « empreinte » du contenu du fichier (somme de contrôle).\n'
                          '\n'
                          'À quoi cela sert :\n'
                          '• contrôler les changements — des SHA1 différents signifient que le '
                          'fichier a changé\n'
                          '• rechercher des doublons exacts par contenu\n'
                          '\n'
                          'Inconvénient : SHA1 se calcule en lisant tout le fichier, ce qui peut '
                          'ralentir sensiblement l’analyse.',
        'help_title': 'Aide',
        'help_update_db_text': 'Si vous avez supprimé ou déplacé des fichiers sur le disque, la '
                               'base peut être obsolète.\n'
                               '\n'
                               '• Cliquez sur « Créer une base depuis des dossiers » et activez la '
                               '« mise à jour incrémentielle »\n'
                               '• Ou recréez la base\n'
                               '\n'
                               'Après la mise à jour, la recherche et « Afficher dans le dossier » '
                               'fonctionneront correctement.',
        'ok': 'J’ai compris',
        'yes': 'Oui',
        'no': 'Non',
        'error_title': 'Erreur',
        'help_btn_build_title': 'Créer / mettre à jour la base',
        'help_btn_build_text': 'Analyse les dossiers sélectionnés et crée ou met à jour la base de '
                               'fichiers SQLite.\n'
                               '\n'
                               'Étapes :\n'
                               '1) choisissez un ou plusieurs dossiers à analyser\n'
                               '2) si le mode incrémentiel est activé, ouvrez une .db existante à '
                               'mettre à jour\n'
                               '3) si le mode incrémentiel est désactivé, choisissez où '
                               'enregistrer une nouvelle .db ou recréez une base existante\n'
                               '\n'
                               'Ce bouton :\n'
                               '• ajoute les nouveaux fichiers\n'
                               '• met à jour les fichiers modifiés\n'
                               '• en mode incrémentiel, marque les fichiers supprimés comme '
                               'absents du disque\n'
                               '• avec le mode incrémentiel désactivé, reconstruit la table des '
                               'fichiers depuis zéro\n'
                               '\n'
                               'Les options ci-dessus influencent la vitesse et l’exhaustivité de '
                               'l’analyse.',
        'help_btn_set_title': 'Créer / mettre à jour un ensemble',
        'help_btn_set_text': 'Charge une liste de chemins depuis le presse-papiers, un fichier TXT '
                             'ou Excel et la compare à la base sélectionnée.\n'
                             '\n'
                             'Le résultat est enregistré comme ensemble nommé avec les statuts '
                             'Trouvé / Introuvable / Ambigu.',
        'help_btn_view_title': 'Afficher la base',
        'help_btn_view_text': 'Ouvre l’affichage de la base de données : recherche, filtres, export CSV, affichage du fichier dans le dossier et résolution manuelle des lignes ambiguës de l’ensemble.',
        'text_files_filetype': 'Fichiers texte',
        'text_excel_filetype': 'Texte/Excel',
        'excel_files_filetype': 'Fichiers Excel',
        'err_read_paths': 'Impossible de lire la liste des chemins :\n{err}',
        'err_open_db': 'Impossible d’ouvrir la base de données :\n{err}',
        'err_read_paths_generic': 'Impossible de lire la liste des chemins.',
        'err_open_db_generic': 'Impossible d’ouvrir la base de données.',
        'report_save_failed_generic': 'Impossible d’enregistrer le rapport.',
        'show_in_folder_failed_generic': 'Impossible d’afficher le fichier dans le dossier.',
        'search_failed_generic': 'Impossible d’effectuer la recherche.',
        'scan_failed_generic': 'L’analyse s’est terminée avec une erreur.',
        'set_sync_failed_generic': 'Impossible de créer ou de mettre à jour l’ensemble.',
        'resolve_need_specific_set': 'La résolution d’ambiguïté ne fonctionne que pour un ensemble '
                                     'sélectionné (pas « (Tous) »).',
        'resolve_row_not_ambiguous': 'La ligne sélectionnée n’a pas le statut « Ambigu ».',
        'resolve_no_service_data': 'Impossible de déterminer les données de service de la ligne '
                                   'sélectionnée.',
        'set_summary_full': 'Ensemble : {name}\n'
                            'Nombre total d’éléments : {total}\n'
                            'Trouvés : {found}\n'
                            'Introuvables : {missing}\n'
                            'Ambigus : {ambiguous}\n'
                            '\n'
                            'Étapes suivantes :\n'
                            '1) Ouvrez « Afficher la base ».\n'
                            '2) Sélectionnez l’ensemble « {name} ».\n'
                            '3) Pour les lignes au statut « Ambigu », double-cliquez et choisissez '
                            'le bon fichier.',
        'set_status_updated': 'Ensemble « {name} » mis à jour : {total} éléments (trouvés {found})',
        'set_toast_updated': 'Ensemble « {name} » : {total} él., trouvés {found}, ambigus '
                             '{ambiguous}',
        'confirm_title': 'Confirmation',
        'scan_report_summary': 'Résumé',
        'scan_report_folders': 'Dossiers',
        'scan_stopped_title': 'Opération arrêtée',
        'scan_stopped_msg': 'L’opération a été arrêtée par l’utilisateur.',
        'status_scan_stopped': 'Analyse arrêtée.',
        'export_csv_running': 'Export CSV en cours…',
        'export_csv_done': 'Export CSV terminé',
        'exit_scan_running_title': 'Fenêtre d’opération',
        'exit_scan_running_msg': 'Une opération est encore en cours. Que voulez-vous faire ?',
        'search_mode_fs': 'Fichiers et dossiers',
        'search_mode_content': 'Contenu des documents',
        'header_mark': 'Sélection',
        'header_source': 'Source',
        'header_snippet': 'Extrait',
        'item_kind_all': 'Tous les éléments',
        'item_kind_files': 'Fichiers uniquement',
        'item_kind_folders': 'Dossiers uniquement',
        'filter_ext': 'Ext.',
        'filter_size_from': 'Taille à partir de',
        'filter_to': 'à',
        'filter_date_from': 'Date à partir de',
        'filter_clear': 'Réinitialiser les filtres',
        'btn_equalize_columns': 'Égaliser la largeur',
        'tt_equalize_columns': 'Rendre toutes les colonnes de même largeur.',
        'filter_ext_all': 'Toutes les extensions',
        'tt_ext_filter_files_only': 'Le filtre par extension est disponible uniquement en mode « '
                                    'Fichiers uniquement ».',
        'tt_size_filter_example': 'Par exemple : 500 KB, 10 MB, 1.5 GB. Appuyez sur Entrée',
        'calendar_btn': '...',
        'calendar_title': 'Choisir une date',
        'calendar_today': 'Aujourd’hui',
        'calendar_prev_month': '←',
        'calendar_next_month': '→',
        'calendar_month_names': 'Janvier|Février|Mars|Avril|Mai|Juin|Juillet|Août|Septembre|Octobre|Novembre|Décembre',
        'calendar_weekday_names': 'Lun|Mar|Mer|Jeu|Ven|Sam|Dim',
        'btn_mark_all': 'Tout cocher',
        'nothing_found_title': 'Aucun résultat',
        'content_search_no_results_message': 'Aucun résultat n’a été trouvé dans le contenu des documents. Si l’indexation est encore en cours, les résultats peuvent apparaître plus tard.',
        'tt_search_mode_content_help': 'La recherche dans le contenu fonctionne avec les fichiers PDF, DOCX et XLSX. Les résultats n’apparaissent que pour les fichiers déjà indexés. Pour certains PDF, la recherche dépend du texte intégré ou de l’OCR.',
        'search_failed_content': 'La recherche dans le contenu n’a pas pu être exécutée. Essayez une requête avec moins de ponctuation ou vérifiez si l’indexation est terminée.',
        'btn_unmark_all': 'Tout décocher',
        'btn_collect_checked': 'Rassembler les cochés',
        'collect_files_title': 'Rassembler les fichiers',
        'collect_files_choose_dir': 'Choisir le dossier de destination',
        'collect_files_none_selected': 'Aucune sélection',
        'collect_files_result': 'Copiés : {copied}\nIgnorés : {skipped}',
        'item_type_folder': 'Dossier',
        'item_type_file': 'Fichier',
        'index_docs_title': 'Indexation des documents',
        'index_docs_prepare': 'Préparation…',
        'index_mode_changed': 'Modifiés',
        'index_mode_all': 'Tous',
        'index_mode_errors': 'Erreurs',
        'btn_index_content': 'Indexer le contenu des documents',
        'help_index_content_title': 'Indexer le contenu des documents',
        'help_index_content_text': 'Crée un index de recherche à partir du texte contenu dans les '
                                   'documents. Word, Excel et PDF sont pris en charge. Pour les '
                                   'PDF avec un texte intégré de mauvaise qualité, l’OCR peut être '
                                   'utilisé si content_runtime est disponible à proximité. Plus il '
                                   'y a de documents, plus l’opération est longue.',
        'old_db_title': 'Ancienne base de données',
        'old_db_message': 'Cette base de données a été créée avec une ancienne version de '
                          'l’application et ne prend pas en charge les nouvelles fonctions.\n'
                          '\n'
                          'Tables manquantes : {tables}\n'
                          '\n'
                          'Créez une nouvelle base avec la version actuelle de l’utilitaire.',
        'help_index_content_body': 'Crée ou met à jour un index de recherche pour le texte contenu '
                                   'dans les documents.\n'
                                   '\n'
                                   'Word, Excel et PDF sont pris en charge. Pour les PDF, l’OCR '
                                   'peut être utilisé si le texte intégré est de mauvaise qualité '
                                   'et si content_runtime est disponible.\n'
                                   '\n'
                                   'Un lancement normal fonctionne de manière incrémentielle : les '
                                   'documents nouveaux et modifiés sont mis à jour sans tout '
                                   'retraiter.',
        'index_docs_summary': 'Terminé. Traités : {processed}\nRéussis : {ok}\nErreurs : {errors}',
        'index_docs_nothing_to_do': "Aucun document nouveau ou modifié à indexer n'a été trouvé.",
        'save': 'Enregistrer',
        'open': 'Ouvrir',
        'select': 'Sélectionner',
        'path_dialog_title': 'Choisir un chemin',
        'path_dialog_location': 'Dossier :',
        'path_dialog_go': 'Aller',
        'path_dialog_up': 'Monter',
        'path_dialog_name': 'Nom',
        'path_dialog_type': 'Type',
        'path_dialog_filename': 'Nom du fichier :',
        'path_dialog_current_folder': 'Dossier actuel :',
        'path_dialog_folder': 'Dossier',
        'path_dialog_file': 'Fichier',
        'path_dialog_invalid_folder': 'Le dossier indiqué est indisponible.',
        'path_dialog_no_file_name': 'Saisissez un nom de fichier.',
        'path_dialog_file_missing': 'Le fichier sélectionné est introuvable.',
        'tray_restore': 'Restaurer',
        'tray_hide_icon': 'Masquer l’icône de la barre',
        'size_unit_b': 'o',
        'size_unit_kb': 'Ko',
        'size_unit_mb': 'Mo',
        'size_unit_gb': 'Go',
        'size_unit_tb': 'To',
        'size_unit_pb': 'Po',
        'datetime_format': '%d/%m/%Y %H:%M',
        'content_source_docx': 'Word',
        'content_source_xlsx': 'Excel',
        'content_source_pdf_embedded': 'PDF (texte intégré)',
        'content_source_pdf_ocr': 'PDF (OCR)',
        'content_source_pdf_mixed': 'PDF (mixte)',
        'content_source_unknown': 'Inconnu',
        'help': 'Aide',
        'unsupported_set_source_filetype': 'Seuls les formats .txt et .xlsx/.xlsm/.xltx/.xltm sont '
                                           'pris en charge',
        'quick_start_title': 'Pour commencer',
        'quick_start_text': '1. Ouvrez une base existante ou créez-en une nouvelle.\n'
                            '2. Pour l’indexation, choisissez un ou plusieurs dossiers.\n'
                            '3. Une indexation complète du contenu est nécessaire pour la '
                            'recherche dans le contenu.\n'
                            '4. Le filtre par extension fonctionne uniquement en mode « Fichiers '
                            'uniquement ».\n'
                            '5. Le dossier content_runtime doit se trouver à côté du programme. Il est nécessaire pour l’OCR des fichiers PDF et l’indexation complète de leur contenu.',
        'btn_hide': 'Masquer',
        'btn_show': 'Afficher'},
 'it': {'done': 'Completato',
        'csv_saved_msg': 'Righe esportate: {n}\nFile: {path}',
        'scan_mode_recursive': 'Scansione (con sottocartelle)',
        'scan_mode_norec': 'Scansione (solo cartella corrente)',
        'stat_new': 'nuov',
        'stat_updated': 'agg',
        'stat_skipped': 'salt',
        'stat_errors': 'err',
        'stat_sha1': 'SHA1',
        'app_title': 'Gestore database file',
        'app_subtitle': 'Indicizza, cerca e gestisci file con SQLite',
        'theme': 'Tema:',
        'language': 'Lingua:',
        'info_text': '• Le cartelle di sistema/nascoste vengono escluse automaticamente\n'
                     '• Doppio clic nell’elenco — mostra il file nella cartella\n'
                     '• Ambiguo: doppio clic per scegliere',
        'scan_options': 'Opzioni di scansione',
        'incremental': 'Aggiornamento incrementale',
        'calc_sha1': 'Calcola SHA1 (lento)',
        'include_subfolders': 'Includi sottocartelle',
        'btn_build': 'Crea nuovo database da cartelle',
        'btn_build_incremental': 'Aggiorna database esistente da cartelle',
        'btn_set': 'Crea/aggiorna set (appunti/txt/xlsx)',
        'btn_view': '👁️ Visualizza database',
        'btn_exit': 'Esci',
        'btn_stop': 'Ferma operazione',
        'btn_background': 'Riduci nella tray',
        'confirm_stop_title': 'Conferma arresto',
        'confirm_stop_msg': 'Vuoi davvero fermare l’operazione?',
        'scan_close_running_title': 'Finestra operazione',
        'scan_close_running_msg': 'L’operazione è ancora in corso. Cosa vuoi fare?',
        'status_ready': 'Pronto.',
        'status_stopping': 'Arresto… (attendere la fine del lotto corrente)',
        'status_scan': 'Scansione in corso…',
        'status_counting_title': 'Conteggio file…',
        'status_counting_files': 'Conteggio file… trovati: {counted}',
        'status_sync': 'Sincronizzazione set…',
        'set_name_title': 'Nome set',
        'set_name_prompt': 'Inserisci un nome per il set (es. Contratto_123):',
        'set_name_empty': 'Inserisci un nome per il set.',
        'source_title': 'Origine',
        'source_text': 'Scegli l’origine dell’elenco percorsi:',
        'mode_title': 'Modalità',
        'mode_text': 'Sovrascrivere completamente il set esistente?\n'
                     'Sì = sostituisci\n'
                     'No = aggiungi al set esistente',
        'empty_warning': 'Vuoto',
        'empty_text': 'Nessun percorso trovato (appunti/file vuoto).',
        'scan_complete': 'Scansione completata',
        'scan_complete_msg': 'File elaborati: ',
        'set_created': 'Set salvato',
        'set_created_msg': ' elementi, trovati: ',
        'choose_scan_folder_title': 'Seleziona cartella da scansionare',
        'choose_scan_folders_title': 'Seleziona cartelle da scansionare',
        'add_more_folders_title': 'Aggiungere un’altra cartella?',
        'add_more_folders_text': 'La cartella corrente è stata aggiunta. Vuoi aggiungere un’altra '
                                 'cartella allo stesso database?',
        'no_scan_folders_selected': 'Non sono state selezionate cartelle da scansionare.',
        'multi_folder_prompt': 'Seleziona più cartelle da indicizzare in un’unica finestra. '
                               'Aggiungi alla lista le cartelle necessarie, rimuovi quelle '
                               'superflue e avvia la scansione.',
        'selected_folders_label': 'Cartelle selezionate',
        'selected_folders_count': 'Cartelle selezionate: {count}',
        'btn_add_folder': 'Aggiungi cartella',
        'btn_remove_selected_folder': 'Rimuovi selezione',
        'btn_clear_folders': 'Svuota elenco',
        'btn_start_scan': 'Avvia indicizzazione',
        'folder_already_added': 'Questa cartella è già presente nell’elenco.',
        'scan_roots_label': 'Radici di scansione:',
        'choose_db_save_title': 'Salva database (.db)',
        'choose_db_open_title': 'Apri database (.db)',
        'incremental_no_db_selected_title': 'Aggiornamento incrementale',
        'incremental_no_db_selected_text': "Per l'aggiornamento incrementale serve un database "
                                           'esistente creato da questo programma.\n'
                                           '\n'
                                           'Se non ne hai ancora uno, fai clic su « Sì » per '
                                           'creare un nuovo database senza aggiornamento '
                                           'incrementale.\n'
                                           'Se vuoi tornare indietro senza modifiche, fai clic su '
                                           '« No ».',
        'incremental_invalid_db_title': 'Il database selezionato non è adatto',
        'incremental_invalid_db_text': "Questo database non può essere usato per l'aggiornamento "
                                       'incrementale.\n'
                                       '\n'
                                       'Motivo: {reason}\n'
                                       '\n'
                                       'Fai clic su « Sì » per scegliere un altro database '
                                       'esistente.\n'
                                       'Fai clic su « No » per creare un nuovo database senza '
                                       'aggiornamento incrementale.',
        'incremental_db_reason_missing': 'il file del database non è stato trovato',
        'incremental_db_reason_structure': 'il file non contiene la struttura del database di '
                                           'questo programma (sono richieste le tabelle files e '
                                           'meta)',
        'incremental_db_reason_sqlite': 'il file non è stato aperto come database SQLite valido',
        'incremental_db_reason_unknown': 'non è stato possibile verificare la struttura del '
                                         'database',
        'choose_set_source_title': 'Origine elenco percorsi',
        'choose_set_source_paste': 'Incolla dagli appunti',
        'choose_set_source_file': 'Seleziona file',
        'choose_set_source_cancel': 'Annulla',
        'status_found': 'Trovato',
        'status_missing': 'Non trovato',
        'status_ambiguous': 'Ambiguo',
        'theme_changed': 'Tema cambiato',
        'theme_changed_msg': 'Tema applicato: ',
        'lang_changed': 'Lingua cambiata',
        'lang_changed_msg': 'Lingua selezionata: ',
        'viewer_title': 'Visualizza database — ',
        'set_all': '(Tutti)',
        'set_label': 'Insieme:',
        'status_label': 'Stato:',
        'search_label': 'Ricerca:',
        'search_btn': 'Cerca',
        'tt_search_btn_filters': 'La ricerca viene eseguita sulla selezione corrente filtrata. Per esempio, se è selezionato PDF, i risultati verranno cercati solo tra i PDF.',
        'copy': 'Copia',
        'stop': 'Ferma',
        'reset_btn': 'Reimposta',
        'only_existing': 'Solo file esistenti',
        'show_in_folder': 'Mostra nella cartella',
        'resolve_ambiguous': 'Risolvi elementi ambigui',
        'export_csv': 'Esporta in CSV',
        'close': 'Chiudi',
        'first': '⏮ Inizio',
        'previous': '← Indietro',
        'next': 'Avanti →',
        'last': 'Fine ⏭',
        'of': 'di',
        'searching': 'Ricerca…',
        'header_name': 'Nome',
        'header_relpath': 'Percorso relativo / origine',
        'header_size': 'Dimensione',
        'header_mtime': 'Modificato',
        'header_present': 'Presente',
        'header_status': 'Stato',
        'header_fullpath': 'Percorso completo / percorso associato',
        'resolve_title': 'Risolvi ambiguità',
        'original_path': 'Percorso originale:',
        'candidates': 'Candidati per nome file: ',
        'select_save': 'Seleziona e salva',
        'cancel': 'Annulla',
        'no_candidates': 'Nessun candidato',
        'no_candidates_msg': 'Nessun candidato trovato. Potrebbe essere necessario aggiornare il '
                             'database.',
        'no_selection': 'Nessuna selezione',
        'no_selection_msg': 'Seleziona un elemento.',
        'error': 'Errore',
        'warning': 'Avviso',
        'info': 'Informazione',
        'empty_path': 'Percorso vuoto',
        'empty_path_msg': 'Nessun percorso file selezionato.',
        'file_not_found': 'File non trovato',
        'file_not_found_msg': 'File non trovato. Aggiorna il database.\n\nCartella aperta:\n\n',
        'show_in_folder_failed': 'Impossibile mostrare il file nella cartella:\n{err}',
        'not_found': 'Non trovato',
        'not_found_msg': 'File e cartella non trovati:\n\n',
        'save_report_title': 'Salva report',
        'save_report_btn': 'Salva report…',
        'filetype_text': 'File di testo',
        'filetype_all': 'Tutti i file',
        'report_saved_title': 'Report salvato',
        'report_saved_msg': 'Report salvato nel file:\n{path}',
        'report_save_failed': 'Impossibile salvare il report:\n{err}',
        'tt_incremental': 'Si applica solo al pulsante « Crea/aggiorna database da cartelle ». '
                          'Quando è attiva, aggiorna una .db esistente: aggiunge i nuovi file e '
                          'contrassegna quelli mancanti come « non presenti sul disco ». I record '
                          'non vengono eliminati.',
        'tt_only_existing': 'Mostra solo i file attualmente esistenti sul disco. Se hai eliminato '
                            'manualmente dei file, aggiorna il database (incrementale).',
        'tt_sha1': 'SHA1 è il checksum di un file. Aiuta a rilevare modifiche e a trovare '
                   'duplicati esatti. Rallenta sensibilmente la scansione.',
        'tt_recursive': 'Scansiona anche le sottocartelle della cartella selezionata.',
        'tt_help_btn': 'Apri aiuto',
        'dialog_hint_open_file': 'Si aprirà ora la finestra di sistema Windows per scegliere un '
                                 'file.',
        'dialog_hint_save_file': 'Si aprirà ora la finestra di sistema Windows per scegliere dove '
                                 'salvare il file.',
        'dialog_hint_select_folder': 'Si aprirà ora la finestra di sistema Windows per scegliere '
                                     'una cartella.',
        'warning_title': 'Avviso',
        'warn_increment_off': 'Hai disattivato l’aggiornamento incrementale. La prossima scansione '
                              'ricreerà il database da zero (i vecchi record verranno rimossi). '
                              'Continuare?',
        'warn_only_existing_on': 'Il filtro «Solo esistenti su disco» usa i dati del database. Se '
                                 'hai eliminato manualmente dei file, è consigliato aggiornare il '
                                 'database (incrementale). Attivare il filtro?',
        'warn_sha1_on': 'Il calcolo di SHA1 può rallentare sensibilmente la scansione, soprattutto '
                        'con file grandi e cartelle HDD/rete. Attivare SHA1?',
        'help_incremental_title': 'Aggiornamento incrementale',
        'help_incremental_text': 'Questa opzione si applica solo al pulsante « Crea/aggiorna '
                                 'database da cartelle ».\n'
                                 '\n'
                                 'Come funziona:\n'
                                 '• quando la modalità incrementale è attiva, il programma chiede '
                                 'di aprire una .db esistente da aggiornare\n'
                                 '• i nuovi file vengono aggiunti al database\n'
                                 '• i file rimossi dal disco restano nel database ma vengono '
                                 'contrassegnati come « non presenti sul disco »\n'
                                 '• i file modificati vengono aggiornati\n'
                                 '\n'
                                 'Se la modalità incrementale è disattivata, il programma chiede '
                                 'dove salvare una nuova .db oppure consente di ricreare da zero '
                                 'un database esistente. In questa modalità la tabella dei file '
                                 'viene ricostruita da zero.\n'
                                 '\n'
                                 'Questa opzione non si applica ai pulsanti « Crea/aggiorna set » '
                                 'e « Visualizza database ».',
        'help_only_existing_title': 'Solo esistenti su disco',
        'help_only_existing_text': 'Questo filtro mostra solo i file contrassegnati come esistenti '
                                   'sul disco nel database.\n'
                                   '\n'
                                   'Se hai eliminato manualmente un file, il database lo '
                                   'rifletterà dopo un aggiornamento incrementale.',
        'help_status_title': 'Filtro «Stato»',
        'help_status_text': 'Mostra le voci per stato (utile per gli insiemi):\n'
                            '\n'
                            '• (Tutti) — nessun filtro\n'
                            '• Trovato — percorso associato e file trovato\n'
                            '• Non trovato — file assente sul disco\n'
                            '• Ambiguo — trovate più varianti, è necessaria una scelta\n'
                            '\n'
                            'Se è selezionato (Tutti) gli insiemi, gli stati non vengono usati.',
        'help_sha1_title': 'Calcolo SHA1',
        'help_sha1_text': 'SHA1 è una “impronta” del contenuto del file (checksum).\n'
                          '\n'
                          'A cosa serve:\n'
                          '• controllare le modifiche — SHA1 diversi significano che il file è '
                          'cambiato\n'
                          '• trovare duplicati esatti in base al contenuto\n'
                          '\n'
                          'Svantaggio: SHA1 viene calcolato leggendo l’intero file, quindi la '
                          'scansione può diventare sensibilmente più lenta.',
        'help_title': 'Aiuto',
        'help_update_db_text': 'Se hai eliminato o spostato file sul disco, il database potrebbe '
                               'non essere aggiornato.\n'
                               '\n'
                               '• Fai clic su «Crea database dalle cartelle» e attiva '
                               '«Aggiornamento incrementale»\n'
                               '• Oppure ricrea il database\n'
                               '\n'
                               'Dopo l’aggiornamento, la ricerca e «Mostra nella cartella» '
                               'funzioneranno correttamente.',
        'ok': 'Ho capito',
        'yes': 'Sì',
        'no': 'No',
        'error_title': 'Errore',
        'help_btn_build_title': 'Crea / aggiorna database',
        'help_btn_build_text': 'Esegue la scansione delle cartelle selezionate e crea o aggiorna '
                               'il database SQLite dei file.\n'
                               '\n'
                               'Procedura:\n'
                               '1) scegli una o più cartelle da scansionare\n'
                               '2) se la modalità incrementale è attiva, apri una .db esistente da '
                               'aggiornare\n'
                               '3) se la modalità incrementale è disattivata, scegli dove salvare '
                               'una nuova .db oppure ricrea un database esistente\n'
                               '\n'
                               'Questo pulsante:\n'
                               '• aggiunge nuovi file\n'
                               '• aggiorna i file modificati\n'
                               '• in modalità incrementale, contrassegna come assenti dal disco i '
                               'file rimossi\n'
                               '• con la modalità incrementale disattivata, ricostruisce da zero '
                               'la tabella dei file\n'
                               '\n'
                               'Le opzioni sopra influiscono sulla velocità e sulla completezza '
                               'della scansione.',
        'help_btn_set_title': 'Crea / aggiorna insieme',
        'help_btn_set_text': 'Carica un elenco di percorsi dagli appunti, da TXT o da Excel e lo '
                             'confronta con il database selezionato.\n'
                             '\n'
                             'Il risultato viene salvato come insieme con stati Trovato / Non '
                             'trovato / Ambiguo.',
        'help_btn_view_title': 'Visualizza database',
        'help_btn_view_text': 'Apre il visualizzatore del database: ricerca, filtri, esportazione CSV, mostra il file nella cartella e risoluzione manuale delle righe ambigue del set.',
        'text_files_filetype': 'File di testo',
        'text_excel_filetype': 'Testo/Excel',
        'excel_files_filetype': 'File Excel',
        'err_read_paths': 'Impossibile leggere l’elenco dei percorsi:\n{err}',
        'err_open_db': 'Impossibile aprire il database:\n{err}',
        'err_read_paths_generic': 'Impossibile leggere l’elenco dei percorsi.',
        'err_open_db_generic': 'Impossibile aprire il database.',
        'report_save_failed_generic': 'Impossibile salvare il report.',
        'show_in_folder_failed_generic': 'Impossibile mostrare il file nella cartella.',
        'search_failed_generic': 'Impossibile eseguire la ricerca.',
        'scan_failed_generic': 'La scansione è terminata con un errore.',
        'set_sync_failed_generic': 'Impossibile creare o aggiornare l’insieme.',
        'resolve_need_specific_set': 'La risoluzione dell’ambiguità funziona solo per un insieme '
                                     'selezionato (non «(Tutti)»).',
        'resolve_row_not_ambiguous': 'La riga selezionata non ha lo stato «Ambiguo».',
        'resolve_no_service_data': 'Impossibile determinare i dati di servizio della riga '
                                   'selezionata.',
        'set_summary_full': 'Insieme: {name}\n'
                            'Elementi totali: {total}\n'
                            'Trovati: {found}\n'
                            'Non trovati: {missing}\n'
                            'Ambigui: {ambiguous}\n'
                            '\n'
                            'Passi successivi:\n'
                            '1) Apri «Visualizza database».\n'
                            '2) Seleziona l’insieme «{name}».\n'
                            '3) Per le righe con stato «Ambiguo», fai doppio clic e scegli il file '
                            'corretto.',
        'set_status_updated': 'Insieme «{name}» aggiornato: {total} elementi (trovati {found})',
        'set_toast_updated': 'Insieme «{name}»: {total} elem., trovati {found}, ambigui '
                             '{ambiguous}',
        'confirm_title': 'Conferma',
        'scan_report_summary': 'Riepilogo',
        'scan_report_folders': 'Cartelle',
        'scan_stopped_title': 'Operazione interrotta',
        'scan_stopped_msg': 'L’operazione è stata interrotta dall’utente.',
        'status_scan_stopped': 'Scansione interrotta.',
        'export_csv_running': 'Esportazione CSV in corso…',
        'export_csv_done': 'Esportazione CSV completata',
        'exit_scan_running_title': 'Finestra operazione',
        'exit_scan_running_msg': 'È ancora in corso un’operazione. Cosa vuoi fare?',
        'search_mode_fs': 'File e cartelle',
        'search_mode_content': 'Contenuto dei documenti',
        'header_mark': 'Selezione',
        'header_source': 'Origine',
        'header_snippet': 'Estratto',
        'item_kind_all': 'Tutti gli elementi',
        'item_kind_files': 'Solo file',
        'item_kind_folders': 'Solo cartelle',
        'filter_ext': 'Est.',
        'filter_size_from': 'Dimensione da',
        'filter_to': 'a',
        'filter_date_from': 'Data da',
        'filter_clear': 'Reimposta filtri',
        'btn_equalize_columns': 'Uniforma larghezze',
        'tt_equalize_columns': 'Rende tutte le colonne della stessa larghezza.',
        'filter_ext_all': 'Tutte le estensioni',
        'tt_ext_filter_files_only': 'Il filtro per estensione è disponibile solo nella modalità « '
                                    'Solo file ».',
        'tt_size_filter_example': 'Per esempio: 500 KB, 10 MB, 1.5 GB. Premi Invio',
        'calendar_btn': '...',
        'calendar_title': 'Scegli data',
        'calendar_today': 'Oggi',
        'calendar_prev_month': '←',
        'calendar_next_month': '→',
        'calendar_month_names': 'Gennaio|Febbraio|Marzo|Aprile|Maggio|Giugno|Luglio|Agosto|Settembre|Ottobre|Novembre|Dicembre',
        'calendar_weekday_names': 'Lun|Mar|Mer|Gio|Ven|Sab|Dom',
        'btn_mark_page': 'Seleziona tutto nella pagina',
        'btn_mark_all_pages': 'Seleziona tutto in tutte le pagine',
        'nothing_found_title': 'Nessun risultato',
        'content_search_no_results_message': 'Nel contenuto dei documenti non è stato trovato nulla. Se l’indicizzazione è ancora in corso, i risultati potrebbero comparire più tardi.',
        'tt_search_mode_content_help': 'La ricerca nel contenuto funziona con file PDF, DOCX e XLSX. I risultati appaiono solo per i file già indicizzati. Per alcuni PDF, la ricerca dipende dal testo incorporato o dall’OCR.',
        'search_failed_content': 'Impossibile completare la ricerca nel contenuto. Prova una query con meno segni di punteggiatura oppure controlla se l’indicizzazione è terminata.',
        'btn_mark_all': 'Seleziona tutto',
        'btn_unmark_all': 'Deseleziona tutto',
        'btn_collect_checked': 'Raccogli selezionati',
        'collect_files_title': 'Raccolta file',
        'collect_files_choose_dir': 'Scegli la cartella di destinazione',
        'collect_files_none_selected': 'Niente selezionato',
        'collect_files_result': 'Copiati: {copied}\nSaltati: {skipped}',
        'item_type_folder': 'Cartella',
        'item_type_file': 'File',
        'index_docs_title': 'Indicizzazione documenti',
        'index_docs_prepare': 'Preparazione…',
        'index_mode_changed': 'Modificati',
        'index_mode_all': 'Tutti',
        'index_mode_errors': 'Errori',
        'btn_index_content': 'Indicizza contenuto documenti',
        'help_index_content_title': 'Indicizza contenuto documenti',
        'help_index_content_text': 'Crea un indice di ricerca del testo all’interno dei documenti. '
                                   'Sono supportati Word, Excel e PDF. Per i PDF con testo '
                                   'incorporato di scarsa qualità può essere usato l’OCR, se '
                                   'content_runtime è disponibile accanto all’applicazione. Più '
                                   'documenti ci sono, più l’operazione richiederà tempo.',
        'old_db_title': 'Vecchio database',
        'old_db_message': 'Questo database è stato creato con una versione precedente '
                          'dell’applicazione e non supporta le nuove funzioni.\n'
                          '\n'
                          'Tabelle mancanti: {tables}\n'
                          '\n'
                          'Crea un nuovo database con la versione corrente dell’utilità.',
        'help_index_content_body': 'Crea o aggiorna un indice di ricerca per il testo contenuto '
                                   'nei documenti.\n'
                                   '\n'
                                   'Sono supportati Word, Excel e PDF. Per i PDF può essere usato '
                                   'l’OCR quando il testo incorporato è di bassa qualità e '
                                   'content_runtime è disponibile.\n'
                                   '\n'
                                   'L’esecuzione normale è incrementale: aggiorna i documenti '
                                   'nuovi e modificati senza rielaborare tutto.',
        'index_docs_summary': 'Completato. Elaborati: {processed}\n'
                              'Riusciti: {ok}\n'
                              'Errori: {errors}',
        'index_docs_nothing_to_do': 'Non sono stati trovati documenti nuovi o modificati da '
                                    'indicizzare.',
        'save': 'Salva',
        'open': 'Apri',
        'select': 'Seleziona',
        'path_dialog_title': 'Scegli percorso',
        'path_dialog_location': 'Cartella:',
        'path_dialog_go': 'Vai',
        'path_dialog_up': 'Su',
        'path_dialog_name': 'Nome',
        'path_dialog_type': 'Tipo',
        'path_dialog_filename': 'Nome file:',
        'path_dialog_current_folder': 'Cartella corrente:',
        'path_dialog_folder': 'Cartella',
        'path_dialog_file': 'File',
        'path_dialog_invalid_folder': 'La cartella indicata non è disponibile.',
        'path_dialog_no_file_name': 'Inserisci un nome file.',
        'path_dialog_file_missing': 'Il file selezionato non è stato trovato.',
        'tray_restore': 'Ripristina',
        'tray_hide_icon': 'Nascondi icona nell’area di notifica',
        'size_unit_b': 'B',
        'size_unit_kb': 'KB',
        'size_unit_mb': 'MB',
        'size_unit_gb': 'GB',
        'size_unit_tb': 'TB',
        'size_unit_pb': 'PB',
        'datetime_format': '%d/%m/%Y %H:%M',
        'content_source_docx': 'Word',
        'content_source_xlsx': 'Excel',
        'content_source_pdf_embedded': 'PDF (testo incorporato)',
        'content_source_pdf_ocr': 'PDF (OCR)',
        'content_source_pdf_mixed': 'PDF (misto)',
        'content_source_unknown': 'Sconosciuto',
        'help': 'Aiuto',
        'unsupported_set_source_filetype': 'Sono supportati solo i file .txt e '
                                           '.xlsx/.xlsm/.xltx/.xltm',
        'quick_start_title': 'Per iniziare',
        'quick_start_text': '1. Apri un database esistente o creane uno nuovo.\n'
                            '2. Per l’indicizzazione scegli una o più cartelle.\n'
                            '3. Per la ricerca nel contenuto è necessaria un’indicizzazione '
                            'completa del contenuto.\n'
                            '4. Il filtro per estensione funziona solo nella modalità «Solo '
                            'file».\n'
                            '5. La cartella content_runtime deve trovarsi accanto al programma. Serve per l’OCR dei file PDF e per l’indicizzazione completa del loro contenuto.',
        'btn_hide': 'Nascondi',
        'btn_show': 'Mostra'},
 'rm': {'done': 'Finì',
        'csv_saved_msg': 'Lingias exportadas: {n}\nDatoteca: {path}',
        'scan_mode_recursive': 'Scansiun (cun sutdossiers)',
        'scan_mode_norec': 'Scansiun (mo il dossier actual)',
        'stat_new': 'nov',
        'stat_updated': 'act',
        'stat_skipped': 'surpass',
        'stat_errors': 'err',
        'stat_sha1': 'SHA1',
        'app_title': 'Manager da banca da datotecas',
        'app_subtitle': 'Indexar, tschertgar e administrar datotecas cun SQLite',
        'theme': 'Tema:',
        'language': 'Lingua:',
        'info_text': '• Dossiers da sistem/zuppads vegnan exclus automaticamain\n'
                     '• Dubel clic en la glista — mussar il file en il dossier\n'
                     '• Ambigu: dubel clic per tscherner',
        'scan_options': 'Opziuns da scansiun',
        'incremental': 'Actualisaziun incrementala',
        'calc_sha1': 'Calcular SHA1 (plaun)',
        'include_subfolders': 'Includer sutordinaturs',
        'btn_build': 'Crear ina nova banca da novitads ord ordinaturs',
        'btn_build_incremental': 'Actualisar ina banca da novitads existenta ord ordinaturs',
        'btn_set': 'Crear/actualisar set (clipboard/txt/xlsx)',
        'btn_view': '👁️ Mussar la banca da novitads',
        'btn_exit': 'Sortir',
        'btn_stop': 'Fermer l’operaziun',
        'btn_background': 'Minimisar en la zona da notificaziun',
        'confirm_stop_title': 'Confermar l’arrest',
        'confirm_stop_msg': 'Vuls ti propi fermar l’operaziun?',
        'scan_close_running_title': 'Fanestra da l’operaziun',
        'scan_close_running_msg': 'L’operaziun è anc en curs. Tge vulais far?',
        'status_ready': 'Pront.',
        'status_stopping': 'Fermar… (spetgai la fin dal pachet actual)',
        'status_scan': 'Scansiun en curs…',
        'status_counting_title': 'Quintar files…',
        'status_counting_files': 'Quintar files… chattads: {counted}',
        'status_sync': 'Set vegn sincronisà…',
        'set_name_title': 'Num dal set',
        'set_name_prompt': 'Endatescha in num dal set (p.ex. Contract_123):',
        'set_name_empty': 'Endatescha in num dal set.',
        'source_title': 'Funtauna',
        'source_text': 'Tscherna la funtauna da la glista da vias:',
        'mode_title': 'Moda',
        'mode_text': 'Surdar cumplettamain il set existent?\n'
                     'Gea = remplazzar\n'
                     'Na = agiuntar al set existent',
        'empty_warning': 'Vid',
        'empty_text': 'Nagins viadis chattads (clipboard/datoteca vida).',
        'scan_complete': 'Scanning terminà',
        'scan_complete_msg': 'Datotecas elaboradas: ',
        'set_created': 'Set memorisà',
        'set_created_msg': ' elements, chattads: ',
        'choose_scan_folder_title': 'Tscherner ordinatur per scannar',
        'choose_scan_folders_title': 'Tscherner ordinaturs per scannar',
        'add_more_folders_title': 'Agiuntar anc in ordinatur?',
        'add_more_folders_text': 'L’ordinatur actual è vegnì agiuntà. Vulais agiuntar anc in '
                                 'ordinatur a la medema banca da novitads?',
        'no_scan_folders_selected': 'Nagins ordinaturs tschernids per la scansiun.',
        'multi_folder_prompt': 'Tscherna plirs ordinaturs per l’indexaziun en ina suletta '
                               'fanestra. Agiunta ils ordinaturs necessaris a la glista, stizza '
                               'quels surflus e lantscha la scansiun.',
        'selected_folders_label': 'Ordinaturs tschernids',
        'selected_folders_count': 'Ordinaturs tschernids: {count}',
        'btn_add_folder': 'Agiuntar ordinatur',
        'btn_remove_selected_folder': 'Allontanar selecziun',
        'btn_clear_folders': 'Svidar glista',
        'btn_start_scan': 'Lantschar indexaziun',
        'folder_already_added': 'Quest ordinatur è gia en la glista.',
        'scan_roots_label': 'Ragischs da scansiun:',
        'choose_db_save_title': 'Memorisar la banca da novitads (.db)',
        'choose_db_open_title': 'Avrir la banca da novitads (.db)',
        'incremental_no_db_selected_title': 'Actualisaziun incrementala',
        'incremental_no_db_selected_text': "Per l'actualisaziun incrementala dovraziuns ina banca "
                                           'da novitads existenta creada da quest program.\n'
                                           '\n'
                                           "Sche Vus n'avais anc nagina, cliccai sin « Gea » per "
                                           'crear ina nova banca da novitads senza actualisaziun '
                                           'incrementala.\n'
                                           'Sche Vus vulais turnar enavos senza novitads, cliccai '
                                           'sin « Na ».',
        'incremental_invalid_db_title': 'La banca da novitads tschernida na va betg',
        'incremental_invalid_db_text': 'Questa banca da novitads na po betg vegnir duvrada per '
                                       "l'actualisaziun incrementala.\n"
                                       '\n'
                                       'Motiv: {reason}\n'
                                       '\n'
                                       "Cliccai sin « Gea » per tscherner in'autra banca da "
                                       'novitads existenta.\n'
                                       'Cliccai sin « Na » per crear ina nova banca da novitads '
                                       'senza actualisaziun incrementala.',
        'incremental_db_reason_missing': 'il file da la banca da novitads na è betg vegnì chattà',
        'incremental_db_reason_structure': 'il file na cuntegna betg la structura da banca da '
                                           'novitads da quest program (las tabellas files e meta '
                                           'èn necessarias)',
        'incremental_db_reason_sqlite': 'il file na po betg vegnir avert sco banca SQLite valida',
        'incremental_db_reason_unknown': 'la structura da la banca da novitads na pudeva betg '
                                         'vegnir verifitgada',
        'choose_set_source_title': 'Funtauna da la glista da vias',
        'choose_set_source_paste': 'Encollar dal buffer',
        'choose_set_source_file': 'Tscherner ina datoteca',
        'choose_set_source_cancel': 'Interrumper',
        'status_found': 'Chattà',
        'status_missing': 'Betg chattà',
        'status_ambiguous': 'Ambigu',
        'theme_changed': 'Tema midà',
        'theme_changed_msg': 'Tema applicà: ',
        'lang_changed': 'Lingua midada',
        'lang_changed_msg': 'Lingua tschernida: ',
        'viewer_title': 'Vista da la banca — ',
        'set_all': '(Tut)',
        'set_label': 'Set:',
        'status_label': 'Status:',
        'search_label': 'Tschertga:',
        'search_btn': 'Tschertgar',
        'tt_search_btn_filters': 'La tschertga vegn exequida sin la selecziun actuala filtrada. Per exempel, sche PDF è tschernì, vegnan tschertgads mo PDFs.',
        'copy': 'Copiar',
        'stop': 'Stop',
        'reset_btn': 'Reinizialisar',
        'only_existing': 'Mo datotecas existentas',
        'show_in_folder': 'Mussar en l’ordinatur',
        'resolve_ambiguous': 'Schliar ils elements ambigus',
        'export_csv': 'Exportar sco CSV',
        'close': 'Serrar',
        'first': '⏮ A l’entschatta',
        'previous': '← Enavos',
        'next': 'Enavant →',
        'last': 'A la fin ⏭',
        'of': 'da',
        'searching': 'Tschertga…',
        'header_name': 'Num',
        'header_relpath': 'Via relativa / funtauna',
        'header_size': 'Grondezza',
        'header_mtime': 'Midà',
        'header_present': 'Preschent',
        'header_status': 'Status',
        'header_fullpath': 'Via cumpletta / via associada',
        'resolve_title': 'Schliar l’ambiguitad',
        'original_path': 'Via originala:',
        'candidates': 'Candidats tenor num da datoteca: ',
        'select_save': 'Tscherner e memorisar',
        'cancel': 'Interrumper',
        'no_candidates': 'Nagin candidat',
        'no_candidates_msg': 'Nagins candidats chattads. La banca sto eventualmain vegnir '
                             'actualisada.',
        'no_selection': 'Nagina selecziun',
        'no_selection_msg': 'Tscherna per plaschair in element.',
        'error': 'Errur',
        'warning': 'Avis',
        'info': 'Infurmaziun',
        'empty_path': 'Via vida',
        'empty_path_msg': 'Nagina via da datoteca tschernida.',
        'file_not_found': 'Datoteca betg chattada',
        'file_not_found_msg': 'Datoteca betg chattada. Actualisescha per plaschair la banca.\n'
                              '\n'
                              'Ordinatur avert:\n'
                              '\n',
        'show_in_folder_failed': 'Impussibel mussar la datoteca en il dossier:\n{err}',
        'not_found': 'Betg chattà',
        'not_found_msg': 'Datoteca e ordinatur betg chattads:\n\n',
        'save_report_title': 'Memorisar rapport',
        'save_report_btn': 'Memorisar rapport…',
        'filetype_text': 'Datoteca da text',
        'filetype_all': 'Tut las datotecas',
        'report_saved_title': 'Rapport memorisà',
        'report_saved_msg': 'Rapport memorisà en la datoteca:\n{path}',
        'report_save_failed': 'Impussibel memorisar il rapport:\n{err}',
        'tt_incremental': 'Vala mo per il buttun « Crear/actualisar la banca da novitads ord '
                          'ordinaturs ». Sche activà, vegn ina .db existenta actualisada: novs '
                          'datotecas vegnan agiuntadas e quellas mancantas vegnan marcadas sco « '
                          'betg sin il disc ». Las endataziuns na vegnan betg stizzadas.',
        'tt_only_existing': 'Mussa mo ils files che existan actualmain sin il disc. Sche vus avais '
                            'stizzà files manualmain, actualisai la banca da novitads '
                            '(incrementalmain).',
        'tt_sha1': 'SHA1 è la summa da controlla d’in file. Gida d’identifitgar midadas e da '
                   'chattar duplicats exacts. Fa la scansiun cleramain pli lenta.',
        'tt_recursive': 'Scannar er ils sutdossiers dal dossier tschernì.',
        'tt_help_btn': 'Avrir l’agid',
        'dialog_hint_open_file': 'Ussa s’avra la fanestra da sistem Windows per tscherner in file.',
        'dialog_hint_save_file': 'Ussa s’avra la fanestra da sistem Windows per tscherner il lieu '
                                 'da memorisar.',
        'dialog_hint_select_folder': 'Ussa s’avra la fanestra da sistem Windows per tscherner in '
                                     'ordinatur.',
        'warning_title': 'Avis',
        'warn_increment_off': 'Vus avais deactivà l’actualisaziun incrementala. La proxima '
                              'scansiun recreescha la banca da novitads da nov (vegls records '
                              'vegnan stizzads). Cuntinuar?',
        'warn_only_existing_on': 'Il filter «Be ils existents sin il disc» utilisescha novitads da '
                                 'la banca da novitads. Sche vus avais stizzà files manualmain, '
                                 'recumandain nus d’actualisar la banca da novitads '
                                 '(incrementalmain). Activar il filter?',
        'warn_sha1_on': 'Il calcul da SHA1 po ralentir cleramain la scansiun, surtut cun files '
                        'gronds e dossiers da rait/HDD. Activar SHA1?',
        'help_incremental_title': 'Actualisaziun incrementala',
        'help_incremental_text': 'Questa opziun vala mo per il buttun « Crear/actualisar la banca '
                                 'da novitads ord ordinaturs ».\n'
                                 '\n'
                                 'Uschia funcziuna quai:\n'
                                 '• sche il modus incremental è activà, dumonda il program d’avrir '
                                 'ina .db existenta per actualisar\n'
                                 '• novas datotecas vegnan agiuntadas a la banca da novitads\n'
                                 '• datotecas allontanadas dal disc restan en la banca da '
                                 'novitads, ma vegnan marcadas sco « betg sin il disc »\n'
                                 '• datotecas midada vegnan actualisadas\n'
                                 '\n'
                                 'Sche il modus incremental è deactivà, dumonda il program nua '
                                 'memorisar ina nova .db u permetta da recrear ina banca da '
                                 'novitads existenta da zero. En quel modus vegn la tabella da '
                                 'datotecas reconstruida da zero.\n'
                                 '\n'
                                 'Questa opziun na vala betg per ils buttuns « Crear/actualisar '
                                 'set » e « Mussar la banca da novitads ».',
        'help_only_existing_title': 'Be ils existents sin il disc',
        'help_only_existing_text': 'Quest filter mussa mo ils files marcads sco existents sin il '
                                   'disc en la banca da novitads.\n'
                                   '\n'
                                   'Sche vus avais stizzà in file manualmain, la banca da novitads '
                                   'mussa quai suenter in update incremental.',
        'help_status_title': 'Filter «Status»',
        'help_status_text': 'Mussa las entradas tenor status (util per sets):\n'
                            '\n'
                            '• (Tut) — senza filter\n'
                            '• Chattà — la via è associada ed il file è chattà\n'
                            '• Betg chattà — il file manca sin il disc\n'
                            '• Ambigu — pliras variantas chattadas, tscherna necessaria\n'
                            '\n'
                            'Sche (Tut) ils sets è tschernì, ils status na vegnan betg duvrads.',
        'help_sha1_title': 'Quint SHA1',
        'help_sha1_text': 'SHA1 è ina «impronta» dal cuntegn dal file (summa da controlla).\n'
                          '\n'
                          'Per tge quai serva:\n'
                          '• controllar midaments — differents SHA1 vulan dir ch’il file è sa '
                          'midà\n'
                          '• tschertgar duplicats exacts tenor cuntegn\n'
                          '\n'
                          'Dischavantatg: SHA1 vegn calculà cun leger l’entir file, uschia che la '
                          'scansiun po vegnir cleramain pli lenta.',
        'help_title': 'Agid',
        'help_update_db_text': 'Sche vus avais stizzà u spustà files sin il disc, po la banca da '
                               'novitads esser antiquada.\n'
                               '\n'
                               '• Cliccai sin «Crear banca da novitads ord dossiers» ed activai '
                               '«actualisaziun incrementala»\n'
                               '• U recreai la banca da novitads\n'
                               '\n'
                               'Suenter l’actualisaziun funcziunan la tschertga e «Mussar en il '
                               'dossier» correctamain.',
        'ok': 'Chapì',
        'yes': 'Gea',
        'no': 'Na',
        'error_title': 'Errur',
        'help_btn_build_title': 'Crear / actualisar la banca da novitads',
        'help_btn_build_text': 'Scannescha ils ordinaturs tschernids e creescha u actualisescha la '
                               'banca da novitads SQLite da datotecas.\n'
                               '\n'
                               'Andament:\n'
                               '1) tscherner in u plirs ordinaturs per scannar\n'
                               '2) sche il modus incremental è activà, avrir ina .db existenta per '
                               'actualisar\n'
                               '3) sche il modus incremental è deactivà, tscherner nua memorisar '
                               'ina nova .db u recrear ina banca da novitads existenta\n'
                               '\n'
                               'Quest buttun:\n'
                               '• agiunta novas datotecas\n'
                               '• actualisescha datotecas midadas\n'
                               '• en modus incremental marchescha datotecas allontanadas sco '
                               'mancantas sin il disc\n'
                               '• cun modus incremental deactivà reconstruescha la tabella da '
                               'datotecas da zero\n'
                               '\n'
                               'Las opziuns sura influenzeschan la sveltezza e cumplettadad da la '
                               'scansiun.',
        'help_btn_set_title': 'Crear / actualisar il set',
        'help_btn_set_text': 'Chargia ina glista da viadis ord il clipboard, TXT u Excel e la '
                             'confrunta cun la banca da novitads tschernida.\n'
                             '\n'
                             'Il resultat vegn memorisà sco set cun ils status Chattà / Betg '
                             'chattà / Ambigu.',
        'help_btn_view_title': 'Mussar la banca da novitads',
        'help_btn_view_text': 'Avra la vista da la banca da datotecas: tschertga, filters, export CSV, mussar il file en il dossier e resolver manualmain las lingias ambiguas dal set.',
        'text_files_filetype': 'Datotecas da text',
        'text_excel_filetype': 'Datotecas da text ed Excel',
        'excel_files_filetype': 'Datotecas Excel',
        'err_read_paths': 'Impussibel leger la glista da viadis:\n{err}',
        'err_open_db': 'Impussibel avrir la banca da novitads:\n{err}',
        'err_read_paths_generic': 'Impussibel leger la glista da viadis.',
        'err_open_db_generic': 'Impussibel avrir la banca da novitads.',
        'report_save_failed_generic': 'Impussibel memorisar il rapport.',
        'show_in_folder_failed_generic': 'Impussibel mussar la datoteca en il dossier.',
        'search_failed_generic': 'Impussibel exequir la tschertga.',
        'scan_failed_generic': 'La scansiun è terminada cun in’errur.',
        'set_sync_failed_generic': 'Impussibel crear u actualisar il set.',
        'resolve_need_specific_set': 'La schliaziun da l’ambiguitad funcziuna mo per in set '
                                     'tschernì (betg «(Tut)»).',
        'resolve_row_not_ambiguous': 'La lingia tschernida n’ha betg il status «Ambigu».',
        'resolve_no_service_data': 'Betg pussibel determinar las novitads da servetsch da la '
                                   'lingia tschernida.',
        'set_summary_full': 'Set: {name}\n'
                            'Elements totals: {total}\n'
                            'Chattads: {found}\n'
                            'Betg chattads: {missing}\n'
                            'Ambigus: {ambiguous}\n'
                            '\n'
                            'Pass proxims:\n'
                            '1) Avri «Mussar la banca da novitads».\n'
                            '2) Tschernais il set «{name}».\n'
                            '3) Per las lingias cun status «Ambigu», faschai dubel clic e '
                            'tschernais la datoteca correcta.',
        'set_status_updated': 'Set «{name}» actualisà: {total} elements (chattads {found})',
        'set_toast_updated': 'Set «{name}»: {total} elem., chattads {found}, ambigus {ambiguous}',
        'confirm_title': 'Conferma',
        'scan_report_summary': 'Resumaziun',
        'scan_report_folders': 'Dossiers',
        'scan_stopped_title': 'Operaziun fermada',
        'scan_stopped_msg': 'L’operaziun è vegnida fermada da l’utilisader.',
        'status_scan_stopped': 'Scansiun fermada.',
        'export_csv_running': 'Export CSV en curs…',
        'export_csv_done': 'Export CSV terminà',
        'exit_scan_running_title': 'Fanestra da l’operaziun',
        'exit_scan_running_msg': 'Ina operaziun è anc en curs. Tge vulais far?',
        'search_mode_fs': 'Datotecas ed ordinaturs',
        'search_mode_content': 'cuntegn dals documents',
        'header_mark': 'Elecziun',
        'header_source': 'Funtauna',
        'header_snippet': 'Extract',
        'item_kind_all': 'Tut ils objects',
        'item_kind_files': 'Mo datotecas',
        'item_kind_folders': 'Mo ordinaturs',
        'filter_ext': 'Ext.',
        'filter_size_from': 'Grondezza da',
        'filter_to': 'fin',
        'filter_date_from': 'Data da',
        'filter_clear': 'Reinizialisar filters',
        'btn_equalize_columns': 'Egualisar las larghezzas',
        'tt_equalize_columns': 'Fa che tut las colonnas hajan la medema ladezza.',
        'filter_ext_all': 'Tut las extensiuns',
        'tt_ext_filter_files_only': "Il filter d'extensiun è disponibel mo en il modus « Mo "
                                    'datotecas ».',
        'tt_size_filter_example': 'Per exempel: 500 KB, 10 MB, 1.5 GB. Smatga Enter',
        'calendar_btn': '...',
        'calendar_title': 'Tscherner data',
        'calendar_today': 'Oz',
        'calendar_prev_month': '←',
        'calendar_next_month': '→',
        'calendar_month_names': 'Schaner|Favrer|Mars|Avrigl|Matg|Zercladur|Fanadur|Avust|Settember|October|November|December',
        'calendar_weekday_names': 'Gli|Ma|Me|Gie|Ve|So|Du',
        'btn_mark_page': 'Marcar tut sin la pagina',
        'btn_mark_all_pages': 'Marcar tut sin tut las novitads',
        'nothing_found_title': 'Nagut chattà',
        'content_search_no_results_message': 'En il cuntegn dals documents na è vegnì chattà nagut. Sche l’indexaziun è anc en curs, pon ils resultats cumparair pli tard.',
        'tt_search_mode_content_help': 'La tschertga en il cuntegn funcziuna cun datotecas PDF, DOCX ed XLSX. Resultats cumparan mo per datotecas gia indexadas. Per tschertas PDF dependa la tschertga dal text integrà u da l’OCR.',
        'search_failed_content': 'La tschertga en il cuntegn n’è betg reussida. Emprova ina dumonda cun damain punctuaziun u controllescha sche l’indexaziun è terminada.',
        'btn_mark_all': 'Marcar tut',
        'btn_unmark_all': 'De-marcar tut',
        'btn_collect_checked': 'Ramassar ils marcads',
        'collect_files_title': 'Ramassar datotecas',
        'collect_files_choose_dir': 'Tscherner l’ordinatur da destinaziun',
        'collect_files_none_selected': 'Nagut seleziunà',
        'collect_files_result': 'Copià: {copied}\nSursiglì: {skipped}',
        'item_type_folder': 'Ordinatur',
        'item_type_file': 'Datoteca',
        'index_docs_title': 'Indexar documents',
        'index_docs_prepare': 'Preparaziun…',
        'index_mode_changed': 'Midà',
        'index_mode_all': 'Tut',
        'index_mode_errors': 'Errurs',
        'btn_index_content': 'Indexar il cuntegn dals documents',
        'help_index_content_title': 'Indexar il cuntegn dals documents',
        'help_index_content_text': 'Crea in index da tschertga dal text entaifer documents. Word, '
                                   'Excel e PDF vegnan sustegnids. Per PDFs cun text integrà da '
                                   'qualitad nauschsa po vegnir duvrà OCR, sche content_runtime è '
                                   'disponibel sper l’applicaziun. Dapli documents che vegnan '
                                   'duvrads, dapli temp dura l’operaziun.',
        'old_db_title': 'Veglia banca da novitads',
        'old_db_message': 'Questa banca da novitads è vegnida creada cun ina versiun pli veglia da '
                          'l’applicaziun e na sustegna betg las novitads novas.\n'
                          '\n'
                          'Tabellas mancantas: {tables}\n'
                          '\n'
                          'Creai ina nova banca da novitads cun la versiun actuala da l’utensil.',
        'help_index_content_body': 'Crea u actualisescha in index da tschertga per il text '
                                   'entaifer documents.\n'
                                   '\n'
                                   'Word, Excel e PDF vegnan sustegnids. Per PDFs po vegnir duvrà '
                                   'OCR sche il text integrà è da nauscha qualitad e '
                                   'content_runtime è disponibel.\n'
                                   '\n'
                                   'L’execuziun normala lavura incrementalmain: documents novs e '
                                   'midai vegnan actualisads senza reprocessar tut.',
        'index_docs_summary': 'Fatg. Processà: {processed}\nBun: {ok}\nErrurs: {errors}',
        'index_docs_nothing_to_do': "Nagina documents novs u midai per l'indexaziun èn vegnids "
                                    'chattads.',
        'save': 'Memorisar',
        'open': 'Avrir',
        'select': 'Tscherner',
        'path_dialog_title': 'Tscherner via',
        'path_dialog_location': 'Ordinatur:',
        'path_dialog_go': 'Ir',
        'path_dialog_up': 'Enavos',
        'path_dialog_name': 'Num',
        'path_dialog_type': 'Tip',
        'path_dialog_filename': 'Num da file:',
        'path_dialog_current_folder': 'Ordinatur actual:',
        'path_dialog_folder': 'Ordinatur',
        'path_dialog_file': 'Datoteca',
        'path_dialog_invalid_folder': "L'ordinatur indicà na stat betg disponibla.",
        'path_dialog_no_file_name': 'Endatescha in num da file.',
        'path_dialog_file_missing': "Il file tschernì n'exista betg.",
        'tray_restore': 'Restaurar',
        'tray_hide_icon': 'Zuppentar l’icona en la tray',
        'size_unit_b': 'B',
        'size_unit_kb': 'KB',
        'size_unit_mb': 'MB',
        'size_unit_gb': 'GB',
        'size_unit_tb': 'TB',
        'size_unit_pb': 'PB',
        'datetime_format': '%d.%m.%Y %H:%M',
        'content_source_docx': 'Word',
        'content_source_xlsx': 'Excel',
        'content_source_pdf_embedded': 'PDF (text integrà)',
        'content_source_pdf_ocr': 'PDF (OCR)',
        'content_source_pdf_mixed': 'PDF (maschadà)',
        'content_source_unknown': 'Nunenconuschent',
        'help': 'Agid',
        'unsupported_set_source_filetype': 'Mo .txt e .xlsx/.xlsm/.xltx/.xltm vegnan sustegnids',
        'quick_start_title': 'Co cumenzar',
        'quick_start_text': '1. Avri ina banca da novitads existenta u creescha ina nova.\n'
                            '2. Per l’indexaziun tscherna ina u pliras ordinaturs.\n'
                            '3. Per la tschertga en il cuntegn dovri in’indexaziun cumpletta dal '
                            'cuntegn.\n'
                            '4. Il filter per extensiun funcziuna mo en la moda «Mo datotecas».\n'
                            '5. L’ordinatur content_runtime sto sa chattar sper il program. El è necessari per OCR da datotecas PDF e per l’indexaziun cumpletta da lur cuntegn.',
        'btn_hide': 'Zuppentar',
        'btn_show': 'Mussar'}}

class I18N:
    def __init__(self):
        self.current_language = 'ru'

    def set_language(self, language):
        if language in TRANSLATIONS:
            self.current_language = language

    def t(self, key):
        return TRANSLATIONS.get(self.current_language, {}).get(key, TRANSLATIONS.get('en', {}).get(key, key))

    def get_languages(self):
        return list(TRANSLATIONS.keys())


i18n = I18N()
