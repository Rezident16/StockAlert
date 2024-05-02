from flask_socketio import Namespace
from app import socketio

class NewsNameSpace(Namespace):
    def on_connect(self):
        print("Client connected")
        self.emit('connected', {'message': 'Connected to News namespace'})  


    def on_disconnect(self):
        print("Client disconnected")
    def on_news(self, data):
        self.emit('news', data)


class StockPrice(Namespace):
    def on_price(self, data):
        self.emit('price', data)

class Patterns(Namespace):
    def on_connect(self):
        print("Client connected")
        self.emit('connected', {'message': 'Connected to Patterns namespace'})

    def on_disconnect(self):
        print("Client disconnected")
    def on_pattern(self, data):
        self.emit('pattern', data)


patterns_namespace = Patterns('/patterns')
socketio.on_namespace(patterns_namespace)

news_namespace = NewsNameSpace('/news')
socketio.on_namespace(news_namespace)
