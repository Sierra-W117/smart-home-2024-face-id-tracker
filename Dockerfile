# ========== Build Stage ==========
# Uses heavier CUDA development image Used to compile and build all dependencies (Much larger in size due to development tools)

# Базовый образ для этапа сборки
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04 AS builder

# Метаданные образа
LABEL maintainer="your-email@example.com"
LABEL version="1.0"
LABEL description="Face recognition with CUDA support"

# Настройка окружения для APT
# Отключает интерактивные диалоги при установке пакетов, чтобы автоматизировать сборку
ARG DEBIAN_FRONTEND=noninteractive

# Install system packages
RUN apt-get update && apt-get install -y \
    python3=3.10* \
    python3-pip \
    python3-dev \
    ubuntu-drivers-common \
    libopenblas-dev \
    liblapack-dev \
    cmake \
    build-essential \
    libx11-dev \
    libgl1-mesa-glx \
    git \
    libssl-dev \
    && ubuntu-drivers autoinstall \
    && rm -rf /var/lib/apt/lists/*

# Setup CUDA environment
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
ENV CUDA_HOME=/usr/local/cuda

# Install Python dependencies
RUN python3 -m pip install --upgrade pip setuptools wheel cmake

# Install dlib with CUDA support
RUN pip3 install --no-cache-dir dlib==19.24.2 \
    --global-option="--yes" \
    --global-option="DLIB_USE_CUDA"

# ========== Runtime Stage ==========
# Uses lighter CUDA runtime image Copies only compiled results from Build Stage Contains only necessary libraries to run the application No development tools or source code

FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Копируем только необходимые артефакты из builder
COPY --from=builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages
COPY --from=builder /usr/lib/python3.10 /usr/lib/python3.10
COPY --from=builder /usr/bin/python3 /usr/bin/python3

# Настройка окружения для APT
# Отключает интерактивные диалоги при установке пакетов, чтобы автоматизировать сборку
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3=3.10* \
    python3-pip \
    python3-dev \
    libopenblas0 \
    libopenblas-dev \
    liblapack3 \
    liblapack-dev \
    libx11-6 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxcb1 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    qtbase5-dev \
    libqt5gui5 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    numpy==1.24.3 \
    opencv-python==4.8.0.76 \
    face_recognition==1.3.0

# Создаем не-root пользователя
RUN useradd -m appuser
USER appuser
WORKDIR /home/appuser

# Healthcheck для проверки работоспособности
# Docker использует эту информацию для мониторинга и может автоматически перезапускать контейнер при проблемах
HEALTHCHECK --interval=30s --timeout=10s \
  CMD python3 -c "import face_recognition" || exit 1

# Копирует файл main.py из контекста сборки в текущую директорию контейнера (.)
# Сразу устанавливает правильного владельца файла (appuser) и группу (appuser)
COPY --chown=appuser:appuser main.py .

CMD ["python3", "main.py"]