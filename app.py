from flask import Flask, render_template, request, redirect, url_for, flash
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Секретный ключ для работы с flash-сообщениями

# Конфигурация для загрузки файлов
# Путь к директории, где находится app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Папка uploads рядом с app.py
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # Лимит размера файла: 3 МБ

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'tgz'}


def allowed_file(filename):
    """Проверяет, разрешено ли расширение файла."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(RequestEntityTooLarge)
def handle_413(error):
    """Обработчик ошибки 413 (слишком большой файл)."""
    flash('Размер файла превышает допустимый лимит (3 МБ).', 'error')
    return redirect(url_for('upload_file'))


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        fio = request.form.get('fio', '').strip()
        file = request.files.get('file')

        # Проверка ФИО
        if not fio:
            flash('Пожалуйста, введите ФИО.', 'error')
            return redirect(request.url)

        # Проверка файла
        if not file or file.filename == '':
            flash('Пожалуйста, выберите файл.', 'error')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash(
                'Разрешены только сжатые файлы (например, .zip, .rar, .7z и другие).', 'error')
            return redirect(request.url)

        # Создание папки для сохранения файлов
        today = datetime.now().strftime('%Y-%m-%d')
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], today, fio)
        os.makedirs(save_path, exist_ok=True)

        # Сохранение файла
        filename = secure_filename(file.filename)
        file.save(os.path.join(save_path, filename))

        flash('Отправка была успешно завершена!', 'success')
        return redirect(url_for('upload_file'))

    return render_template('upload.html')


if __name__ == '__main__':
    # Убедитесь, что папка uploads существует
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=8080, debug=True)
