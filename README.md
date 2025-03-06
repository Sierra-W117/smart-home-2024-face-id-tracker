# Face Recognition with CUDA Support

Реализация системы распознавания лиц с аппаратным ускорением через NVIDIA CUDA. Проект использует двухэтапную сборку Docker-образа для оптимизации размера и безопасности.

## Предварительные требования

Перед запуском проекта убедитесь, что ваша система соответствует следующим требованиям:

- **Операционная система:** Ubuntu или любая другая Linux-система, поддерживающая Docker и CUDA.
- **Docker:** Установленный и правильно настроенный Docker.
- **NVIDIA GPU:** Ваше устройство должно иметь видеокарту, поддерживающую CUDA версии **11.8** или выше.
- **NVIDIA драйверы:** Установлены драйверы NVIDIA, совместимые с CUDA 11.8.

Проверить требования можно:

```bash 
# Проверка версии CUDA
nvidia-smi

# Проверка поддержки Docker
docker run --rm hello-world
```

## Структура проекта

```bash
project-root/
├── Dockerfile      # Конфигурация многоэтапной сборки
├── main.py         # Основной скрипт приложения
├── photos/         # Директория с эталонными изображениями
│   ├── user1.jpg
│   └── user2.jpg
└── README.md
```

## Инструкция по установке и запуску

### 1. Сборка образов

```bash
# Сборка builder-образа с компиляцией dlib
docker build --target builder -t face-recognition-builder .

# Проверка поддержки CUDA
docker run -it --rm --gpus all face-recognition-builder \
  python3 -c "import dlib; print('CUDA enabled:', dlib.DLIB_USE_CUDA)"

# Сборка финального образа
docker build -t face-recognition .
```

### 2. Подготовка данных

Убедитесь, что в корневой директории проекта присутствуют все необходимые файлы, включая:
- Файл `main.py` – основной скрипт приложения.
- Фотографии или другие данные, требуемые для распознавания лиц, внутри директории `photos`.

### 3. Запуск контейнера

```bash
docker run --gpus all \
  -v $(pwd):/home/appuser \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  --device=/dev/video0:/dev/video0 \
  --group-add video \
  face-recognition
```
