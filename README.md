# My laboratory work #2
https://lab2-kvqu.onrender.com

## Варіант
Шемчук Віталій ІО-13
13%3=1

Мій варіант:
Для валют - потрібно зробити окрему сутність, також для кожного користувача повинна бути валюта по замовчуванню(її можна встановити) а також при створенні витрати, можна вказувати валюту, проте не обов’язково(якщо не вказали то буде використана валюта по замовчуванню).

Для запуску у себе на пк 

Потрібно клонувати проект в свою робочу директорію:
```
git clone https://github.com/vetshem/lab2_back.git
```
Створити віртуальне середовище за допомогою venv:
```
python3 -m venv venv
```
Активувати віртуальне середовище:
```
source ./venv/bin/activate
```
Встановити flask та решту за допомогою команди:
```
pip install flask
```
```
pip install -r requirements.txt
```
Тут є .flaskenv файл, тому потрібно поставити python-dotenv:
```
pip install python-dotenv
```
Далі можна збілдити image такою командою:
```
docker build --build-arg PORT=<your port> . -t <image_name>:latest
```
Якщо image упішно збілдився, то його можна запустити і перевірити:
```
docker run -it --rm --network=host -e PORT=<your port> <image_name>:latest
```
Збілдити контейнер: 
```
docker-compose build
```
Запустити контейнер:
```
docker-compose up
```
