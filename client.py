import socketio

sio = socketio.Client()


@sio.event
def connect():
    print('connection established')


@sio.event
def message(data):
    print('message received with ', data)
    sio.emit('my_response', {'response': 'my response'})


@sio.event
def disconnect():
    print('disconnected from server')


if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    sio.emit('my_message', {'response': 'my response'})