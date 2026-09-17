FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MPLBACKEND=Agg MPLCONFIGDIR=/tmp/matplotlib OPENBLAS_NUM_THREADS=1
RUN pip install --no-cache-dir --upgrade pip==26.2.1 && pip install --no-cache-dir pandas==3.0.1 numpy==2.4.2 matplotlib==3.10.8 seaborn==0.13.2 scipy==1.17.1 openpyxl==3.1.5
COPY runner/worker.py /app/worker.py
WORKDIR /tmp
USER 65534:65534
ENTRYPOINT ["python", "-I", "/app/worker.py"]
