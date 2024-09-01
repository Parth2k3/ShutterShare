from comparato.celery import app

@app.task
def add(x, y):
    return x + y

# Then in your Django shell or script
add.delay(2, 3)

