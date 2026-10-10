FROM python:3.12-slim
WORKDIR /app

# Line 3. Copy two_sum.py from your folder into the image.
#         Use COPY. The destination is a single dot, meaning the current
#         folder inside the image, which WORKDIR set to /app.

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY two_sum.py .

# Line 4. Record the command a container runs when it starts.
#         Use CMD with the bracket form: the program first, then the file
#         you want handed to it.

CMD ["python", "two_sum.py"]